from datetime import timedelta
import configparser
import os
from web3 import Web3

basedir = os.path.abspath(os.path.dirname(__file__))

config = configparser.ConfigParser()
config.read('crypto_predict/config.ini')
env = config["DEFAULT"]

db_user = "crypto_predict"
db_pass = env.get("DBPASS")
db_host = env.get("DBHOST")
db_name = "crypto_predict"


class Config(object):

    DEBUG = False

    # If in case postgres is used
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://%s:%s@%s/%s" % (db_user, db_pass, db_host, db_name)
    JWT_EXPIRATION_DELTA = timedelta(seconds=604800)
    SECRET_KEY = ""
    RPC_PROVIDER = env.get("RPC_PROVIDER")
    ADMIN_ETH_ACCOUNT = Web3.toChecksumAddress(env.get("ADMIN_ETH_ACCOUNT"))
    ADMIN_ETH_PASSWORD = env.get("ADMIN_ETH_PASSWORD")
    INITIAL_BALANCE = env.get("INITIAL_BALANCE")


class DevConfig(Config):
    DEBUG = True
    ENV = "development"
    SECRET_KEY = "some-secret-key"
