import configparser

from crypto_predict.app import w3, app
from crypto_predict.contracts.core import BitCoin, BitCoinCash, Ripple, Ethereum, LiteCoin
from crypto_predict.commands.base import BaseCommand


class DeployContracts(BaseCommand):

    def __export_config_variables(
            self, bitcoin_address, bitcoin_cash_address, ethereum_address, litecoin_address, ripple_address):
        config = configparser.ConfigParser()
        config.read("crypto_predict/config.ini")
        config["DEFAULT"]["bitcoin_address"] = bitcoin_address
        config["DEFAULT"]["bitcoin_cash_address"] = bitcoin_cash_address
        config["DEFAULT"]["ethereum_address"] = ethereum_address
        config["DEFAULT"]["litecoin_address"] = litecoin_address
        config["DEFAULT"]["ripple_address"] = ripple_address

        with open("crypto_predict/config.ini", "w") as config_file:
            config.write(config_file)

    def command(self, *args, **kwargs):
        admin_account = app.config['ADMIN_ETH_ACCOUNT']
        admin_pswd = app.config['ADMIN_ETH_PASSWORD']
        w3.personal.unlockAccount(admin_account, admin_pswd)
        bitcoin = BitCoin()
        bitcoin.deploy(admin_account)
        bitcoin_cash = BitCoinCash()
        bitcoin_cash.deploy(admin_account)
        ripple = Ripple()
        ripple.deploy(admin_account)
        litecoin = LiteCoin()
        litecoin.deploy(admin_account)
        ethereum = Ethereum()
        ethereum.deploy(admin_account)

        self.__export_config_variables(
            bitcoin.contract_address, bitcoin_cash.contract_address,
            ethereum.contract_address, litecoin.contract_address, ripple.contract_address)
