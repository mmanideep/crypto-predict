import os
import pkgutil
import sys

from crypto_predict.models.base import BaseModel

pkg_dir = os.path.dirname(__file__)

export_models = []

for (module_loader, name, ispkg) in pkgutil.iter_modules([pkg_dir]):

    exec('from ' + __name__ + '.' + name + ' import *')
    pkg_name = __name__ + '.' + name
    obj = sys.modules[pkg_name]

    for dir_name in dir(obj):
        if dir_name.startswith('_'):
            continue
        dir_obj = getattr(obj, dir_name)

        if hasattr(dir_obj, "__bases__") and hasattr(dir_obj, '__tablename__') and BaseModel in dir_obj.__bases__:
            export_models.append(dir_obj)
