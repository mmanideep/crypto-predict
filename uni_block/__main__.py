import os
import sys

from flask.cli import shell_command
from uni_block.app import app

if __name__ == '__main__':
    os.environ["PYTHONPATH"] = os.getcwd()
    # Todo modify the module name from 'app' to your custom module name
    os.environ["FLASK_APP"] = "base_app/app.py"
    try:
        arg = sys.argv.pop(1)
    except IndexError:
        arg = ""
    if arg == "shell":
        shell_command()
    else:
        app.run(host="0.0.0.0", threaded=True, port=8000, debug=True)
