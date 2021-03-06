from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, Form, FormField, PasswordField
from wtforms.fields.simple import HiddenField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from .models import User
from application import db
#from flask_wtf.file import FileField, FileRequired
#from werkzeug.utils import secure_filename
from ipapy import is_valid_ipa
from markupsafe import Markup


def isIPA(form, field):
    if not is_valid_ipa(field.data):
        if field.data is not "Ø":
            raise ValidationError("Not valid IPA")


# Commented out this admin login form since I'm experimenting with Flask-User

# def adminExists(form, field):
#    admin = db.session.query(User).filter_by(
#        username=field.data).filter_by(role=2).first()
#    if not admin:
#        raise ValidationError("Invalid username")


# def pwCorrect(form, field):
#    admin = db.session.query(User).filter_by(
#        username=form.username.data).filter_by(role=2).first()
#    print(str(admin) + " attempted to login")
#    if not admin:
#        print("not admin")
#        return
#    elif admin.password != field.data:
#        print("pw not the same")
#        print(field.data)
#        raise ValidationError("Incorrect password")
#    else:
#        form.id = admin.id


# class AdminLogin(FlaskForm):
#    username = StringField("label", validators=[DataRequired(), adminExists])
#    password = PasswordField("label", validators=[DataRequired(), pwCorrect])
#    id = None


class SearchSounds(FlaskForm):
    sound1 = StringField(validators=[DataRequired(), isIPA])
    sound2 = StringField(validators=[DataRequired(), isIPA])


class SearchMOs(FlaskForm):
    sound1 = StringField(validators=[DataRequired(), isIPA])
    sound2 = StringField(validators=[DataRequired(), isIPA])


class toPDF(FlaskForm):
    # First argument of each choice needs to be file name of the background image file
    background = RadioField(
        'Label', choices=[('fiskpattern.svg', 'Fish cookies'), ('catpattern.svg', 'Logo cats')], validators=[DataRequired()])
