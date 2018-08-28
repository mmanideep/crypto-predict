import json
from solc import compile_source

from uni_block.app import w3


class BaseContract(object):

    _solidity_code = None
    _byte_code = None
    _abi_code = None
    __contract_address = None
    __contract_instance = None

    def __init__(self, contract_address=None):
        if self._byte_code is not None and self._abi_code is not None:
            self._abi_code = json.loads(self._abi_code)
        elif self._solidity_code is not None:
            self._compile_solidity()
        else:
            raise NotImplementedError("At least one of byte_code, abi_code or _solidity_code needs to be implemented")
        self.contract = w3.eth.contract(
            abi=self._abi_code,
            bytecode=self._byte_code)
        if not contract_address is None:
            self.__contract_address = contract_address
            self.__contract_instance = w3.eth.contract(address=self.__contract_address, abi=self.abi)

    def _compile_solidity(self):
        compiled_sol = compile_source(self._solidity_code)
        contract_interface = compiled_sol['<stdin>:' + self.__class__.__name__]
        self._byte_code = contract_interface['bin']
        self._abi_code = contract_interface['abi']

    def deploy(self, account_key, gas=3000000):
        tx_hash = self.contract.deploy(transaction={'from': account_key, 'gas': gas})
        tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
        self.__contract_address = tx_receipt['contractAddress']
        self.__contract_instance = w3.eth.contract(address=self.__contract_address, abi=self.abi)
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
            self.__contract_instance = w3.eth.contract(address=self.__contract_address, abi=self.abi)
            return self.__contract_instance
        return None

    @property
    def solidity_code(self):
        return self._solidity_code

    @property
    def abi(self):
        return self._abi_code

    @property
    def contract_address(self):
        return self.__contract_address

    @staticmethod
    def convert_to_dict(fields, values):
        response = {fields[i]: values[i] for i in range(len(fields))}
        return response
