from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, BooleanField, SelectMultipleField, SelectField, Form, FieldList, FormField, HiddenField, DateTimeField
from wtforms.validators import DataRequired, Length, EqualTo, Required, ValidationError
from application.models import Word
from .models import News
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from ipapy import is_valid_ipa
from .filehelpers import validate_image
from datetime import datetime
from wtforms_sqlalchemy.fields import QuerySelectField


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
                    if word.sound1.data == "" or word.sound2.data == "":
                        repopulateFieldList(form.pairSounds, form.pairs, word1)
                        raise ValidationError("No empty sound fields allowed")
                    if (not is_valid_ipa(word.sound1.data) and (word.sound1.data != "-")) or (not is_valid_ipa(word.sound2.data) and (word.sound2.data != "-")):
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

def imageOK(form, field):
    if field.data:
        try:
            validate_image(field.data)
        except Exception as e:
            raise ValidationError(str(e))


class PairSoundForm(Form):
    sound1 = StringField("Sound 1", validators=[DataRequired()])
    sound2 = StringField("Sound 2", validators=[DataRequired()])
    word2_id = HiddenField("word2_id")


class AddForm(FlaskForm):
    # First argument will be name and will be used as label
    word = StringField("Word", validators=[
        DataRequired(), Length(min=1, max=30), isHomonym])
    cue = StringField("Cue", validators=[Length(min=0, max=30)])
    image = FileField("Image", validators=[imageOK])
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


class ChangeForm(FlaskForm):

    """
    <form name="myform" class="popup-form" method="POST" enctype="multipart/form-data"
        action="{{ url_for('admin_blueprint.change') }}">
        <h1 id="formtitle"></h1>

        <input type="hidden" id="custId" name="newwordid" value="">

        <label for="newword"><b>Change spelling</b></label>
        <input type="text" placeholder="jinjaoldword" name="newword">

        <label for="newcue"><b>Change cue</b></label>
        <input type="text" placeholder="jinjaoldcue" name="newcue">

        <label for="image"><b>Change image</b></label>
        <input autocomplete="off" id="image" name="newimg" required="" type="file">
        <label class="change-file-label file-label-name" for="image"></label>

        <button type="button" class="btn save" onclick="sendChanges()">Save</button>
        <button type="button" class="btn delete" onclick="requestDelete()">Delete</button>
        <button id="closeButton" type="button" class="btn cancel" onclick="closeForm()">Close</button>
    </form>
    """
    pass


class ChangePairForm(FlaskForm):

        # <form id="change_pair_form" action="#" method="post">

        #         <input type="hidden" id="pair_id" name="pair_id" value="#">

        #             <label id="w1label" for="s1-input" class="form-label">Word 1</label>
        #             <input type="text" class="form-control sound_input_field" id="s1-input" name="s1" aria-describedby="w1Help" value="sound1">
        #             <div id="w1Help" class="form-text">Word one's sound</div>


        #             <label id="w2label" for="s2-input" class="form-label">Word 2</label>
        #             <input type="text" class="form-control sound_input_field" id="s2-input" name="s2" aria-describedby="w2Help" value="sound2">
        #             <div id="w2Help" class="form-text">Word two's sound</div>

        # </form>

    pair_id = HiddenField("pair_id", id="pair_id", validators=[DataRequired()])
    s1 = StringField("s1", id="s1-input", validators=[DataRequired(), Length(min=1, max=5)])
    s2 = StringField("s2", id="s2-input", validators=[DataRequired(), Length(min=1, max=5)])


class AddForm(FlaskForm):
    # First argument will be name and will be used as label
    word = StringField("Word", validators=[
        DataRequired(), Length(min=1, max=30), isHomonym])
    cue = StringField("Cue", validators=[Length(min=0, max=30)])
    image = FileField("Image", validators=[imageOK])
    add = SubmitField("Add")
    addAnyway = SubmitField("Add homonym")
    cancel = SubmitField("Cancel")


def word_query():
    return Word.query


class NewsForm(FlaskForm):

    title = StringField("Titel (da)", validators=[Length(max=50)])
    title_en = StringField("Title (en)", validators=[Length(max=50)])
    text = TextAreaField("Indhold (da)", validators=[Length(max=2000)])
    text_en = TextAreaField("Content (en)", validators=[Length(max=2000)])
    date_posted = DateTimeField("Datetime", default=datetime.today)
    word = QuerySelectField(query_factory=word_query, allow_blank=True, get_label='word', blank_text='None')
    submit_news = SubmitField()

    def __repr__(self):
        return f"News: {self.title}"