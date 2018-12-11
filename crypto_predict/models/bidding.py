import datetime

from crypto_predict.models.base import BaseModel
from crypto_predict.models.custom_exception import ValidationError
from crypto_predict.models.non_db_models.crypto_currency import CryptoCurrency
from crypto_predict.app import db


class UserBidModel(BaseModel):

    CRYPTO_CURRENCIES = [
        CryptoCurrency.Ethereum, CryptoCurrency.Litecoin, CryptoCurrency.BitcoinCash,
        CryptoCurrency.Bitcoin, CryptoCurrency.Ripple
    ]

    __tablename__ = "user_bid"

    user_id = db.Column(db.String(32), db.ForeignKey('user.id'))
    min_estimate_value = db.Column(db.Float, nullable=False)
    max_estimate_value = db.Column(db.Float, nullable=False)
    for_date = db.Column(db.Date, nullable=False)
    currency = db.Column(db.String(), nullable=False)
    is_closed = db.Column(db.Boolean, nullable=False, default=False)

    def save(self):
        if self.for_date - datetime.datetime.utcnow().date() != datetime.timedelta(days=2):
            raise ValidationError("for_date and created_at date difference should be equal to two days")
        if self.currency not in UserBidModel.CRYPTO_CURRENCIES:
            raise ValidationError("Invalid currency")
        difference_in_est = self.max_estimate_value - self.min_estimate_value
        if difference_in_est > 5 or difference_in_est < -5:
            raise ValidationError("Difference Cannot be more than one")
        super(UserBidModel, self).save()

    @property
    def user(self):
        from crypto_predict.models.user import UserModel
        return UserModel.query.filter_by(id=self.user_id).first()
