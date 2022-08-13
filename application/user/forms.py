from email.mime import application
from timeit import repeat
from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectMultipleField, RadioField, Form, FormField, PasswordField, FileField
from wtforms.fields.simple import HiddenField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email

from application.models import PermaImage, Sound
from application import exceptions
from .models import User
from application import db, app
# from flask_wtf.file import FileField, FileRequired
# from werkzeug.utils import secure_filename
from ipapy import is_valid_ipa
from application.content_management import Content
import imghdr
import email_validator
import requests
from flask import g

  


def is_valid_symbol(form, field):
    """ Checks the input symbol. Previous check """
    field.data = field.data.lower()
    field.data = field.data.replace(" ", "")

    # Check that dash and wildcard have been used properly
    if ("-" in field.data) and (len(field.data) > 1):
        msg = Content()["dash_in_string_error"]
        g.errorfeedback = msg
        raise ValidationError(msg)

    if ("*" in field.data) and (len(field.data) > 1):
        msg = Content()["wc_in_string_error"]
        g.errorfeedback = msg
        raise ValidationError(msg)

    # Do not let anything through that isn't - or å (or * in case of pair search - already dealt with)
    if not is_valid_ipa(field.data.lower()): 
        # Check if * or - or å. If invalid and not one of these, do not allow
        if (field.data != "-") and (field.data != "å"):
            msg = Content()["invalid_ipa_error"]
            g.errorfeedback = msg
            raise ValidationError(msg)


    # Can't be ' or * or å if it gets here
    try:
        print("sound get {}".format(field.data))
        field.data = Sound.get(field.data).sound
    except exceptions.multiSyllableError as e:
        msg = Content()["multi_syllable_error"]
        g.errorfeedback = msg
        raise ValidationError(msg)
    except exceptions.syllableStructureError as e:
        msg = Content()["syllable_structure_error"]
        g.errorfeedback = msg
        raise ValidationError(msg)
    except exceptions.doubleSoundError as e:
        msg = Content()["double_sound_error"]
        g.errorfeedback = msg
        raise ValidationError(msg)
    except Exception as e:
        msg = "Noget gik galt i søgningen. Beklager!"
        print("*** *** *** *** Uncaught error in sound search using Sound.get()" + str(e))
        g.errorfeedback = msg
        raise ValidationError(msg)


def is_valid_pair_search(form, field):
    """ Checks that the search combination for pairs is valid and then checks symbol """

    # Check for double dash
    if form.sound1.data == "-" and form.sound2.data == "-":
        msg = Content()["double_dash_error"]
        g.errorfeedback = msg
        raise ValidationError(msg)

        #form.errors["va"].append(error)
    if form.sound1.data == "*":
        if form.sound2.data == "*":
            msg = Content()["double_wc_error"]
            g.errorfeedback = msg
            raise ValidationError(msg)
        else:
            temp = form.sound2.data
            form.sound2.data = form.sound1.data
            form.sound1.data = temp

    if form.sound1.data == form.sound2.data:
        msg = Content()["same_sound_error"]
        g.errorfeedback = msg
        raise ValidationError(msg)

    if field.data != "*":
        is_valid_symbol(form, field)



def required(form, field):
    if field.data == None or field.data.isspace():
        g.errorfeedback = "Der skal stå noget i begge søgefelter. Hvis en lyd skal være tom/udeladt, så brug minus, altså \"-\""


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
        msg = Content()["too_few_oppositions_error"]
        g.errorfeedback = msg
        raise ValidationError(msg)


def is_valid_MO_search(form, field):
    """ Checks that the search combination for MOs is valid and then checks symbol """
    if "*" in field.data:
        msg = Content()["MO_wc_error"]
        g.errorfeedback = msg
        raise ValidationError(msg)
    
    fields = [form.sound1, form.sound2, form.sound3, form.sound4, form.sound5]
    for f in fields:
        if field.data != "" and field != f:
            if field.data == f.data:
                msg = Content()["same_sound_error"]
                g.errorfeedback = msg
                raise ValidationError(msg)

    if not field.data == "":
        is_valid_symbol(form, field)


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


def customDatarequired(form, field):
    if not field.data or field.data.isspace():
        if isinstance(form, SearchMOs):
            msg = Content()["too_few_oppositions_error"]
            raise ValidationError(msg)
        else: # SearchSounds form
            msg = Content()["pair_data_required_error"]
            raise ValidationError(msg)

class SearchSounds(FlaskForm):
    sound1 = StringField(validators=[required, is_valid_pair_search, customDatarequired])
    sound2 = StringField(validators=[required, is_valid_pair_search, customDatarequired])


class SearchMOs(FlaskForm):
    sound1 = StringField(
        validators=[required, customDatarequired, is_valid_MO_search, minimumFields])
    sound2 = StringField(validators=[is_valid_MO_search])
    sound3 = StringField(validators=[is_valid_MO_search])
    sound4 = StringField(validators=[is_valid_MO_search])
    sound5 = StringField(validators=[is_valid_MO_search])


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
