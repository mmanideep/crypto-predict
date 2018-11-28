import copy

from flask import request, jsonify

from crypto_predict.app import app, w3
from crypto_predict.controllers.base import UnAuthenticatedBaseAPI, mandatory_fields_check
from crypto_predict.models.custom_exception import ValidationError
from crypto_predict.models.user import UserModel


class RegisterAPI(UnAuthenticatedBaseAPI):

    MANDATORY_FIELDS = [
        "user_name", "first_name", "last_name", "email", "phone", "password", "eth_password", "image_url"
    ]

    def _create_user_account(self, eth_password):
        try:
            account_address = w3.personal.newAccount(eth_password)

            w3.personal.unlockAccount(
                app.config["ADMIN_ETH_ACCOUNT"],
                app.config["ADMIN_ETH_PASSWORD"]
            )

            w3.eth.sendTransaction(
                {
                    'to': account_address,
                    'from': app.config.get('ADMIN_ETH_ACCOUNT'),
                    'value': app.config['INITIAL_BALANCE']
                }
            )

            w3.personal.unlockAccount(account_address, eth_password)

            return account_address

        except ValueError as e:
            raise ValidationError(str(e))

    @mandatory_fields_check(MANDATORY_FIELDS)
    def post(self):
        user_data = copy.deepcopy(request.json)
        eth_password = user_data.pop("eth_password")

        try:
            user = UserModel(**user_data)
            user.save()
            account = self._create_user_account(eth_password)
        except ValidationError as e:
            return jsonify({"payload": {}, "message": str(e)}), 400

        user.update(blockchain_account_key=account)
        return jsonify({'payload': user.as_dict(), "message": "Successfully registered"})
