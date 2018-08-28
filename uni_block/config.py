import os

basedir = os.path.abspath(os.path.dirname(__file__))
env = os.environ

db_user = env.get("DBUSER")
db_pass = env.get("DBPASS")
db_host = env.get("DBHOST")
db_name = env.get("DBNAME")


class Config(object):

    DEBUG = False

    # If in case postgres is used
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://%s:%s@%s/%s" % (db_user, db_pass, db_host, db_name)

    SECRET_KEY = ""


class DevConfig(Config):

    DEVELOPMENT = True
    SECRET_KEY = "some-secret-key"
