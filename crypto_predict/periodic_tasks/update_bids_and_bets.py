import datetime

from crypto_predict.app import app, w3
from crypto_predict.contracts.core import BitCoinCash, BitCoin, Dogecoin, Ethereum, LiteCoin
from crypto_predict.models.non_db_models.crypto_currency import CryptoCurrency
from crypto_predict.models.bidding import UserBidModel, BetModel
from crypto_predict.periodic_tasks.base import BaseTask
from crypto_predict.utils import BlockChainInfo

LOGGER = app.logger


class FetchUpdateBids(BaseTask):
    """

    """

    # Runs once in a day
    MINUTES = 60*24

    PAUSE = True

    def _create_bets(self):
        admin_account = app.config['ADMIN_ETH_ACCOUNT']
        admin_pswd = app.config['ADMIN_ETH_PASSWORD']
        w3.personal.unlockAccount(admin_account, admin_pswd)

        for_date = datetime.datetime.utcnow().date() + datetime.timedelta(days=2)

        bitcoin_bets = BetModel.query.filter_by(
            currency=CryptoCurrency.Bitcoin,
            is_open=True,
            for_date=for_date
        ).first()

        if bitcoin_bets is None:
            bitcoin = BitCoin()
            bitcoin.deploy(admin_account)
            BetModel(
                currency=CryptoCurrency.Bitcoin,
                bet_contract_address=bitcoin.contract_address,
                is_open=True,
                for_date=for_date
            ).save()
            LOGGER.info("Created bitcoin_bet")

        bitcoin_cash_bets = BetModel.query.filter_by(
            currency=CryptoCurrency.BitcoinCash,
            is_open=True,
            for_date=for_date
        ).first()

        if bitcoin_cash_bets is None:
            bitcoin_cash = BitCoinCash()
            bitcoin_cash.deploy(admin_account)
            BetModel(
                currency=CryptoCurrency.BitcoinCash,
                bet_contract_address=bitcoin_cash.contract_address,
                is_open=True,
                for_date=for_date
            ).save()
            LOGGER.info("Created bitcoin_cash_bets")

        dogecoin_bets = BetModel.query.filter_by(
            currency=CryptoCurrency.Dogecoin,
            is_open=True,
            for_date=for_date
        ).first()

        if dogecoin_bets is None:
            dogecoin = Dogecoin()
            dogecoin.deploy(admin_account)
            BetModel(
                currency=CryptoCurrency.Dogecoin,
                bet_contract_address=dogecoin.contract_address,
                is_open=True,
                for_date=for_date
            ).save()
            LOGGER.info("Created dogecoin_bets")

        litecoin_bets = BetModel.query.filter_by(
            currency=CryptoCurrency.Litecoin,
            is_open=True,
            for_date=for_date
        ).first()

        if litecoin_bets is None:
            litecoin = LiteCoin()
            litecoin.deploy(admin_account)
            BetModel(
                currency=CryptoCurrency.Litecoin,
                bet_contract_address=litecoin.contract_address,
                is_open=True,
                for_date=for_date
            ).save()
            LOGGER.info("Created litecoin_bets")

        ethereum_bets = BetModel.query.filter_by(
            currency=CryptoCurrency.Ethereum,
            is_open=True,
            for_date=for_date
        ).first()

        if ethereum_bets is None:
            ethereum = Ethereum()
            ethereum.deploy(admin_account)
            BetModel(
                currency=CryptoCurrency.Ethereum,
                bet_contract_address=ethereum.contract_address,
                is_open=True,
                for_date=for_date
            ).save()
            LOGGER.info("Created ethereum_bets")

    def task(self):

        admin_account = app.config['ADMIN_ETH_ACCOUNT']
        admin_pswd = app.config['ADMIN_ETH_PASSWORD']
        w3.personal.unlockAccount(admin_account, admin_pswd)
        LOGGER.info("Unlocked admin account")

        bet_date = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)

        all_open_bets = BetModel.query.filter_by(is_open=True, for_date=bet_date).all()

        if len(all_open_bets) == 0:
            LOGGER.warning("Found zero open bets for date {}".format(str(bet_date)))

        for open_bet in all_open_bets:
            all_user_bids = UserBidModel.query.filter_by(bet_id=open_bet.id).all()

            response = BlockChainInfo.get_crypto_exchange_rate_on_date(open_bet.for_date, open_bet.currency)
            closing_exchange_rate = response.json()[BlockChainInfo.CURRENCY_KEY_WORD_MAP[open_bet.currency]]['USD']

            LOGGER.info("{} closing exchange rate for date {} is {}".format(
                open_bet.currency, str(open_bet.for_date), closing_exchange_rate))

            winners_block_chain_accounts = []

            for user_bid in all_user_bids:
                if user_bid.min_estimate_value <= closing_exchange_rate <= user_bid.max_estimate_value:
                    winners_block_chain_accounts.append(user_bid.user.blockchain_account_key)
                    user_bid.update(status=UserBidModel.WON)
                else:
                    user_bid.update(status=UserBidModel.LOST)

            if len(winners_block_chain_accounts) > 0:
                tx_hash = open_bet.crypto_contract.functions.add_winners(
                            winners_block_chain_accounts
                        ).transact({"from": admin_account})
                w3.eth.waitForTransactionReceipt(tx_hash)
                LOGGER.info("Added {} winners and closing the bet with id {}".format(
                    str(len(winners_block_chain_accounts)), open_bet.id))

            open_bet.update(is_open=False)

        self._create_bets()

        w3.personal.lockAccount(admin_account)
        LOGGER.info("Locked admin account")
