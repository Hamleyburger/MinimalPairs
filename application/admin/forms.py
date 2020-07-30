from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField, Form, FieldList, FormField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from application.models import Word


def emptyFiedList(fieldList):
    for item in range(len(fieldList)):
        fieldList.pop_entry()


def repopulateFieldList(formPairSounds, formPairs, word1):
    emptyFiedList(formPairSounds)

    for i, wordid in enumerate(formPairs.data):
        # Add word2 as new entry in pairSounds
        word2 = dict(formPairs.choices).get(wordid)
        formPairSounds.append_entry()
        field = formPairSounds[i]
        field.word2_id.data = wordid  # This field is hidden
        field.label.text = "Differing sounds:"
        field.sound1.label.text = "'" + word1 + "':"
        field.sound2.label.text = "'" + word2 + "':"


def isHomonym(form, field):
    homonyms = Word.homonyms(form.word.data)
    if homonyms:
        session["homonyms"] = homonyms
        if form.add.data or form.addSounds.data:
            raise ValidationError(
                "User must choose whether to add new or use old")


def pairsDefined(form, field):
    # Ensures that the "choose pairs" field is invalid if pairs are chosen but not filled out.
    # Generates fields to fill out based on chosen pairs
    # TODO: tidy up the actual "add sounds" part
    # TODO: generate sound pairs from list and add to db (no empty fields)./
    # TODO: Apply to "add anyway": only "add sounds" can be valid, but s word added?

    # Check if cue and word are valid and if user has chosen any pairs
    if form.word.data and form.cue.data and form.pairs.data:

        word1 = form.word.data + " (" + form.cue.data + ")"
        # If user has not clicked "Add sounds", refresh list from pairs
        if not form.addSounds.data:
            # Make new list from chosen pairs
            repopulateFieldList(form.pairSounds, form.pairs, word1)

        else:
            # User clicked "Add sounds"

            # TODO: Check if each field is filled out. If any field is not filled out,
            # don't store anything. Else store all in database.

            if form.pairSounds.data:
                print("WORD 1: '{}'".format(word1))
                for word in form.pairSounds:
                    if word.sound1.data is "" or word.sound2.data is "":
                        print("Screw this")
                        return
                print("adding but not committing yet")
                db_word1 = Word.add(
                    form.word.data, form.image.data, form.cue.data)
                for word in form.pairSounds:
                    db_word2 = Word.query.get(int(word.word2_id.data))
                    print("pairing words in db: 1: {} ({}), 2: {} ({})".format(
                        db_word1.word, word.sound1.data, db_word2.word, word.sound2.data))
                    db_word1.pair(db_word2, word.sound1.data, word.sound2.data)

            else:
                raise ValidationError("Sounds must be filled out")

        # raise ValidationError("Need to define pair sound")
        return
    emptyFiedList(form.pairSounds)


class PairSoundForm(Form):
    sound1 = StringField("Sound1", validators=[DataRequired()])
    sound2 = StringField("Sound2", validators=[DataRequired()])
    word2_id = HiddenField("word2_id")


class AddForm(FlaskForm):
    # First argument will be name and will be used as label
    word = StringField("Word", validators=[
        DataRequired(), Length(min=1, max=30), isHomonym])
    cue = StringField("Cue", validators=[
        DataRequired(), Length(min=0, max=30)])
    image = StringField("Image")
    add = SubmitField("Add")
    addAnyway = SubmitField("Add homonym")
    cancel = SubmitField("Cancel")
    addSounds = SubmitField("Add sounds")

    pairs = SelectMultipleField(
        "Add pairs", choices=[], validators=[pairsDefined])

    pairSounds = FieldList(
        FormField(PairSoundForm)
    )
