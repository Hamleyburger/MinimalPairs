#!/bin/env python

import sentry_sdk
from flask import Flask, g
from sentry_sdk.integrations.flask import FlaskIntegration
# flask_session could only be imported when downgrading werkzeug:
# pip uninstalled werkzeug and pip installed werkzeug==0.16.0
from flask_session import Session
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager
from .content_management import Content
from flask_migrate import Migrate
import stripe



# Sentry
def before_send(event, hint):
    if app.config["DEBUG"]:
        print("\n\nNot sending error event to Sentry.io")
        return None
    else:
        return event

sentry_sdk.init(
    dsn="https://f9fb4e8eb2904b20869f5e8d11f138e2@o837681.ingest.sentry.io/5813571",
    integrations=[FlaskIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=0,
    before_send=before_send

)



# Configure application
app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')


# All configs are taken from object in config.py
app.config.from_object("configd.ProductionConfig")


# Instantiate Session
Session(app)

# Instantiate debug toolbar
debugToolbar = DebugToolbarExtension(app)

# Instantiate SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize flask-user and make an admin user if not exists
from .user.models import User, Userimage
user_manager = UserManager(app, db, User)

# Instantiate Flask migrate
migrate = Migrate(app, db, render_as_batch=True)

# Configure Stripe
stripe.api_key = app.config["STRIPE_SECRET_KEY"]


# Views.py must be imported AFTER instantiating the app. Otherwise circular import problems

from application.admin.views import admin_blueprint
from application.user.views import user_blueprint
from application.errors.handlers import errors

app.register_blueprint(admin_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(errors)
# app.register_blueprint(transactions)
# app.register_blueprint(main)

# Using context processor to pass content to all templates

@app.context_processor
def get_content():
    # Must return a dict (Conten() returns a dict)
    return Content()



from . import setdefaults
print("Checking defaults...")
setdefaults.go()




