from crypto_predict.contracts.base import BaseContract


class BitCoin(BaseContract):
    _solidity_file = "solidity_code.sol"
    _contract_name = "BitCoin"


class BitCoinCash(BaseContract):
    _solidity_file = "solidity_code.sol"
    _contract_name = "BitCoinCash"


class Ethereum(BaseContract):
    _solidity_file = "solidity_code.sol"
    _contract_name = "Ethereum"


class Dogecoin(BaseContract):
    _solidity_file = "solidity_code.sol"
    _contract_name = "Dogecoin"


class LiteCoin(BaseContract):
    _solidity_file = "solidity_code.sol"
    _contract_name = "LiteCoin"

