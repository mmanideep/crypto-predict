import os

basedir = os.path.abspath(os.path.dirname(__file__))
env = os.environ

db_user = "crypto_predict"
db_pass = env.get("DBPASS", "crypto_predict")
db_host = env.get("DBHOST", "localhost:5432")
db_name = "crypto_predict"


class Config(object):

    DEBUG = False

    # If in case postgres is used
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://%s:%s@%s/%s" % (db_user, db_pass, db_host, db_name)

    SECRET_KEY = ""
    RPC_PROVIDER = env.get("RPC_PROVIDER", "HTTP://127.0.0.1:7545")


class DevConfig(Config):

    DEVELOPMENT = True
    SECRET_KEY = "some-secret-key"
