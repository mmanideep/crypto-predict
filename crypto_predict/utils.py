from crypto_predict.app import app
from crypto_predict.contracts.core import BitCoinCash, BitCoin, Ethereum, Ripple, LiteCoin
from crypto_predict.models.non_db_models.crypto_currency import CryptoCurrency


crypto_contract_mapping = {
    CryptoCurrency.Bitcoin: BitCoin(app.config["BITCOIN_ADDRESS"]),
    CryptoCurrency.BitcoinCash: BitCoinCash(app.config["BITCOIN_CASH_ADDRESS"]),
    CryptoCurrency.Ripple: Ripple(app.config["ETHEREUM_ADDRESS"]),
    CryptoCurrency.Litecoin: LiteCoin(app.config["LITECOIN_ADDRESS"]),
    CryptoCurrency.Ethereum: Ethereum(app.config["RIPPLE_ADDRESS"])
}
