import os
import sys
import pkgutil
import multiprocessing


from crypto_predict.contracts.base import BaseContract

pkg_dir = os.path.dirname(__file__)

processes = []


def compile_solidity_class(contract_class):
    """
        Function to compile solidity code and initiate class variables
    """
    contract_class()


for (module_loader, name, ispkg) in pkgutil.iter_modules([pkg_dir]):

    # executes python code for importing modules
    exec('import ' + __name__ + '.' + name)

    pkg_name = __name__ + '.' + name
    obj = sys.modules[pkg_name]

    for dir_name in dir(obj):
        if dir_name.startswith('_'):
            continue
        dir_obj = getattr(obj, dir_name)
        if hasattr(dir_obj, "__bases__") and BaseContract in dir_obj.__bases__:
            processes.append(multiprocessing.Process(target=compile_solidity_class(dir_obj)))

[process.start() for process in processes]
[process.join() for process in processes]
