from flask_user import user_manager
from .models import Image
from .user import models as usermodels
from . import app, user_manager as user_manager
from flask import session

"""
When starting from empty database go() is called
in init.py to define admin from configs and set
default image
"""


def go():
    Image.setDefault()
    adminname = app.config['SECRET_ADMIN_NAME']
    adminpw = app.config['SECRET_ADMIN_PASSWORD']
    usermodels.User.setAdmin(adminname, adminpw, user_manager)
