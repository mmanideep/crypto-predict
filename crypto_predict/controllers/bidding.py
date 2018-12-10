from flask_jwt import current_identity
from flask import request, jsonify

from crypto_predict.app import app, w3
from crypto_predict.utils import crypto_contract_mapping
from crypto_predict.controllers.base import BaseAPI, unlock_and_lock_eth_account, mandatory_fields_check

LOGGER = app.logger


class PlaceBid(BaseAPI):

    url = "bid"

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
        return jsonify({"payload": {"total_bid": float(total_bid), "all_bidders_count": all_bidders_count}})

    @unlock_and_lock_eth_account()
    @mandatory_fields_check(["bid_value_in_ethers", "crypto_currency"])
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
