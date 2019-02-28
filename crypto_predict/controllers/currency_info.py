import  datetime
from flask import request, jsonify

from crypto_predict.controllers.base import BaseAPI, mandatory_fields_check
from crypto_predict.models.custom_exception import ValidationError
from crypto_predict.utils import BlockChainInfo


class CryptoCurrenciesInfo(BaseAPI):

    @mandatory_fields_check(["currency", "to_date"])
    def get(self):
        try:
            to_date = datetime.datetime.strptime(request.args['to_date'], "%d-%m-%Y")
        except ValueError as e:
            return jsonify({"payload": {}, "message": str(e)}), 400
        try:
            return BlockChainInfo.get_time_range_data(to_date, request.args['currency'])
        except ValidationError as e:
            return jsonify({"payload": {}, "message": str(e)}), 400
