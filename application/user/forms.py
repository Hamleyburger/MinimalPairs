from timeit import repeat
from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectMultipleField, RadioField, Form, FormField, PasswordField, FileField
from wtforms.fields.simple import HiddenField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email

from application.models import PermaImage
from .models import User
from application import db, app
# from flask_wtf.file import FileField, FileRequired
# from werkzeug.utils import secure_filename
from ipapy import is_valid_ipa
from application.content_management import Content
import imghdr
import email_validator
import requests
  


def isValidSymbol(form, field):
    """ Checks if input is valid IPA or accepted alternative. Accepts if lower case version is valid IPA """

    if not is_valid_ipa(field.data):

        if (field.data != "-") and (field.data != "å"):
            if not is_valid_ipa(field.data.lower()):
                raise ValidationError("Not valid IPA")
            else:
                field.data = field.data.lower()


def isWildCard(form, field):
    if field.data != "*":
        isValidSymbol(form, field)


def IPAOrNothing(form, field):
    if not field.data == "":
        isValidSymbol(form, field)


def minimumFields(form, field):
    fields = [form.sound2,
              form.sound3,
              form.sound4,
              form.sound5]

    filledOut = 0

    for item in fields:
        if item.data:
            filledOut += 1

    print("{} fields were filled out".format(filledOut))
    if filledOut < 2:
        raise ValidationError("Input at least two opposition sounds")

def reCaptcha_valid(form, field):

    secret_key = app.config["RECAPTCHA_PRIVATE_KEY"]
    token = form.token.data

        # captcha verification
    data = {
        'response': token,
        'secret': secret_key
    }
    resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result_json = resp.json()

    print(result_json)

    if not result_json.get('success'):
        raise ValidationError("Failed reCaptcha check")

class SearchSounds(FlaskForm):
    sound1 = StringField(validators=[DataRequired(), isValidSymbol])
    sound2 = StringField(validators=[DataRequired(), isWildCard])


class SearchMOs(FlaskForm):
    sound1 = StringField(
        validators=[DataRequired(), isValidSymbol, minimumFields])
    sound2 = StringField(validators=[IPAOrNothing])
    sound3 = StringField(validators=[IPAOrNothing])
    sound4 = StringField(validators=[IPAOrNothing])
    sound5 = StringField(validators=[IPAOrNothing])


def toPDF_wrap(locale):

    repeatpatterns = db.session.query(PermaImage).filter_by(type="repeatpattern").all()
    choices = []
    my_choice_objects = {}
    for image in repeatpatterns:
        if locale == "en":
            choices.append((str(image.id), image.display_name_en))
        else:
            choices.append((str(image.id), image.display_name_da))

        my_choice_objects[image.id] = image

    class toPDF(FlaskForm):

        # First argument of each choice needs to be file name of the background image file
        background = RadioField(
            'Label', choices=choices, validators=[DataRequired()])
        choice_objects = my_choice_objects

    return toPDF



  
class contactForm(FlaskForm):
    name = StringField(label='Navn', validators=[DataRequired()])
    email = StringField(label='Email', validators=[
      DataRequired(), Email(granular_message=True)])
    message= TextAreaField(label='Besked', validators=[DataRequired()])
    submitcontact = SubmitField(label="Send")
    token = HiddenField(id="rectoken", validators=[reCaptcha_valid])
    agree = BooleanField("Send", validators=[DataRequired()])
