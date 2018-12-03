import copy

from flask import request, jsonify
from flask_jwt import current_identity

from crypto_predict.models.user import UserModel
from crypto_predict.controllers.base import BaseAPI, mandatory_fields_check


class UserInfo(BaseAPI):

    url = "user"

    def get(self):
        user_id = request.args.get("user_id")
        if isinstance(user_id, list):
            users = UserModel.query.filter(UserModel.id.in_(user_id))
            return jsonify({"payload": [user.get_basic_data for user in users]})
        elif isinstance(user_id, str):
            user = UserModel.query.filter_by(id=user_id).first()
            return jsonify({"payload": user.as_dict()})
        else:
            return jsonify({"payload": current_identity.as_dict()})

    @mandatory_fields_check(["user_id"])
    def patch(self):
        user_data = copy.deepcopy(request.json)
        user_id = user_data.pop("user_id")
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"payload": {}, "message": "Invalid user"}), 400
        user.update(**user_data)
        return jsonify({"payload": user.as_dict()})
