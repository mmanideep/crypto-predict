import datetime

import requests

from crypto_predict.app import db, app, w3
from crypto_predict.contracts.core import BitCoin, BitCoinCash, Dogecoin, Ethereum, LiteCoin
from crypto_predict.commands.base import BaseCommand
from crypto_predict.models.user import UserModel
from crypto_predict.models.bidding import UserBidModel, BetModel
from crypto_predict.models.non_db_models.crypto_currency import CryptoCurrency


class CreateFakeData(BaseCommand):

    DATA = {
        "users": [
            {
                "user_name": "rick.sanchez",
                "first_name": "Rick",
                "last_name": "S",
                "email": "rick.sanchez@yahoo.com",
                "phone": "9876543210",
                "password": "rick1234",
                "eth_password": "rick1234",
                "image_url": ""
            },
            {
                "user_name": "morty.sanchez",
                "first_name": "Morty",
                "last_name": "S",
                "email": "morty.sanchez@yahoo.com",
                "phone": "91232456780",
                "password": "morty1234",
                "eth_password": "morty1234",
                "image_url": ""
            }
        ]
    }

    def _create_bets(self):
        admin_account = app.config['ADMIN_ETH_ACCOUNT']
        admin_pswd = app.config['ADMIN_ETH_PASSWORD']
        w3.personal.unlockAccount(admin_account, admin_pswd)

        for_date = datetime.datetime.utcnow().date().today() + datetime.timedelta(days=2)

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
            print("Created bitcoin_bet")

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
            print("Created bitcoin_cash_bets")

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
            print("Created dogecoin_bets")

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
            print("Created litecoin_bets")

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
            print("Created ethereum_bets")
        db.session.commit()

    def command(self, *args, **kwargs):

        remove_db = str(input("Remove db:\n"))
        if remove_db in ["Y", "y"]:
            UserBidModel.query.delete()
            UserModel.query.delete()
            BetModel.query.delete()
            db.session.commit()

        self._create_bets()

        for user in CreateFakeData.DATA["users"]:
            response = requests.post("http://127.0.0.1:8000/register", json=user)

            if response.status_code != 200:
                print(response.json())
                raise Exception("Registration Failed")

            response = requests.post(
                "http://127.0.0.1:8000/auth",
                json={"username": user["user_name"], "password": user["password"]}
            )
            if response.status_code != 200:
                print(response.json())
                raise Exception("Login Failed")
            auth_token = response.json()["access_token"]

            min_bid = float(input("Minimum Bid for Ethereum: "))
            max_bid = float(input("Maximum Bid for Ethereum: "))

            headers = {"eth-password": user["eth_password"], "authorization": "JWT {}".format(auth_token)}

            bid_date = datetime.datetime.utcnow().date() + datetime.timedelta(days=2)

            response = requests.post("http://localhost:8000/bid", json={
                "crypto_currency": CryptoCurrency.Ethereum,
                "min_estimate_value": min_bid,
                "max_estimate_value": max_bid,
                "for_date": bid_date.strftime("%Y-%m-%d")
            }, headers=headers)

            if not response.status_code == 200:
                print(response.json())
                raise Exception("Failed to place bid")
            print(response.json())
