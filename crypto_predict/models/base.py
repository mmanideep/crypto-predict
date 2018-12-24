import datetime
import uuid

from sqlalchemy.exc import SQLAlchemyError

from crypto_predict.app import db
from crypto_predict.models.custom_exception import ValidationError


def get_unique_id():
    return uuid.uuid4().hex


def get_current_utc():
    return datetime.datetime.utcnow()


class BaseModel(db.Model):
    """
        Abstract model containing default fields id, created_at, updated_at
    """
    __abstract__ = True

    id = db.Column("id", db.String(32), primary_key=True, default=get_unique_id)
    created_at = db.Column(db.DateTime(), default=get_current_utc)
    updated_at = db.Column(db.DateTime(), default=get_current_utc, onupdate=get_current_utc)
    is_deleted = db.Column(db.Boolean, default=False)

    query = db.session.query_property()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def save(self):
        session = db.session.begin_nested()
        self.pre_save()
        try:
            db.session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValidationError(str(e))

    def destroy(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValidationError(str(e))

    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        # TODO enable this
        #self.validations()
        session = db.session.begin_nested()
        try:
            db.session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise ValidationError(str(e))

    def validations(self):
        pass

    def pre_save(self):
        pass
