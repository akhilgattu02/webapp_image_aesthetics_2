from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import secrets

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    rod = db.Column(db.String(50))
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.String(19))

    @staticmethod
    def verify_reset_token(token):
        return User.query.filter_by(reset_token=token).first()

    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        return self.reset_token