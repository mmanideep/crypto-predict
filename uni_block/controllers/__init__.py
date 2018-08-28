import os
import sys
import pkgutil

from flask.views import MethodViewType, MethodView

all_my_base_classes = {}

export_api_list = []

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
        all_my_base_classes[dir_name] = dir_obj
        if type(dir_obj) == MethodViewType and dir_obj != MethodView:
            export_api_list.append(dir_obj)
