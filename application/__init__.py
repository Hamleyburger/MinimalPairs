#!/bin/env python

from flask import Flask
# flask_session could only be imported when downgrading werkzeug:
# pip uninstalled werkzeug and pip installed werkzeug==0.16.0
from flask_session import Session
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager




# Configure application
app = Flask(__name__)


# All configs are taken from object in config.py
app.config.from_object("configu.DevelopmentConfig")


# Instantiate Session
Session(app)

# Instantiate debug toolbar
debugToolbar = DebugToolbarExtension(app)

# Instantiate SQLAlchemy
db = SQLAlchemy(app)

# Initialize flask-user and make an admin user if not exists
from .user.models import User
user_manager = UserManager(app, db, User)




# Views.py must be imported AFTER instantiating the app. Otherwise circular import problems

#from application.main.views import main
#from application.transactions.views import transactions
from application.admin.views import admin_blueprint
from application.user.views import user_blueprint

app.register_blueprint(admin_blueprint)
app.register_blueprint(user_blueprint)
# app.register_blueprint(transactions)
# app.register_blueprint(main)


from . import setdefaults
print("Checking defaults...")
setdefaults.go()