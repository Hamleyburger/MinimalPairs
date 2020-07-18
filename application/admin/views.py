from flask import Blueprint, session, request, redirect, render_template, flash, jsonify
#from .helpers import clearSessionExcept
from application.models import Word
from .forms import AddForm
from application import db

admin_blueprint = Blueprint("admin_blueprint", __name__)


@admin_blueprint.route("/add", methods=["GET", "POST"])
def add():
    """admin stuff"""
    if session.get("homonyms"):
        session.pop("homonyms")
    form = AddForm()
    if request.method == "POST":
        if form.validate_on_submit():
            Word.add(word=form.word.data,
                     cue=form.cue.data, image=form.image.data)

    return render_template("add.html", form=form)


@admin_blueprint.route("/change", methods=["GET", "POST"])
def change():
    words = Word.query.all()
    return render_template("change.html", words=words)


@admin_blueprint.route("/ajax_word_changer", methods=["POST"])
# Receives changes from user and makes changes in database
def ajax():
    print("running ajax")
    newword = request.form["newword"]
    newcue = request.form["newcue"]
    newimg = request.form["newimg"]
    word_id = request.form["id"]

    if newimg is "":
        print("no new image")
    else:
        print("new image is: {}".format(newimg))

    return jsonify({"id": word_id})
