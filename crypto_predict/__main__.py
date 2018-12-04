import os
import sys

from flask.cli import shell_command

from crypto_predict.commands import export_command_dict
from crypto_predict.app import app

if __name__ == '__main__':
    os.environ["PYTHONPATH"] = os.getcwd()
    os.environ["FLASK_APP"] = "crypto_predict/app.py"
    try:
        ARG = sys.argv.pop(1)
    except IndexError:
        ARG = ""
    if ARG == "shell":
        shell_command()
    elif ARG == "":
        app.run(host="0.0.0.0", threaded=True, port=8000, debug=app.config.get("DEBUG"))
    else:
        try:
            with app.app_context():
                export_command_dict[ARG](sys.argv[1:])
        except KeyError:
            raise Exception("Command not found")
