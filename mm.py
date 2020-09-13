import subprocess
import os
import pwd
import pymysql
import logging
import string
import random
import re
import math

class UserAPI:
    def __init__(self, base_dir, user_group, samplequota):
        self.base_dir = base_dir
        self.user_group = user_group
        self.samplequota = samplequota

    def create_user(self, name):
        home_dir = os.path.join(self.base_dir, name)
        content_dir = os.path.join(home_dir, 'content')

        if os.path.exists(home_dir):
            raise FileExistsError(home_dir)

        subprocess.run(['useradd', '-m', '-b', self.base_dir, '-g', self.user_group, '-s', '/sbin/nologin', name], check=True)
        
        os.chown(home_dir, 0, 0)
        os.chmod(home_dir, 0o755)

        upwd = pwd.getpwnam(name)
        os.mkdir(content_dir)
        os.chown(content_dir, upwd.pw_uid, upwd.pw_gid)

        if self.samplequota:
            subprocess.run(['edquota', '-p', self.samplequota, name], check=True)

    def remove_user(self, name):
        subprocess.run(['userdel', '-rf', name], check=True)

    def set_password(self, name, password):
        subprocess.run(['chpasswd'], input=('%s:%s' % (name, password)).encode(), check=True)

class MariaDBApi:
    def __init__(self, host='127.0.0.1', sock='/var/run/mysqld/mysqld.sock'):
        self.host = host
        self.sock = sock

    def create_user(self, name):
        conn = pymysql.connect(user='root', host=self.host, unix_socket=self.sock)

        dbname = "db%s" % name

        try:
            with conn.cursor() as cur:
                cur.execute("CREATE USER '%s'@'%s';" % (name, self.host))
                cur.execute("CREATE DATABASE %s;" % dbname)
                cur.execute("GRANT ALL PRIVILEGES ON %s.* TO %s@%s;" % (dbname, name, self.host))
            conn.commit()
        except:
            raise
        finally:
            conn.close()


    def remove_user(self, name):
        conn = pymysql.connect(user='root', host=self.host, unix_socket=self.sock)

        dbname = "db%s" % name

        ex = None

        with conn.cursor() as cur:
            try:
                cur.execute("DROP USER '%s'@'%s';" % (name, self.host))
                conn.commit()
            except pymysql.err.OperationalError as e:
                ex = e
            
            try:
                cur.execute("DROP DATABASE %s;" % dbname)
                conn.commit()
            except pymysql.err.OperationalError as e:
                ex = e
            
        conn.close()

        if ex:
            raise ex


    def set_password(self, name, password):
        conn = pymysql.connect(user='root', host=self.host, unix_socket=self.sock)

        try:
            with conn.cursor() as cur:
                cur.execute("ALTER USER '%s'@'%s' IDENTIFIED BY '%s'" % (name, self.host, password))
                conn.commit()
        except:
            raise
        finally:
            conn.close()

class UnsafeNameError(Exception):
    def __init__(self, name):
        self.name = name

class MortalManager:
    def __init__(self, userapi, mortals=None, dbapi=None, name_digits=3):
        if mortals:
            self.mortals = set(mortals)
        else:
            self.mortals = set()

        if dbapi:
            self.dbapi = dbapi
        else:
            self.dbapi = MariaDBApi()

        self.name_digits = name_digits
        self.userapi = userapi
        logging.info("Created Mortal Manager.")

    #auxiliary methods
    def get_free_name(self):
        for i in range(1, int(math.pow(10,self.name_digits))):
            name = "s%d" % i
            if name not in self.mortals:
                return name
        
    def is_name_safe(self, name):
        if re.match('^(s\\d{1,%d})$' % self.name_digits, name):
            return True
    
    def generate_password(self, length=12):
        return "".join(random.choices(string.ascii_letters+string.digits, k=length))


    #management methods
    def create_mortal(self):
        name = self.get_free_name()
        logging.info("Creating mortal %s" % name)
        self.remove_mortal(name)

        try:
            self.userapi.create_user(name)
            self.dbapi.create_user(name)
        except Exception as e:
            logging.error("Mortal creation error: "+str(e))
            self.remove_mortal(name)
            return
        
        self.mortals.add(name)
        return name

    def remove_mortal(self, name):
        if not self.is_name_safe(name):
            raise UnsafeNameError(name)

        logging.info("Attempting to raze %s's earthly possessions." % name)
        if name in self.mortals:
            self.mortals.remove(name)

        try:
            self.userapi.remove_user(name)
        except:
            pass
        try:
            self.dbapi.remove_user(name)
        except:
            pass

    def password_reset(self, name):
        if not self.is_name_safe(name):
            raise UnsafeNameError(name)

        dbpass = self.generate_password()
        userpass = self.generate_password()
        
        self.userapi.set_password(name, userpass)
        self.dbapi.set_password(name, dbpass)

        return userpass, dbpass


    #config methods
    @staticmethod
    def from_save(config):
        dbapi = MariaDBApi(config["dbapi"]['host'], config["dbapi"]['sock'])
        userapi = UserAPI(config["userapi"]["base_dir"], config["userapi"]["user_group"], config["userapi"]["samplequota"])

        return MortalManager(userapi, mortals=config['mortals'], dbapi=dbapi)

    def dump_save(self):
        config = {
            'mortals': list(self.mortals),
            'dbapi': {
                'sock': self.dbapi.sock,
                'host': self.dbapi.host
            },
            'userapi': {
                'base_dir': self.userapi.base_dir,
                'user_group': self.userapi.user_group,
                'samplequota': self.userapi.samplequota
            }
        }
        return config



#TESTING
import argparse
import sys
import json

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manages mortals')
    parser.add_argument('--conf', default='conf.json')
    subparsers = parser.add_subparsers()

    parser_create = subparsers.add_parser('create', help='creates user')
    parser_create.set_defaults(op='create')

    parser_remove = subparsers.add_parser('remove', help='removes user')
    parser_remove.add_argument('names', action="extend", nargs="+", type=str)
    parser_remove.set_defaults(op='remove')

    parser_chpass = subparsers.add_parser('chpass', help='changes password')
    parser_chpass.add_argument('names', action="extend", nargs="+", type=str)
    parser_chpass.set_defaults(op='chpass')

    args = parser.parse_args(sys.argv[1:])
    print(args)
    if os.path.isfile(args.conf):
        with open(args.conf, 'r') as conffile:
            mm = MortalManager.from_save(json.load(conffile))
    else:
        mm = MortalManager(UserAPI('/smietnik', 'smiertelnicy', 'samplequota'))
    
    if args.op == 'create':
        print(mm.create_mortal())
    elif args.op == 'remove':
        for name in args.names:
            mm.remove_mortal(name)
    elif args.op == 'chpass':
        for name in args.names:
            print(mm.password_reset(name))

    with open(args.conf, 'w') as conffile:
        json.dump(mm.dump_save(), conffile)
