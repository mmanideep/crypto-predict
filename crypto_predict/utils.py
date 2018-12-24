import datetime
import requests
import time

from crypto_predict.app import app
from crypto_predict.contracts.core import BitCoinCash, BitCoin, Ethereum, Dogecoin, LiteCoin
from crypto_predict.models.non_db_models.crypto_currency import CryptoCurrency
from crypto_predict.models.custom_exception import ValidationError


LOGGER = app.logger

crypto_contract_mapping = {
    CryptoCurrency.Bitcoin: BitCoin,
    CryptoCurrency.BitcoinCash: BitCoinCash,
    CryptoCurrency.Dogecoin: Dogecoin,
    CryptoCurrency.Litecoin: LiteCoin,
    CryptoCurrency.Ethereum: Ethereum
}


class BlockChainInfo:

    DAY_API = "https://min-api.cryptocompare.com/data/pricehistorical"
    PERIODIC_DAY_API = "https://min-api.cryptocompare.com/data/histoday"

    CURRENCY_KEY_WORD_MAP = {
        CryptoCurrency.Bitcoin: "BTC",
        CryptoCurrency.Ethereum: "ETH",
        CryptoCurrency.Litecoin: "LTC",
        CryptoCurrency.BitcoinCash: "BCH",
        CryptoCurrency.Dogecoin: "DOGE"
    }

    @classmethod
    def get_crypto_exchange_rate_on_date(cls, for_date, crypto_currency):
        if not isinstance(for_date, datetime.date):
            raise ValidationError("for_date is not of type date")
        if crypto_currency not in cls.CURRENCY_KEY_WORD_MAP.keys():
            raise ValidationError("invalid value for crypto_currency")
        timestamp = int(time.mktime(for_date.timetuple()))

        LOGGER.info("Requesting url {} for time_stamp {}".format(cls.DAY_API, str(for_date)))

        return requests.get(
            cls.DAY_API,
            params={
                "ts": timestamp,
                "tsyms": "USD",
                "fsym": cls.CURRENCY_KEY_WORD_MAP[crypto_currency]
            }
        )

    @classmethod
    def get_time_range_data(cls, to_date, crypto_currency):
        if not isinstance(to_date, datetime.date):
            raise ValidationError("from_date and to_date should be of type date")
        if crypto_currency not in cls.CURRENCY_KEY_WORD_MAP.keys():
            raise ValidationError("invalid value for crypto_currency")
        to_timestamp = int(time.mktime(to_date.timetuple()))

        LOGGER.info("Requesting url {} for time_stamp {}".format(cls.DAY_API, str(to_date)))

        return requests.get(
            cls.PERIODIC_DAY_API,
            params={
                "tsym": "USD",
                "fsym": cls.CURRENCY_KEY_WORD_MAP[crypto_currency],
                "limit": 30,
                "aggregate": 1,
                "toTs": to_timestamp
            }
        )
