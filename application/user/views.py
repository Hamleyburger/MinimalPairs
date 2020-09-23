from flask import Blueprint, session, request, redirect, render_template, flash, jsonify, url_for
from application.models import Word, Pair
from .forms import SearchSounds
# from .helpers import store_image
# from .helpers import clearSessionExcept

user_blueprint = Blueprint("user_blueprint", __name__,
                           static_folder="static", template_folder="templates")


@user_blueprint.route("/", methods=["GET", "POST"])
def index():
    """admin stuff"""
    return redirect(url_for("user_blueprint.contrasts"))


@ user_blueprint.route("/pairs", methods=["GET", "POST"])
def contrasts():
    # remove Pair from imports?
    # Get sounds with POST

    form = SearchSounds()
    pairs = []

    if request.method == "POST":
        if form.validate_on_submit():
            pairs = Pair.getContrasts(form.sound1.data, form.sound2.data)

    return render_template("contrasts.html", pairs=pairs, form=form)
