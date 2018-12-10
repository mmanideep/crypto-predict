"""

Class BaseAPI should be used for transaction management and to log execution time

"""
import datetime

from flask import request, jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_identity
from werkzeug.exceptions import BadRequest

from crypto_predict.app import db, app, w3
from crypto_predict.models.custom_exception import ValidationError

LOGGER = app.logger


def transaction_mgmt(func):
    """
        Creates a db session and commits on successful execution of API call
    """
    def executable(*args, **kwargs):
        session = db.session.begin_nested()
        response = func(*args, **kwargs)
        if type(response) == tuple:
            status_code = response[1]
        else:
            status_code = response.status_code
        if status_code in [200, 201]:
            session.commit()
            db.session.commit()
        else:
            session.rollback()
            db.session.rollback()
        return response
    return executable


def log_execution_time_and_error_handling(func, *args, **kwargs):
    """
        Logs time taken by the API call and logs error in case of internal server error
    """
    def executable(*args, **kwargs):
        start_datetime = datetime.datetime.utcnow()
        try:
            response = func(*args, **kwargs)
            end_datetime = datetime.datetime.utcnow()
            LOGGER.info("Execution time info: Time taken: {} - method: {} - url: {}".format(
                str(end_datetime - start_datetime)[:-3],
                request.method,
                str(request.url_rule)
            ))
            return response
        except Exception as e:
            LOGGER.error(e, exc_info=True)
            return jsonify({"payload": {}, "message": "Internal Server Error"}), 500
    return executable


def mandatory_fields_check(mandatory_fields):
    """
    Decorator to check if required fields exists in the request
    :param mandatory_fields:
    :return:
    """

    def wrapper(func, *args, **kwargs):
        def executable(*args, **kwargs):
            if request.method in ["POST", "PUT", "PATCH"]:
                if not set(request.json.keys()) >= set(mandatory_fields):
                    return jsonify({
                        "payload": {},
                        "message": "[" + ",".join(mandatory_fields) + "] are required fields"}
                    ), 400
            elif request.method == "GET":
                if not set(request.args.keys()) >= set(mandatory_fields):
                    return jsonify({
                        "payload": {},
                        "message": "[" + ",".join(mandatory_fields) + "] are required fields"}
                    ), 400
            response = func(*args, **kwargs)
            return response
        return executable
    return wrapper


def unlock_and_lock_eth_account():
    """
        Decorator to unlock etheruem account before doing write transactions
        And locking it back once operation is done.
    @return:
    """
    def wrapper(func):
        def executable(*args, **kwargs):
            try:
                if "ETH-Password" in request.headers:
                    eth_password = request.headers['ETH-Password']
                else:
                    try:
                        eth_password = request.json.get("eth_password", "")
                    except BadRequest:
                        eth_password = ""
                if not eth_password.strip():
                    raise ValidationError("eth_password should be present in either json or in headers as ETH-Password")
                eth_account_key = current_identity.blockchain_account_key
                w3.personal.unlockAccount(eth_account_key, eth_password)  # pylint: disable= no-member
                LOGGER.info("Unlocked eth account..")
                response = func(*args, **kwargs)
                w3.personal.lockAccount(eth_account_key)  # pylint: disable= no-member
                LOGGER.info("Locked eth account..")
                return response
            except (ValidationError, ValueError) as error:
                LOGGER.error(error, exc_info=True)
                return jsonify({"message": str(error)}), 400
            except Exception as error:
                LOGGER.error(error, exc_info=True)
                return jsonify({"payload": {}, "message": "Internal Server Error"}), 500
        return executable
    return wrapper


def login_required(func, *args, **kwargs):
    """
        Logs time taken by the API call and logs error in case of internal server error
    """

    def executable(*args, **kwargs):
        response = func(*args, **kwargs)
        return response
    response = jwt_required()(executable)
    return response


class BaseAPI(MethodView):
    """
        Base class for API development
    """

    decorators = (transaction_mgmt, log_execution_time_and_error_handling, login_required)


class UnAuthenticatedBaseAPI(MethodView):
    """
        Base class for avoiding login required
    """
    decorators = (transaction_mgmt, log_execution_time_and_error_handling)
