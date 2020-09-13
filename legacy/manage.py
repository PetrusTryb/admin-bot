import serverio
import argparser
import json
import os


class Manager:
    DB_FILEPATH = 'db.json'
    SETTINGS_FILEPATH = 'settings.json'

    def __init__(self):
        self.settings = self.loadDb(self.SETTINGS_FILEPATH)
        self.db = self.loadDb(self.DB_FILEPATH)
        if len(self.db) == 0:
            self.db = []

        self.server = serverio.Server(
            self.settings['home_dir'], self.settings['sample_quota'], self.settings['mortal_group'])

    # database commands

    def saveDb(self, filename, data):
        open(filename).write(json.dumps(data))

    def loadDb(self, filename):
        if not os.path.isfile(filename):
            return {}
        return json.loads(open(filename).read())

    # serverio commands

    def info(self):
        yield(self.server.info())

    def register(self, name):
        try:
            self.server.register(name)

            self.db.append({
                'username': name,
                'home_dir': os.path.join(self.settings['home_dir'], name),
            })
            self.saveDb(self.DB_FILEPATH, self.db)

            yield(f"Successfully registered '{name}' user")

        except serverio.UnsafeNameError as e:
            yield(f"Incorrect username: {e}")
        except serverio.RegistrationError as e:
            yield(f"{e}")
        except Exception as e:
            yield(f"Unknown exception occured: {e}")

    def kill(self, name):
        try:
            self.server.kill(name)
            
            # remove from db
            for user in self.db:
                if user['name'] == name:
                    self.db.remove(user)
                    break
            self.saveDb(self.DB_FILEPATH, self.db)
            yield("User removed successfully")

        except serverio.UnsafeNameError as e:
            yield(f"Incorrect username: {e}")
        except serverio.MurderError as e:
            yield(f"{e}")
        except serverio.DeletionError as e:
            yield(f"Couldn't remove user dir: {e}")

            # remove from db anyway
            for user in self.db:
                if user['name'] == name:
                    self.db.remove(user)
                    break
            self.saveDb(self.DB_FILEPATH, self.db)
            yield("User removed")

        except Exception as e:
            yield(f"Unknown exception occured: {e}")

    def purge(self, name):
        try:
            self.server.purge(name)
            yield(f"{name}'s dir content successfully removed")
        except serverio.UnsafeNameError as e:
            yield(f"Incorrect username: {e}")
        except serverio.DeletionError as e:
            yield(f"Failed to clear user's dir content: {e}")
        except Exception as e:
            yield(f"Unknown exception occured: {e}")

    def reset(self, name, password):
        try:
            self.server.reset(name, password)
            yield(f"{name}'s password resetted successfully")
        except serverio.UnsafeNameError as e:
            yield(f"Incorrect username: {e}")
        except serverio.ResetError as e:
            yield(f"Failed to reset password: {e}")
        except Exception as e:
            yield(f"Unknown exception occured: {e}")

    def quota(self, name):
        #TODO
        try:
            yield(f"{name}'s dir size: {self.server.quota(name)}")
        except Exception as e:
            yield(f"Unknown exception occured: {e}")

    @property
    def parser(self):
        commands = [
            {
                'name': "info",
                'description': "Show server info",
                'func': self.serverInfo,
            },
            {
                'name': "register",
                'args': [
                    "username",
                ],
                'description': "Register user with specified username",
                'func': self.register,
            },
            {
                'name': "kill",
                'args': [
                    "username",
                ],
                'description': "Completely remove user from server",
                'func': self.kill,
            },
            {
                'name': "clear",
                'args': [
                    "username",
                ],
                'description': "Clear user's dir content",
                'func': self.purge,
            },
            {
                'name': "reset",
                'args': [
                    "username",
                    "password",
                ],
                'description': "Set user's password",
                'func': self.reset,
            },
            {
                'name': "quota",
                'args': [
                    "username",
                ],
                'description': "Show user's dir size",
                'func': self.quota,
            },
        ]
        return argparser.ArgParser("manage.py", commands)


if __name__ == "__main__":
    Manager().parser.parseArgs()
