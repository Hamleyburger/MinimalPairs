from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, RadioField, Form, FormField, PasswordField
from wtforms.fields.simple import HiddenField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from .models import User
from application import db
# from flask_wtf.file import FileField, FileRequired
# from werkzeug.utils import secure_filename
from ipapy import is_valid_ipa
from application.content_management import Content


def isIPA(form, field):
    """ Checks if input is valid IPA. Accepts if lower case version is valid """

    if not is_valid_ipa(field.data):
        if field.data != "-":
            if not is_valid_ipa(field.data.lower()):
                raise ValidationError("Not valid IPA")
            else:
                field.data = field.data.lower()


def IPAOrNothing(form, field):
    if not field.data == "":
        isIPA(form, field)


def minimumFields(form, field):
    fields = [form.sound2,
              form.sound3,
              form.sound4,
              form.sound5]

    filledOut = 0

    for item in fields:
        print("checking field")
        print("item is {}".format(type(item.data)))
        if item.data:
            filledOut += 1

    print("{} fields were filled out".format(filledOut))
    if filledOut < 2:
        raise ValidationError("Input at least two opposition sounds")


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
    sound1 = StringField(validators=[DataRequired(), isIPA, minimumFields])
    sound2 = StringField(validators=[IPAOrNothing])
    sound3 = StringField(validators=[IPAOrNothing])
    sound4 = StringField(validators=[IPAOrNothing])
    sound5 = StringField(validators=[IPAOrNothing])


def toPDF_wrap(locale):

    content = Content(locale)

    class toPDF(FlaskForm):

        # First argument of each choice needs to be file name of the background image file
        background = RadioField(
            'Label', choices=[(content["bs_filename_fishcookies"], content["bs_label_fishcookies"]), (content["bs_filename_logocat"], content["bs_label_logocat"])], validators=[DataRequired()])

    return toPDF
