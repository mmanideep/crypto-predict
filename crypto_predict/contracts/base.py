import json
import os
from solc import compile_source, compile_files

from crypto_predict.app import w3

import logging


logger = logging.getLogger(__name__)


class BaseContract(object):
    """
        While using this class either (byte_code, abi_code) or (solidity_file, contract_name) or solidity_code
        should be present
    """

    _solidity_code = None

    _byte_code = None
    _abi_code = None

    _solidity_file = None
    _contract_name = None

    def __init__(self, contract_address=None):
        klass = self.__class__
        klass._init_class()
        self.contract = w3.eth.contract(
            abi=klass._abi_code,
            bytecode=klass._byte_code)
        if contract_address is not None:
            self.__contract_address = contract_address
            self.__contract_instance = w3.eth.contract(address=self.__contract_address, abi=klass._abi_code)

    @classmethod
    def _init_class(cls):
        if cls._byte_code is not None and cls._abi_code is not None:
            if isinstance(cls._abi_code, str):
                cls._abi_code = json.loads(cls._abi_code)
        elif cls._solidity_code is not None:
            cls._compile_solidity_code()
        elif cls._solidity_file is not None:
            cls._compile_solidity_file()
        else:
            raise NotImplementedError("""
                At least one of either (byte_code, abi_code) or (solidity_file, contract_name) or
                solidity_code needs to be implemented
            """)

    @classmethod
    def _compile_solidity_file(cls):
        logger.info("Compiling solidity code from solidity file of " + cls.__name__)
        if not cls._contract_name:
            cls._contract_name = cls.__class__.__name__
        file_path = os.path.join(os.getcwd(), cls._solidity_file)
        # Windows dev uncomment below line
        # file_path = cls._solidity_file
        compiled_solidity = compile_files([file_path])
        cls._abi_code = compiled_solidity[file_path + ":" + cls._contract_name]["abi"]
        cls._byte_code = compiled_solidity[file_path + ":" + cls._contract_name]["bin"]

    @classmethod
    def _compile_solidity_code(cls):
        logger.info("Compiling solidity code of " + cls.__name__)
        compiled_sol = compile_source(cls._solidity_code)
        contract_interface = compiled_sol['<stdin>:' + cls.__name__]
        cls._byte_code = contract_interface['bin']
        cls._abi_code = contract_interface['abi']

    def deploy(self, account_key, gas=3000000):
        tx_hash = self.contract.deploy(transaction={'from': account_key, 'gas': gas})
        tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
        self.__contract_address = tx_receipt['contractAddress']
        self.__contract_instance = w3.eth.contract(address=self.__contract_address, abi=self.__class__._abi_code)
        return tx_receipt

    def __getattr__(self, item):
        if self.__contract_instance is not None:
            return getattr(self.__contract_instance, item)
        else:
            raise AttributeError("'"+self.__class__.__name__+"' object has no attribute '"+item+"'")

    @property
    def contract_instance(self):
        if self.__contract_instance is not None:
            return self.__contract_instance
        if self.__contract_address is not None:
            self.__contract_instance = w3.eth.contract(address=self.__contract_address, abi=self.__class__._abi_code)
            return self.__contract_instance
        return None

    @property
    def contract_address(self):
        return self.__contract_address
