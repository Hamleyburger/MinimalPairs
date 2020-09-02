from flask import Blueprint, session, request, redirect, render_template, flash, jsonify, url_for
# from .helpers import clearSessionExcept
from application.models import Word
from .forms import AddForm, AddPairForm
from application import db

admin_blueprint = Blueprint("admin_blueprint", __name__)


@admin_blueprint.route("/", methods=["GET", "POST"])
def index():
    """admin stuff"""
    return redirect(url_for("admin_blueprint.add"))


@admin_blueprint.route("/add", methods=["GET"])
def add():
    """admin stuff"""

    session.pop("homonyms", None)
    session.pop("existingPairs", None)
    form = AddForm()
    pairForm = AddPairForm()
    pairForm.word1.choices = [(str(word.id), word.word + " (" + word.cue + ")")
                              for word in db.session.query(Word).all()]
    pairForm.pairs.choices = [(str(word.id), word.word + " (" + word.cue + ")")
                              for word in db.session.query(Word).all()]
    wordToRemember_id = session.get("word1") if session.get("word1") else None
    pairForm.word1.default = wordToRemember_id
    pairForm.process()

    return render_template("add.html", form=form, pairForm=pairForm)


@admin_blueprint.route("/add_word", methods=["POST"])
def add_word():
    session.pop("homonyms", None)
    session.pop("existingPairs", None)
    form = AddForm()
    pairForm = AddPairForm()
    pairForm.word1.choices = [(str(word.id), word.word + " (" + word.cue + ")")
                              for word in db.session.query(Word).all()]
    pairForm.pairs.choices = [(str(word.id), word.word + " (" + word.cue + ")")
                              for word in db.session.query(Word).all()]

    if form.cancel.data:
        return redirect(url_for("admin_blueprint.add"))
    if form.validate_on_submit():
        print("was valid")
        if form.add.data or form.addAnyway.data:
            print("adding from view")
            wordToRemember = Word.add(word=form.word.data,
                                      cue=form.cue.data, image=form.image.data)
        session["word1"] = str(wordToRemember.id)
        db.session.commit()

        return redirect(url_for("admin_blueprint.add"))
    else:
        flash(u"{}".format(form.errors), "danger")

    return render_template("add.html", form=form, pairForm=pairForm)


@admin_blueprint.route("/add_pairs", methods=["POST"])
def add_pairs():
    session.pop("homonyms", None)
    session.pop("existingPairs", None)
    form = AddForm()
    pairForm = AddPairForm()
    pairForm.word1.choices = [(str(word.id), word.word + " (" + word.cue + ")")
                              for word in db.session.query(Word).all()]
    pairForm.pairs.choices = [(str(word.id), word.word + " (" + word.cue + ")")
                              for word in db.session.query(Word).all()]

    if pairForm.validate_on_submit():
        print("pairform valid")
        db.session.commit()
        return redirect(url_for("admin_blueprint.add"))
    else:
        print("Pairform errors: {}".format(pairForm.errors))

    return render_template("add.html", form=form, pairForm=pairForm)


@ admin_blueprint.route("/change", methods=["GET", "POST"])
def change():
    words = Word.query.all()
    return render_template("change.html", words=words)


@ admin_blueprint.route("/pairs/<word_id>", methods=["GET", "POST"])
def pairs(word_id):
    word = Word.query.filter_by(id=word_id).first()
    return render_template("pairs.html", words=word.allPartners())


@ admin_blueprint.route("/ajax_word_changer", methods=["POST"])
# Receives changes from user and makes changes in database
def ajax_change():
    print("running ajax")
    newword = request.form["newword"]
    newcue = request.form["newcue"]
    newimg = request.form["newimg"]
    word_id = request.form["id"]

    print("id: {}, new word: {}, new cue: {}, new image: {}".format(
        word_id, newword, newcue, newimg))

    word = Word.change(id=int(word_id), newword=newword,
                       newcue=newcue, newimg=newimg)

    return jsonify(
        id=word.id,
        newword=word.word,
        newcue=word.cue,
        newimg=word.image.name
    )


@ admin_blueprint.route("/ajax_word_delete", methods=["POST"])
# Receives changes from user and makes changes in database
def ajax_delete():

    print("getting word id with ajax")
    word_id = request.form["id"]
    word = Word.query.get(int(word_id))
    print("Deleting: " + str(word.word))
    word.remove()

    return jsonify(
        id=word.id
    )
