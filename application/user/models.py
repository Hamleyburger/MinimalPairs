from flask_user.user_manager import UserManager
from application import db, app
from flask_user import UserMixin


class User(db.Model, UserMixin):
    """ Users can have different roles """
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    # id, username and password properties neessary for Flask-User
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')

    # Active and role will have to do with Flask-User
    active = db.Column(db.Boolean(), nullable=False, server_default='0')
    role = db.Column(db.Integer, nullable=False, server_default=db.text('1'))
