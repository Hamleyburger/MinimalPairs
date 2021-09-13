from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, RadioField, Form, FormField, PasswordField, FileField
from wtforms.fields.simple import HiddenField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from .models import User
from application import db
# from flask_wtf.file import FileField, FileRequired
# from werkzeug.utils import secure_filename
from ipapy import is_valid_ipa
from application.content_management import Content
import imghdr


def isValidSymbol(form, field):
    """ Checks if input is valid IPA or accepted alternative. Accepts if lower case version is valid IPA """

    if not is_valid_ipa(field.data):
        if field.data != "-":
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

    content = Content(locale)

    class toPDF(FlaskForm):

        # First argument of each choice needs to be file name of the background image file
        background = RadioField(
            'Label', choices=[(content["bs_filename_fishcookies"], content["bs_label_fishcookies"]), (content["bs_filename_logocat"], content["bs_label_logocat"])], validators=[DataRequired()])

    return toPDF
