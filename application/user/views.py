from flask import Blueprint, session, request, redirect, render_template, flash, jsonify, url_for, make_response
from application.models import Word, Group, Sound
from application import db, app
from .forms import SearchSounds, toPDF
from flask_weasyprint import HTML, render_pdf


# from .helpers import store_image
# from .helpers import clearSessionExcept


user_blueprint = Blueprint("user_blueprint", __name__,
                           static_folder="static", template_folder="templates")


@user_blueprint.route("/", methods=["GET", "POST"])
def index():
    """admin stuff"""

    return render_template("userindex.html")


@user_blueprint.route("/topdf", methods=["GET", "POST"])
def topdf():
    """Make a pdf"""
    collection = []

    if session.get("collection"):
        print("there's a collection")
        id_collection = session["collection"]

        # for id in id_collection:
        #    collection.append(Word.query.get(int(id)))

    for number in range(18):
        collection.append(Word.query.get(number+1))

    template = render_template("mypdf.html", collection=collection)
    html = HTML(string=template)

    return render_pdf(html)


@user_blueprint.route("/topdf2", methods=["GET"])
def topdf2():
    """make a pdf """
    """Make a pdf"""
    collection = []

    if session.get("collection"):
        print("there's a collection")
        id_collection = session["collection"]

        # for id in id_collection:
        #    collection.append(Word.query.get(int(id)))

    for number in range(6):
        collection.append(Word.query.get(number+1))

    template = render_template("mypdf.html", collection=collection)
    html = HTML(string=template)

    return template


@ user_blueprint.route("/wordinfo/<word_id>", methods=["GET"])
def wordinfo(word_id):

    # update to actually contain contrasts
    word = Word.query.get(word_id)
    if word:
        partners = word.allPartners()

        # 2D array of all pair combinations for all partners (a list of pair lists)
        pairLists = []
        pairs = word.orderedPairs()

        # Make separate lists for pairs that contain the same word
        for partner in partners:
            pairList = []
            for pair in pairs:
                if pair.w2 == partner:
                    pairList.append(pair)
            if pairList:
                pairLists.append(pairList)

        MOsets = word.getMOSets()
        for x in MOsets:
            print("")
            for y in x:
                print(y.textify())

        return render_template("wordinfo.html", word=word, pairLists=pairLists, MOsets=MOsets)
    else:
        return redirect(url_for("user_blueprint.index"))


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


@ user_blueprint.route("/collection", methods=["GET", "POST"])
def collection():

    form = toPDF()

    for subfield in form.background:
        print(subfield.data)

    collection = []
    # Get pairs from session object
    if session.get("collection"):
        print("there's a collection")
        id_collection = session["collection"]

        for id in id_collection:
            collection.append(Word.query.get(int(id)))

    return render_template("collection.html", collection=collection, form=form)


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
