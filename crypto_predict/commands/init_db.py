from crypto_predict.app import db
from crypto_predict.models import *
from crypto_predict.commands.base import BaseCommand


class InitDb(BaseCommand):

    def command(self, *args, **kwargs):
        db.create_all()
        db.session.commit()
