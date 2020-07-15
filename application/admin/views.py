from flask import Blueprint, session, request, redirect, render_template, flash, jsonify
#from .helpers import clearSessionExcept
from application.models import Word
from .forms import AddForm

admin_blueprint = Blueprint("admin_blueprint", __name__)


@admin_blueprint.route("/admin", methods=["GET", "POST"])
def admin():
    """admin stuff"""
    if session.get("homonyms"):
        session.pop("homonyms")
    form = AddForm()
    if request.method == "POST":
        if form.validate_on_submit():
            Word.add(word=form.word.data,
                     cue=form.cue.data, image=form.image.data)

    return render_template("add.html", form=form)
