from flask import Blueprint, session, request, redirect, render_template, flash, jsonify, url_for
from application.models import Word, Group, Sound
from application import db
from .forms import SearchSounds
# from .helpers import store_image
# from .helpers import clearSessionExcept

user_blueprint = Blueprint("user_blueprint", __name__,
                           static_folder="static", template_folder="templates")


@user_blueprint.route("/", methods=["GET", "POST"])
def index():
    """admin stuff"""

    return render_template("userindex.html")


@ user_blueprint.route("/pairs", methods=["GET", "POST"])
def contrasts():
    # remove Pair from imports?
    # Get sounds with POST

    form = SearchSounds()
    pairs = []

    if request.method == "POST":
        if form.validate_on_submit():
            sound1 = Sound.get(form.sound1.data)
            pairs = sound1.getContrasts(form.sound2.data)

    return render_template("contrasts.html", pairs=pairs, form=form)
