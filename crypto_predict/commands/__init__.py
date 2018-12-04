import os
import re
import sys
import pkgutil

from crypto_predict.commands.base import BaseCommand


export_command_dict = {}

pkg_dir = os.path.dirname(__file__)

for (module_loader, name, ispkg) in pkgutil.iter_modules([pkg_dir]):

    # executes python code for importing modules
    exec('import ' + __name__ + '.' + name)

    pkg_name = __name__ + '.' + name
    obj = sys.modules[pkg_name]

    for dir_name in dir(obj):
        if dir_name.startswith('_'):
            continue
        dir_obj = getattr(obj, dir_name)
        if hasattr(dir_obj, "__base__") and dir_obj != BaseCommand and dir_obj.__base__ == BaseCommand:
            export_command_dict[
                re.sub('([A-Z]+)', r'_\1',dir_obj.__name__).lower()[1:]
            ] = getattr(dir_obj(), "run_command_with_args")
