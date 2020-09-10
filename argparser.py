import sys

"""
Commands are created as array of objects, example:
commands = [
    {'name': "adduser",
     'args': [
         'username',
     ],
     'description': "Add new user with specified username",
     'func': createUser,
     }
]

Command objects *have to* have 'name', 'description' and 'func' property,
if command takes no arguments then 'args' can be ommited.
"""


class ArgParser:
    def __init__(self, appname, commands):
        self.appname = appname
        self.commands = commands

    def help(self):
        print(
            f"Type '{self.appname} help <subcommand>' for help on a specific subcommand.")
        print()
        print("Available subcommands:")

        for command in self.commands:
            print(command['name'])

    def helpCommand(self, name):
        # print command usage and description
        for command in self.commands:
            if command['name'] == name:
                print(f"Usage: '{self.appname} {command['name']}", end="")
                if 'args' in command:
                    for arg in command['args']:
                        print(f" <{arg}>", end="")
                print("'")

                print(command['description'])
                return
        noCommand(name)

    def noCommand(self, name):
        print(f"Unknown command: '{name}'")
        print(f"Type '{self.appname} help' for usage.")

    def parseArgs(self):
        if len(sys.argv) < 2:
            self.help()
            return

        # special case
        if sys.argv[1] == 'help':
            if len(sys.argv) == 3:
                self.helpCommand(sys.argv[2])
                return
            self.help()
            return

        for command in self.commands:
            if command['name'] == sys.argv[1]:
                
                if 'args' in command.keys():
                    if len(command['args']) != len(sys.argv) - 2:
                        # wrong positional args number
                        print("Wrong positional arguments number.")
                        self.helpCommand(sys.argv[1])
                        return
                else:
                    if len(sys.argv) != 2:
                        # wrong positional args number
                        print("Wrong positional arguments number.")
                        self.helpCommand(sys.argv[1])
                        return

                command['func'](*sys.argv[2:])
                return
        self.noCommand(sys.argv[1])
