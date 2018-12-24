"""
    Base class to be used for creating commands
"""
from crypto_predict.app import db


class BaseCommand(object):
    """
        Override command function for usage
    """

    def command(self, *args, **kwargs):
        raise NotImplementedError

    def run_command_with_args(self, *args):
        args = args[0]
        arguments = []
        kwargs = {}
        for arg in args:
            if arg[:2] == "--":
                kwargs[arg[2:].split("=")[0]] = arg[2:].split("=")[1]
            else:
                arguments.append(arg)
        self.command(*arguments, **kwargs)
        db.session.commit()
