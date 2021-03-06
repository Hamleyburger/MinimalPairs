from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField, SelectField, Form, FieldList, FormField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from application.models import Word
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from ipapy import is_valid_ipa


def emptyFiedList(fieldList):
    for item in range(len(fieldList)):
        fieldList.pop_entry()


def repopulateFieldList(formPairSounds, formPairs, word1):
    emptyFiedList(formPairSounds)

    newPairIds = []

    session["existingPairs"] = word1.allPartners()

    # Modify fieldList to display pairs to add so user can add sounds
    for i, wordid in enumerate(formPairs.data):
        # Add word2 as new entry in pairSounds
        word2 = dict(formPairs.choices).get(wordid)
        formPairSounds.append_entry()
        field = formPairSounds[i]
        field.word2_id.data = wordid  # This field is hidden
        field.sound1.label.text = "'" + word1.word + "':"
        field.sound2.label.text = "'" + word2 + "':"


def isHomonym(form, field):
    homonyms = Word.homonyms(form.word.data)
    if homonyms:
        session["homonyms"] = homonyms
        if not form.addAnyway.data:
            raise ValidationError(
                "User must choose whether to add new or use old")


def makePairList(form, field):
    print("\nform.makePairList:")
    # Generates fields to fill out based on chosen pairs

    if not form.pairs.data:
        emptyFiedList(form.pairSounds)
        raise ValidationError("Choose what words to pair with")
    else:
        # There are pairs to do stuff with
        word1 = Word.query.get(int(form.word1.data))
        # If user has clicked "Add sounds", refresh list from pairs
        if form.definePairs.data:  # This must be "define pairs"
            # Make new list from chosen pairs
            repopulateFieldList(form.pairSounds, form.pairs, word1)

        else:
            # User clicked "Submit Pairs/add sounds"
            # This is for "add sounds" (first btn)

            if form.pairSounds.data:
                for word in form.pairSounds:
                    if word.sound1.data is "" or word.sound2.data is "":
                        repopulateFieldList(form.pairSounds, form.pairs, word1)
                        raise ValidationError("No empty sound fields allowed")
                    if (not is_valid_ipa(word.sound1.data) and (word.sound1.data is not "Ø")) or (not is_valid_ipa(word.sound2.data) and (word.sound2.data is not "Ø")):
                        repopulateFieldList(form.pairSounds, form.pairs, word1)
                        raise ValidationError("Not valid IPA")

                for word in form.pairSounds:
                    # get word2 from db with word id in hidden field and pair them up
                    word2 = Word.query.get(int(word.word2_id.data))
                    print("incoming data says that word *{}: {}* and word *{}: {}*".format(
                        word1.word, word.sound1.data, word2.word, word.sound2.data))
                    addedPairs = word1.pair(
                        word2, word.sound1.data, word.sound2.data)
                    if addedPairs:
                        for pair in addedPairs:
                            print("Added pair:" + pair.textify())

            else:
                raise ValidationError("Sounds cannot be null")

        # raise ValidationError("Need to define pair sound")
        return
    # emptyFiedList(form.pairSounds)


class PairSoundForm(Form):
    sound1 = StringField("Sound 1", validators=[DataRequired()])
    sound2 = StringField("Sound 2", validators=[DataRequired()])
    word2_id = HiddenField("word2_id")


class AddForm(FlaskForm):
    # First argument will be name and will be used as label
    word = StringField("Word", validators=[
        DataRequired(), Length(min=1, max=30), isHomonym])
    cue = StringField("Cue", validators=[
        DataRequired(), Length(min=0, max=30)])
    image = FileField()
    add = SubmitField("Add")
    addAnyway = SubmitField("Add homonym")
    cancel = SubmitField("Cancel")


class AddPairForm(FlaskForm):

    word1 = SelectField("Word to pair", choices=[], default="1")
    pairs = SelectMultipleField(
        "Words to be paired with", choices=[], validators=[
            makePairList, DataRequired()])

    pairSounds = FieldList(
        FormField(PairSoundForm)
    )
    addSounds = SubmitField("Submit pairs", validators=[])
    definePairs = SubmitField("Define sounds")
