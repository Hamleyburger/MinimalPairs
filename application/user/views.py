from flask import Blueprint, session, request, redirect, render_template, flash, jsonify, url_for, make_response
from application.models import Word, Group, Sound
from application import db, app
from .forms import SearchSounds
from flask_weasyprint import HTML, render_pdf
import pdfkit

# from .helpers import store_image
# from .helpers import clearSessionExcept


user_blueprint = Blueprint("user_blueprint", __name__,
                           static_folder="static", template_folder="templates")


@user_blueprint.route("/", methods=["GET", "POST"])
def index():
    """admin stuff"""

    return render_template("userindex.html")


@user_blueprint.route("/make-my-fucking-pdf-asshole", methods=["GET"])
def topdf():
    """Make a pdf"""
    collection = []

    if session.get("collection"):
        print("there's a collection")
        id_collection = session["collection"]
        for id in id_collection:
            collection.append(Word.query.get(int(id)))

    """
    for number in range(17):
        collection.append(Word.query.get(number+1))
        """

    template = render_template("mypdf.html", collection=collection)
    html = HTML(string=template)
    return render_pdf(html)
    """
    rendered = render_template("testing.html", collection=collection)

    config = pdfkit.configuration(
        wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
    pdf = pdfkit.from_string(rendered, False, configuration=config)

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=output.pdf"

    return response
    """
    return


@user_blueprint.route("/topdf2", methods=["GET"])
def topdf2():
    """Make a pdf"""
    collection = []

    if session.get("collection"):
        print("there's a collection")
        id_collection = session["collection"]
        for id in id_collection:
            collection.append(Word.query.get(int(id)))
    collection.append(Word.query.get(33))
    for number in range(13):
        collection.append(Word.query.get(number+1))

    return render_template("mypdf.html", collection=collection)


@ user_blueprint.route("/pairs", methods=["GET", "POST"])
def contrasts():
    # remove Pair from imports?
    # Get sounds with POST

    form = SearchSounds()
    pairs = []
    collection = []

    if request.method == "POST":
        if form.validate_on_submit():
            sound1 = Sound.get(form.sound1.data)
            pairs = sound1.getContrasts(form.sound2.data)

    if session.get("collection"):
        collection = session["collection"]

    return render_template("contrasts.html", pairs=pairs, form=form, collection=collection)


@ user_blueprint.route("/collection", methods=["GET", "POST"])
def collection():

    collection = []
    # Get pairs from session object
    if session.get("collection"):
        print("there's a collection")
        id_collection = session["collection"]

        for id in id_collection:
            collection.append(Word.query.get(int(id)))

    return render_template("collection.html", collection=collection)


@ user_blueprint.route("/ajax_add2collection", methods=["POST"])
# Receives changes from user and makes changes in session
def ajax_add2collection():

    print("u wanna add to collection with ajax")
    word_id = int(request.form["id"])
    word = Word.query.get(word_id)
    print("Adding word: " + str(word.word))

    if session.get("collection"):
        collection = session["collection"]
        if word_id not in collection:
            collection.append(word_id)
        else:
            print("word id in collecton")
    else:
        session["collection"] = [word_id]
    print(session["collection"])

    return jsonify(
        id=word.id
    )


@ user_blueprint.route("/ajax_remove_from_collection", methods=["POST"])
# Receives changes from user and makes changes in session
def ajax_remove_from_collection():

    print("u wanna remove from collection with ajax")
    word_id = int(request.form["id"])
    word = Word.query.get(int(word_id))
    print("Removing word: " + str(word.word))

    if session.get("collection"):
        collection = session["collection"]
        if word_id in collection:
            collection.remove(word_id)
        else:
            print("word id was not in collecton")

    print(session["collection"])
    print(type(session["collection"]))

    return jsonify(
        id=word.id
    )
