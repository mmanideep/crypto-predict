import hashlib

from crypto_predict.app import db, w3
from crypto_predict.models.base import BaseModel
from crypto_predict.models.custom_exception import ValidationError


class UserModel(BaseModel):

    __tablename__ = "portal_user"

    user_name = db.Column(db.String(32), unique=True, nullable=False)
    first_name = db.Column(db.String(32), nullable=False)
    last_name = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(32), nullable=False)
    blockchain_account_key = db.Column(db.String(42))
    email = db.Column(db.String(), unique=True, nullable=False)
    phone = db.Column(db.String(), unique=True, nullable=False)
    image_url = db.Column(db.String())

    def get_basic_data(self):
        basic_details_keys = [
            "id", "user_name", "first_name", "last_name", "primary_alias_id", "image_url", "phone"]
        return {key: getattr(self, key) for key in basic_details_keys}

    def __repr__(self):
        return '<PortalUser %r>' % self.user_name

    def as_dict(self):
        private_keys = ["password"]
        user_data = {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in private_keys}
        return user_data

    def save(self):
        if len(self.password) < 8:
            raise ValidationError("Password length cannot be less than 8 characters")
        self.password = hashlib.md5(str(self.password).encode('utf-8')).hexdigest()
        super(UserModel, self).save()

    @property
    def ether_balance(self):
        return w3.eth.getBalance(self.blockchain_account_key)
