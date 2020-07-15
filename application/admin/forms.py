from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from application.models import Word


def isHomonym(form, field):
    homonyms = Word.homonyms(form.word.data)
    if homonyms:
        session["homonyms"] = homonyms
        if form.add.data:
            raise ValidationError("User must choose addAnyway")


class AddForm(FlaskForm):
    # First argument will be name and will be used as label
    word = StringField("Word", validators=[
        DataRequired(), Length(min=1, max=30), isHomonym])
    cue = StringField("Cue", validators=[
        DataRequired(), Length(min=0, max=30)])
    image = StringField("Image")
    add = SubmitField("Add")
    addAnyway = SubmitField("Add new")
