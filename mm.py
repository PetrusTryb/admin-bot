import subprocess
import os
import pwd
import pymysql
import logging
import string
import random
import re
import math

class PasswordGenerator:
    def __init__(self, wordlist, extra_chars='123456789', word_count=(4,5), extra_chars_count=(5,8), uppercase_prob=0.1, force_length=None):
        self.wordlist = wordlist
        if word_count:
            self.word_count = word_count

        if extra_chars:
            self.extra_chars = extra_chars

        if extra_chars_count:
            self.extra_chars_count = extra_chars_count

        self.uppercase_prob = uppercase_prob
        self.force_length = force_length

    def generate(self):
        words = random.choices(self.wordlist, k=random.randint(*self.word_count))
        pass_chars = list("".join(words))

        if self.force_length:
            pass_chars = pass_chars[:self.force_length]

        for _ in range(random.randint(*self.extra_chars_count)):
            pass_chars[random.randint(0, len(pass_chars)-1)] = random.choice(self.extra_chars)

        pass_chars = list(map(lambda x: x.upper() if random.random() < self.uppercase_prob else x, pass_chars))


        return "".join(pass_chars)


    @staticmethod
    def filter_words(wordlist, length=(4,6)):
        word_filter = re.compile('^[a-zA-Z]{%d,%d}$' % length)
        return filter(lambda x: word_filter.match(x), wordlist)

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
                cur.execute("CREATE USER '%s'@'%%' REQUIRE SSL;" % (name))
                cur.execute("CREATE USER '%s'@'%s';" % (name, self.host))
                cur.execute("CREATE DATABASE %s;" % dbname)
                cur.execute("GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%s';" % (dbname, name, self.host))
                cur.execute("GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%%';" % (dbname, name))
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
                cur.execute("DROP USER '%s'@'%%';" % (name))
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
                cur.execute("ALTER USER '%s'@'%%' IDENTIFIED BY '%s'" % (name, password))
                conn.commit()
        except:
            raise
        finally:
            conn.close()

class PHPPoolApi:
    def __init__(self, confdir, template, service):
        self.confdir = confdir
        self.template = template
        self.service = service

    def create_user(self, name):
        confpath = os.path.join(self.confdir, "%s.conf" % name)
        with open(confpath, "w") as conffile:
            conffile.write(self.template.format(name))

    def remove_user(self, name):
        confpath = os.path.join(self.confdir, "%s.conf" % name)
        os.remove(confpath)

    def restart(self):
        subprocess.run(['systemctl', 'restart', self.service], check=True)


class UnsafeNameError(Exception):
    def __init__(self, name):
        self.name = name

class MortalManager:
    def __init__(self, userapi, phpapi, passgen, mortals=None, dbapi=None, name_digits=3):
        if mortals:
            self.mortals = set(mortals)
        else:
            self.mortals = set()

        if dbapi:
            self.dbapi = dbapi
        else:
            self.dbapi = MariaDBApi()

        self.name_digits = name_digits
        self.phpapi = phpapi
        self.phpapi.restart()
        self.userapi = userapi
        self.passgen = passgen
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

    #management methods
    def create_mortal(self):
        name = self.get_free_name()
        logging.info("Creating mortal %s" % name)
        self.remove_mortal(name)

        try:
            self.userapi.create_user(name)
            self.dbapi.create_user(name)
            self.phpapi.create_user(name)
            self.phpapi.restart()
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
        try:
            self.phpapi.remove_user(name)
        except:
            pass

    def password_reset(self, name):
        if not self.is_name_safe(name):
            raise UnsafeNameError(name)

        dbpass = self.passgen.generate()
        userpass = self.passgen.generate()
        
        self.userapi.set_password(name, userpass)
        self.dbapi.set_password(name, dbpass)

        return userpass, dbpass


    #config methods
    @staticmethod
    def from_save(config, db):
        dbapi = MariaDBApi(config["dbapi"]['host'], config["dbapi"]['sock'])
        userapi = UserAPI(config["userapi"]["base_dir"], config["userapi"]["user_group"], config["userapi"]["samplequota"])
        phpapi = PHPPoolApi(config["phpapi"]["conf_dir"], config["phpapi"]["template"], config["phpapi"]["service"])

        with open(config["passgen"]["wordsfile"], "r") as wordsfile:
            wordlist = list(PasswordGenerator.filter_words(wordsfile.read().split('\n')))

        wordlist = list(PasswordGenerator.filter_words(wordlist, tuple(config["passgen"]["word_length"])))

        passgen = PasswordGenerator(
        wordlist, 
        extra_chars = config["passgen"]["extra_chars"],
        word_count = tuple(config["passgen"]["word_count"]),
        extra_chars_count = tuple(config["passgen"]["extra_chars_count"]),
        uppercase_prob = float(config["passgen"]["uppercase_prob"]),
        force_length = int(config["passgen"]["force_length"])
        )

        return MortalManager(userapi, phpapi, passgen, mortals=db['mortals'], dbapi=dbapi)

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
