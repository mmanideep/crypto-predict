import os
import sys
import pkgutil


from crypto_predict.periodic_tasks.base import BaseTask

pkg_dir = os.path.dirname(__file__)

periodic_tasks = []


for (module_loader, name, ispkg) in pkgutil.iter_modules([pkg_dir]):

    # executes python code for importing modules
    exec('import ' + __name__ + '.' + name)

    pkg_name = __name__ + '.' + name
    obj = sys.modules[pkg_name]

    for dir_name in dir(obj):
        if dir_name.startswith('_'):
            continue
        dir_obj = getattr(obj, dir_name)
        if hasattr(dir_obj, "__bases__") and BaseTask in dir_obj.__bases__:
            periodic_tasks.append(dir_obj)
