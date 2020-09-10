import subprocess
import pwd
import os

class PhonyServer:
    def __init__(self, home_dir, sample_quota, mortal_group):
        self.home_dir = home_dir
        self.sample_quota = sample_quota
    
    def register(self, name, password=None):
        print("Registering %s:%s" % (name, str(password)))
    
    def kill(self, name):
        print("Killing %s" % name)

    def purge(self, name):
        print("Purging %s" % name)

    def reset(self, name, password=None):
        print("Resetting %s:%s" % (name, str(password)))

    def quota(self, name):
        print("Checking quota %s" % (name))
        quota = None
        return quota

class RegistrationError(Exception):
    def __init__(self, name, message, returncode):
        self.name = name
        self.message = message
        self.returncode = returncode

class EdquotaError(Exception):
    def __init__(self, name, sample_quota, returncode):
        self.name = name
        self.sample_quota = sample_quota
        self.returncode = returncode

class MurderError(Exception):
    def __init__(self, name, message, returncode):
        self.name = name
        self.message = message
        self.returncode = returncode

class UnknownError(Exception):
    def __init__(self, name, returncode):
        self.name = name
        self.returncode = returncode

class DeletionError(Exception):
    def __init__(self, name, returncode, path):
        self.name = name
        self.returncode = returncode
        self.path = path

class UnsafeNameError(Exception):
    def __init__(self, name):
        self.name = name

class ResetError(Exception):
    def __init__(self, name):
        self.name = name

class Server:
    def __init__(self, home_dir, sample_quota, mortal_group):
        self.home_dir = home_dir
        self.sample_quota = sample_quota
        self.mortal_group = mortal_group

    def register(self, name):
        if not name.isalnum():
            raise UnsafeNameError(name)

        user_dir = os.path.join(self.home_dir, name)

        r1 = subprocess.run(['useradd', '-m', '-d', user_dir, '-g', self.mortal_group, '-s', '/sbin/nologin', name])

        if r1.returncode:
            if r1.returncode == 9:
                raise RegistrationError(name, "User already exists", r1.returncode)
            raise UnknownError(name, r1.returncode)

        r2 = subprocess.run(['edquota', '-p', self.sample_quota, name])
        if r2.returncode:
            raise EdquotaError(name, self.sample_quota, r2.returncode)

        
    def kill(self, name):
        if not name.isalnum():
            raise UnsafeNameError(name)

        user_dir = os.path.join(self.home_dir, name)

        r1 = subprocess.run(["userdel", name])
        if r1.returncode:
            if r1.returncode == 6:
                raise MurderError(name, "User does not exist", r1.returncode)
            raise UnknownError(name, r1.returncode)

        r2 = subprocess.run(["rm", "-rf", user_dir])
        if r2.returncode:
            raise DeletionError(name, r2.returncode, user_dir)

    def purge(self, name):
        if not name.isalnum():
            raise UnsafeNameError(name)

        user_dir = os.path.join(self.home_dir, name)

        pinf = pwd.getpwnam(name)
        uid = pinf.pw_uid
        gid = pinf.pw_gid

        r1 = subprocess.run(["rm", "-rf", user_dir])
        if r1.returncode:
            raise DeletionError(name, r1.returncode, user_dir)

        os.mkdir(user_dir)
        os.chown(user_dir, uid, gid)
        os.chmod(user_dir, 0o755)

    def reset(self, name, password):
        if not name.isalnum() or not password.isalnum():
            raise UnsafeNameError(name)
        
        r1 = subprocess.run(["chpasswd"], input="%s:%s" % (name, password))
        if r1.returncode:
            raise ResetError(name)

    def quota(self, name):
        #TODO
        val = None
        return val
