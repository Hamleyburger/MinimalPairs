from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, Form, FormField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from application.models import Word, Pair
#from flask_wtf.file import FileField, FileRequired
#from werkzeug.utils import secure_filename
from ipapy import is_valid_ipa
from markupsafe import Markup


def isIPA(form, field):
    if not is_valid_ipa(field.data):
        if field.data is not "Ø":
            raise ValidationError("Not valid IPA")


class SearchSounds(FlaskForm):
    sound1 = StringField(validators=[DataRequired(), isIPA])
    sound2 = StringField(validators=[DataRequired(), isIPA])
    search_icon = Markup("<i class='fa fa-search'></i>")
    search = SubmitField(search_icon)


class toPDF(FlaskForm):
    # First argument of each choice needs to be file name of the background image file
    background = RadioField(
        'Label', choices=[('fiskpattern.svg', 'Fish cookies'), ('catpattern.svg', 'Logo cats')])
    submit = SubmitField()
