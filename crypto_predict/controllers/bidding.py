from datetime import datetime, timedelta

from flask_jwt import current_identity
from flask import request, jsonify

from crypto_predict.app import app, w3
from crypto_predict.utils import crypto_contract_mapping
from crypto_predict.controllers.base import BaseAPI, unlock_and_lock_eth_account, mandatory_fields_check
from crypto_predict.models.custom_exception import ValidationError
from crypto_predict.models.bidding import UserBidModel, BetModel

LOGGER = app.logger


class PlaceBid(BaseAPI):

    url = "bid"

    POST_FIELDS = ["crypto_currency", "min_estimate_value", "max_estimate_value", "for_date"]

    def get(self):

        bet_models = BetModel.query.filter_by(is_open=True).all()

        response = {}

        for bet in bet_models:

            crypto_contract = crypto_contract_mapping[request.args["crypto_currency"]](bet.bet_contract_address)
            total_bid, all_bidders_count = crypto_contract.functions.total_bids().call()
            user_bids = UserBidModel.query.filter_by(
                user_id=current_identity.id, currency=request.args["crypto_currency"]).all()
            user_bids_data = [bid.as_dict() for bid in user_bids]
            response[bet.id] = {
                "total_bid": float(total_bid),
                "all_bidders_count": all_bidders_count,
                "user_bids": user_bids_data
            }
        return jsonify(
            {
                "payload": response
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

        try:
            bet_date = datetime.utcnow().date() + timedelta(days=2)
            bet_model = BetModel.query.filter_by(
                is_open=True, currency=request.json["crypto_currency"], for_date=bet_date).first()

            user_bid_model = UserBidModel(
                user_id=current_identity.id,
                min_estimate_value=request.json["min_estimate_value"],
                max_estimate_value=request.json["max_estimate_value"],
                bet_id=bet_model.id
            )
            user_bid_model.save()

            crypto_contract = crypto_contract_mapping[request.json["crypto_currency"]](bet_model.bet_contract_address)

        except ValueError as error:
            LOGGER.error(error, exc_info=True)
            return jsonify({"payload": {}, "message": str(error)}), 400

        except ValidationError as error:
            LOGGER.error(error, exc_info=True)
            return jsonify({"payload": {}, "message": str(error)}), 400

        try:
            tx_hash = crypto_contract.functions.add_bid().transact(
                {"from": current_identity.blockchain_account_key, "value": w3.toWei(0.1, "ether")}
            )
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
            return jsonify({"payload": {}, "message": str(error)}), 400


class ClaimBets(BaseAPI):

    url = "bet"

    def get(self):
        all_user_bid_models = UserBidModel.query.filter_by(user_id=current_identity.id).all()
        response = {}
        for bid_model in all_user_bid_models:
            response[bid_model.id] = {
                "bet": bid_model.bet.as_dict(),
                "user_bids": bid_model.as_dict()
            }

        return jsonify({"payload": response})

    @unlock_and_lock_eth_account()
    @mandatory_fields_check(["user_bid_id"])
    def post(self):
        user_bid = UserBidModel.query.filter_by(id=request.json["user_bid_id"]).first()
        if user_bid is None:
            return jsonify({"payload": {}, "message": "User bid does not exists"}), 400
        if user_bid.has_claimed is True:
            return jsonify({"payload": {}, "message": "User has already claimed the won bet"}), 400
        if user_bid.status == UserBidModel.WON:
            crypto_contract = user_bid.bet.crypto_contract
            try:
                tx_hash = crypto_contract.functions.claim_won_bid().transact(
                    {"from": current_identity.blockchain_account_key})
                w3.eth.waitForTransactionReceipt(tx_hash)
                LOGGER.info("Transaction hash for claiming the bid: %s", tx_hash.hex())
                user_bid.update(has_claimed=True)
            except ValueError as error:
                LOGGER.error(error, exc_info=True)
                return jsonify({"payload": {}, "message": str(error)}), 400
            return jsonify({"payload": current_identity.as_dict(), "message": "Successfully claimed bid"})
        else:
            return jsonify({"payload": {}, "message": "Invalid claim request"})
