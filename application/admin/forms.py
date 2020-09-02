from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField, SelectField, Form, FieldList, FormField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from application.models import Word


def emptyFiedList(fieldList):
    for item in range(len(fieldList)):
        fieldList.pop_entry()


def repopulateFieldList(formPairSounds, formPairs, word1):
    emptyFiedList(formPairSounds)

    newPairIds = []

    session["existingPairs"] = word1.allPartners()

    # Filter out illegal pairs (same word or existing pair)
    for wordid in formPairs.data:
        illegalWord = False
        if (int(wordid) == word1.id):
            print("these are the same word")
            illegalWord = True
        for word in word1.allPartners():
            if int(wordid) == word.id:
                print("already paired: {}".format(wordid))
                illegalWord = True
        if illegalWord:
            # Break out and don't add pair if pair already exists
            continue
        # add pair to "add list"
        newPairIds.append(wordid)

    # Modify fieldList to display pairs to add so user can add sounds
    for i, wordid in enumerate(newPairIds):
        # Add word2 as new entry in pairSounds
        word2 = dict(formPairs.choices).get(wordid)
        print("processing newPairs: {}".format(wordid))
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
    print("running makePairs")
    # Generates fields to fill out based on chosen pairs
    # TODO: this function must be spit in two:
    #   1) multiple select is invalid if there are none selected
    # and otherwise render the fieldList of sound inputs.
    #   2) "add sounds" is invalid if sounds are missing (where should pais be added?)
    # TODO: split in two: One validation for "define pairs" and a second for "addSounds"
    # TODO: word must be defined from select field or session after submitting new word
    # TODO: Submitpairs doesn't empty list or sth. Still need to go through whole function
    # TODO: The multiselect must reveal (and grey out?) the already existing pairs

    # check only for pairs.data and notify if empty "must select pairs"
    # Check if cue and word are valid and if user has chosen any pairs
    print("pairsounds list before check: {}".format(form.pairSounds))
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
                print("WORD 1: '{}'".format(word1.word))
                for word in form.pairSounds:
                    if word.sound1.data is "" or word.sound2.data is "":
                        repopulateFieldList(form.pairSounds, form.pairs, word1)
                        return ValidationError("No empty sound fields allowed")

                for word in form.pairSounds:
                    # get word2 from db with word id in hidden field and pair them up
                    word2 = Word.query.get(int(word.word2_id.data))
                    print("Defined words: 1: {} ({}), 2: {} ({}), trying to pair...".format(
                        word1.word, word.sound1.data, word2.word, word.sound2.data))
                    word1.pair(word2, word.sound1.data, word.sound2.data)

            else:
                raise ValidationError("Sounds cannot be null")

        # raise ValidationError("Need to define pair sound")
        return
    emptyFiedList(form.pairSounds)


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
    image = StringField("Image")
    add = SubmitField("Add")
    addAnyway = SubmitField("Add homonym")
    cancel = SubmitField("Cancel")


class AddPairForm(FlaskForm):

    word1 = SelectField("Word to pair", choices=[], default="7")
    pairs = SelectMultipleField(
        "Words to be paired with", choices=[], validators=[
            makePairList, DataRequired()])

    pairSounds = FieldList(
        FormField(PairSoundForm)
    )
    addSounds = SubmitField("Submit pairs", validators=[])
    definePairs = SubmitField("Define sounds")
