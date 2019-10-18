from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from egnyte_app.app import login, db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    egnyte_integration = db.relationship('EgnyteIntegration', uselist=False, back_populates='user')

    def __str__(self) -> str:
        return self.username

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
