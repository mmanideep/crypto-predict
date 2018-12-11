from datetime import datetime

from flask_jwt import current_identity
from flask import request, jsonify

from crypto_predict.app import app, w3
from crypto_predict.utils import crypto_contract_mapping
from crypto_predict.controllers.base import BaseAPI, unlock_and_lock_eth_account, mandatory_fields_check
from crypto_predict.models.custom_exception import ValidationError
from crypto_predict.models.bidding import UserBidModel

LOGGER = app.logger


class PlaceBid(BaseAPI):

    url = "bid"

    POST_FIELDS = ["bid_value_in_ethers", "crypto_currency", "min_estimate_value", "max_estimate_value", "for_date"]

    @mandatory_fields_check(["crypto_currency"])
    def get(self):
        if request.args["crypto_currency"] not in crypto_contract_mapping.keys():
            return jsonify(
                {
                    "payload": {},
                    "message": "{} are the only valid currencies".format(", ".join(crypto_contract_mapping.keys()))
                }
            ), 400
        crypto_contract = crypto_contract_mapping[request.args["crypto_currency"]]
        total_bid, all_bidders_count = crypto_contract.functions.total_bids().call()
        user_bids = UserBidModel.query.filter_by(
            user_id=current_identity.id, currency=request.args["crypto_currency"]).all()
        user_bids_data = [bid.as_dict() for bid in user_bids]
        return jsonify(
            {
                "payload": {
                    "total_bid": float(total_bid),
                    "all_bidders_count": all_bidders_count,
                    "user_bids": user_bids_data
                }
            })

    @unlock_and_lock_eth_account()
    @mandatory_fields_check(POST_FIELDS)
    def post(self):
        if request.json["crypto_currency"] not in crypto_contract_mapping.keys():
            return jsonify(
                {
                    "payload": {},
                    "message": "{} are the only valid currencies".format(", ".join(crypto_contract_mapping.keys()))
                }
            ), 400
        crypto_contract = crypto_contract_mapping[request.json["crypto_currency"]]

        try:
            user_bid_model = UserBidModel(
                user_id=current_identity.id,
                min_estimate_value=request.json["min_estimate_value"],
                max_estimate_value=request.json["max_estimate_value"],
                for_date=datetime.strptime(request.json["for_date"], "%Y-%m-%d").date(),
                currency=request.json["crypto_currency"]
            )
            user_bid_model.save()

        except ValueError as error:
            LOGGER.error(error, exc_info=True)
            return jsonify({"payload": {}, "message": str(error)}), 400

        except ValidationError as error:
            LOGGER.error(error, exc_info=True)
            return jsonify({"payload": {}, "message": str(error)}), 400

        try:
            tx_hash = crypto_contract.functions.add_bid().transact({"from": current_identity.blockchain_account_key})
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            LOGGER.info(
                "Successfully placed bid for {} by user {}. Gas consumed {}".format(
                        request.json["crypto_currency"], current_identity.id, receipt['gasUsed']
                    )
            )
            total_bid, total_number_of_bidders = crypto_contract.functions.total_bids().call()
            return jsonify(
                {
                    "payload": {"total_bid": str(total_bid), "total_number_of_bidders": total_number_of_bidders},
                    "message": "Successfully placed the bid"
                }
            )
        except ValueError as error:
            # Todo catch ran out of balance errors
            LOGGER.error(error, exc_info=True)
            return jsonify({"payload": {}, "message": "Something went wrong please try later"}), 400
