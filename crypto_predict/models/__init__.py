import os

import pkgutil


pkg_dir = os.path.dirname(__file__)

for (module_loader, name, ispkg) in pkgutil.iter_modules([pkg_dir]):

    exec('from ' + __name__ + '.' + name + ' import *')

