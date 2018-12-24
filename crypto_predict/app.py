import hashlib
import logging
from logging.handlers import RotatingFileHandler
from web3 import Web3, HTTPProvider

from flask import Flask, redirect, Response
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_jwt import JWT
from flask_sqlalchemy import SQLAlchemy
from flask_basicauth import BasicAuth

from werkzeug.security import safe_str_cmp
from werkzeug.exceptions import HTTPException


app = Flask(__name__, static_url_path="", static_folder="static")
app.config.from_object('crypto_predict.config.DevConfig')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

handler = RotatingFileHandler('crypto_predict.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

db = SQLAlchemy(app)


w3 = Web3(HTTPProvider(app.config["RPC_PROVIDER"]))


#########################
# JWT Handler
#########################


from crypto_predict.models.user import UserModel


def authenticate(username, password):
    user = UserModel.query.filter_by(user_name=username).first()
    if user and safe_str_cmp(user.password.encode('utf-8'), hashlib.md5(str(password).encode('utf-8')).hexdigest()):
        return user


def identity(payload):
    user_id = payload['identity']
    return UserModel.query.filter_by(id=user_id).first()


jwt = JWT(app, authenticate, identity)


################################
#   Flask-Admin Application
################################

app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'admin@123'

basic_auth = BasicAuth(app)


class BaseModelView(ModelView):
    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Not authenticated.')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())


class AuthException(HTTPException):
    def __init__(self, message):
        super().__init__(message, Response(
            "You could not be authenticated. Please refresh the page.", 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        ))


from crypto_predict.models import export_models

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, name='CryptoPredict', template_mode='bootstrap3')
for model in export_models:
    basic_auth.required(admin.add_view(BaseModelView(model, db.session)))

#################################
#   Adding routes
#################################

from crypto_predict.controllers import export_api_list
from crypto_predict.views import export_views_list

end_points = set(export_views_list).union(set(export_api_list))

for api in end_points:
    if hasattr(api, "url"):
        api_url = getattr(api, "url")
    else:
        api_url = api.__name__.lower().split("api")[0]
    api_name = api.__name__.lower()
    print (api_name, " -> ", "/{}".format(api_url))
    view = api.as_view("{}".format(api_name))
    app.add_url_rule(
        "/{}".format(api_url),
        view_func=view
    )

#################################
# Periodic Tasks
#################################

from crypto_predict.periodic_tasks import periodic_tasks

for task in periodic_tasks:
    task().schedule()
