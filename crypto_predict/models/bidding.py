import datetime

from crypto_predict.app import db
from crypto_predict.models.base import BaseModel
from crypto_predict.models.custom_exception import ValidationError
from crypto_predict.models.non_db_models.crypto_currency import CryptoCurrency
from crypto_predict.utils import crypto_contract_mapping


class BetModel(BaseModel):

    __tablename__ = "bet"

    CRYPTO_CURRENCIES = [
        CryptoCurrency.Ethereum, CryptoCurrency.Litecoin, CryptoCurrency.BitcoinCash,
        CryptoCurrency.Bitcoin, CryptoCurrency.Dogecoin
    ]

    bet_contract_address = db.Column(db.String(42), nullable=False)
    currency = db.Column(db.String(), nullable=False)
    for_date = db.Column(db.Date, nullable=False)
    is_open = db.Column(db.Boolean(), nullable=False)

    @property
    def crypto_contract(self):
        return crypto_contract_mapping[self.currency](self.bet_contract_address)

    def validations(self):
        if self.for_date - datetime.datetime.utcnow().date() != datetime.timedelta(days=2):
            raise ValidationError("for_date and created_at date difference should be equal to two days")
        if self.currency not in BetModel.CRYPTO_CURRENCIES:
            raise ValidationError("Invalid currency")


class UserBidModel(BaseModel):

    __tablename__ = "user_bid"

    WON = 1
    LOST = -1
    IN_PROGRESS = 0

    STATUS = [WON, LOST, IN_PROGRESS]

    user_id = db.Column(db.String(32), db.ForeignKey('user.id'))
    min_estimate_value = db.Column(db.Float, nullable=False)
    max_estimate_value = db.Column(db.Float, nullable=False)
    bet_id = db.Column(db.String(32), db.ForeignKey('bet.id'))
    status = db.Column(db.Integer(), nullable=False, default=IN_PROGRESS)
    has_claimed = db.Column(db.Boolean(), nullable=False, default=False)

    def validations(self):
        if self.min_estimate_value >= self.max_estimate_value:
            raise ValidationError("Minimum can't be less than or equal to max")
        difference_in_est = 100 - (self.min_estimate_value/self.max_estimate_value) * 100
        if difference_in_est > 3 or difference_in_est < -3:
            raise ValidationError("Percentage difference between max and min cannot be more than 0.5 %")
        if self.status not in UserBidModel.STATUS:
            raise ValidationError("status has to be one of ".join([str(x) for x in UserBidModel.STATUS]))
        if self.has_claimed is True and not self.status == UserBidModel.WON:
            raise ValidationError("Invalid has_claimed value")

    @property
    def user(self):
        from crypto_predict.models.user import UserModel
        return UserModel.query.filter_by(id=self.user_id).first()

    @property
    def bet(self):
        return BetModel.query.filter_by(id=self.bet_id).first()
