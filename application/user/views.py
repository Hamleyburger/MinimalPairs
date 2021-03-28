from flask import Blueprint, session, request, redirect, render_template, flash, jsonify, url_for, make_response
import json
from .helpers import getCollection, json_to_ints, manageCollection, pairCollected, easyIPAtyping, stripEmpty, getSecondBest
from application.models import Word, Group, Sound
from .models import User
from application import db, app
from .forms import SearchSounds, toPDF, SearchMOs
from flask_weasyprint import HTML, CSS, render_pdf


user_blueprint = Blueprint("user_blueprint", __name__,
                           static_folder="static", template_folder="templates")


@user_blueprint.route("/", methods=["GET"])
def index():
    """ cute front page """

    return render_template("userindex.html")


@user_blueprint.route("/lukmigind", methods=["GET", "POST"])
def adminLogin():
    """login for admin (user must know URL and no option of registering or feedback)"""

    return redirect(url_for('user.login'))


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
        print(str(url_for(
            'static', filename='images / thumbnails / thumbnail_' + word.image.name)))

        return render_template("wordinfo.html", word=word, pairLists=pairLists, MOsets=MOsets)
    else:
        return redirect(url_for("user_blueprint.index"))


@ user_blueprint.route("/pairs", methods=["GET", "POST"])
def contrasts():
    # remove Pair from imports?
    # Get sounds with POST

    pairSearchForm = SearchSounds()
    MOSearchForm = SearchMOs()

    pairs = []
    MOsets = []
    MOsets2 = []
    renderedids = []
    collectedAll = True
    collectedPairs = []
    MOmode = False

    if request.method == "POST":
        if (request.form["searchBtn"] == "pair") and pairSearchForm.validate_on_submit():
            print("pairsearchform validated")

            # Easy keyboard typing enabled:
            inputSound1 = easyIPAtyping(pairSearchForm.sound1.data)
            inputSound2 = easyIPAtyping(pairSearchForm.sound2.data)

            sound1 = Sound.get(inputSound1)
            pairs = sound1.getContrasts(inputSound2)

            # Make a list of ids of all words rendered and a list of ids in collection
            for pair in pairs:
                idlist = [pair.w1.id, pair.w2.id]
                renderedids.extend(idlist)
                if pairCollected(pair):
                    collectedPairs.extend([pair.id])
                else:
                    collectedAll = False
            renderedids = json.dumps(renderedids)

        if request.form["searchBtn"] == "MO":
            MOmode = True
            if MOSearchForm.validate_on_submit():
                print("MOsearchform validated")
                inputSound1 = easyIPAtyping(MOSearchForm.sound1.data)

                inputList = [
                    easyIPAtyping(MOSearchForm.sound2.data),
                    easyIPAtyping(MOSearchForm.sound3.data),
                    easyIPAtyping(MOSearchForm.sound4.data),
                    easyIPAtyping(MOSearchForm.sound5.data)]

                MOsounds = stripEmpty(inputList)

                sound1 = Sound.get(inputSound1)
                MOsets = sound1.getMOPairs(MOsounds)
                MOsets2 = getSecondBest(sound1, MOsounds, MOsets)

                for MO in MOsets:
                    print(MO)
            else:
                print(MOSearchForm.errors)

    print("collection: " + str(getCollection()) +
          "of type " + str(getCollection()))

    return render_template("contrasts.html",
                           pairs=pairs,
                           form=pairSearchForm,
                           form2=MOSearchForm,
                           renderedids=renderedids,
                           collectedAll=collectedAll,
                           collectedPairs=collectedPairs,
                           MOsets=MOsets,
                           MOsets2=MOsets2,
                           MOmode=MOmode)


@ user_blueprint.route("/collection", methods=["GET", "POST"])
def collection():

    # TODO: apply form     if request.method == "POST":

    form = toPDF()

    collection = []
    # Get pairs from session object
    if session.get("collection"):
        print("there's a collection")
        id_collection = session["collection"]

        for id in id_collection:
            collection.append(Word.query.get(int(id)))

    if request.method == "POST":
        if getCollection():
            if form.validate_on_submit():
                # Background file name is defined in the declaration of wtf choices in forms.py
                bgfilename = form.background.data
                template = render_template("mypdf.html", collection=collection)
                html = HTML(string=template)
                # This bit of CSS is dynamically generated, the rest is hard coded in the template
                css = CSS(
                    string='@page :left { background-image: url(/static/permaimages/' + bgfilename + ');}')

                return render_pdf(html, stylesheets=[css])

    return render_template("collection.html", collection=collection, form=form)


@user_blueprint.route("/topdf", methods=["GET"])
def topdf():
    """Make a pdf"""
    collection = []

    if session.get("collection"):
        id_collection = session["collection"]

        # for id in id_collection:
        #    collection.append(Word.query.get(int(id)))

    for number in range(18):
        collection.append(Word.query.get(number+1))

    template = render_template("mypdf.html", collection=collection)
    html = HTML(string=template)

    return render_pdf(html)


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
        session["collection"] = [word_id]

    return jsonify(
        session=getCollection()
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

    return jsonify(
        session=getCollection()
    )


@ user_blueprint.route("/ajax_collect_many", methods=["POST"])
# Receives changes from user and makes changes in session
def ajax_collect_many():

    wordids = json_to_ints(request.form["ids"])
    remove = json.loads(request.form["remove"])

    manageCollection(wordids, remove)

    # add any words that are not in collection

    return jsonify(
        session=getCollection()
    )


@ user_blueprint.route("/ajax_clear", methods=["POST"])
# Receives changes from user and makes changes in session
def ajax_clear():

    session["collection"] = []
    print("User cleared collection")
    return jsonify(
        session=getCollection()
    )
