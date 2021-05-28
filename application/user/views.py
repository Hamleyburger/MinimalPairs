from flask import Blueprint, session, request, redirect, render_template, flash, jsonify, url_for, make_response, g
import json

from pyphen import LANGUAGES
from .helpers import getCollection, json_to_ints, manageCollection, pairCollected, easyIPAtyping, stripEmpty, getSecondBest, ensure_locale
from application.models import Word, Group, Sound
from .models import User
from application import db, app
from .forms import SearchSounds, SearchMOs, toPDF_wrap
from flask_weasyprint import HTML, CSS, render_pdf
from application.content_management import da_content, en_content, Content


user_blueprint = Blueprint("user_blueprint", __name__,
                           static_folder="static", template_folder="templates")


# Set locale in application context before requests, "da" is default if no choice is stored in session
@app.before_request
def before_request_callback():

    locale = session.get("locale")
    if not locale:
        print("no locale")
        browser_lang = request.accept_languages.best_match(
            app.config["LANGUAGES"])
        session["locale"] = browser_lang


@app.after_request
def after_request_callback(response):

    # print stuff here for debugging

    return response


@user_blueprint.route("/", methods=["GET"], defaults={"locale": ""})
@user_blueprint.route("/<locale>", methods=["GET"], defaults={"locale": f"{en_content['locale_code']}"})
@user_blueprint.route("/<locale>", methods=["GET"], defaults={"locale": f"{da_content['locale_code']}"})
@ensure_locale
def index(locale):
    """ cute front page """

    return render_template("index.html")


@user_blueprint.route("/lukmigind", methods=["GET", "POST"])
def adminLogin():
    """login for admin (user must know URL and no option of registering or feedback)"""

    return redirect(url_for('user.login'))


@user_blueprint.route(f"/<locale>/{en_content['url_wordinfo']}/<word_id>", methods=["GET"], defaults={"locale": f"{en_content['locale_code']}"})
@user_blueprint.route(f"/<locale>/{da_content['url_wordinfo']}/<word_id>", methods=["GET"], defaults={"locale": f"{da_content['locale_code']}"})
@ensure_locale
def wordinfo(word_id, locale):

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
        return redirect(url_for("user_blueprint.index", locale=session["locale"]))


@user_blueprint.route("/<locale>/sound-search", methods=["GET", "POST"], defaults={"locale": "en"})
@user_blueprint.route("/<locale>/find-kontraster", methods=["GET", "POST"], defaults={"locale": "da"})
@ensure_locale
def contrasts(locale):

    # remove Pair from imports?
    # Get sounds with POST

    pairSearchForm = SearchSounds()
    MOSearchForm = SearchMOs()

    pairs = []  # Pairs resulting from search
    MOsets = []  # MOs exact matches
    MOsets2 = []  # MOs partial matches
    renderedids = []  # ids on user's screen
    collectedAll = True  # For accurate button condition on reload
    collectedPairs = []  # For accurate button condition on reload
    MOmode = False  # Show MO form when user last searched for MOs
    searched = False

    if request.method == "POST":
        if (request.form["searchBtn"] == "pair") and pairSearchForm.validate_on_submit():

            searched = True

            # Easy keyboard typing enabled:
            inputSound1 = easyIPAtyping(pairSearchForm.sound1.data)
            inputSound2 = easyIPAtyping(pairSearchForm.sound2.data)

            sound1 = Sound.get(inputSound1)
            pairs = sound1.getContrasts(inputSound2)

            # Make a lists of ids rendered and in collection for comparison
            for pair in pairs:
                idlist = [pair.w1.id, pair.w2.id]
                renderedids.extend(idlist)
                if pairCollected(pair):
                    collectedPairs.extend([pair.id])

        else:
            print("error in pair form: ")
            print(pairSearchForm.errors)

        if request.form["searchBtn"] == "MO":
            MOmode = True
            if MOSearchForm.validate_on_submit():
                print("MOsearchform validated")

                searched = True

                # Convert common typos to what user actually meant
                inputSound1 = easyIPAtyping(MOSearchForm.sound1.data)
                inputList = [
                    easyIPAtyping(MOSearchForm.sound2.data),
                    easyIPAtyping(MOSearchForm.sound3.data),
                    easyIPAtyping(MOSearchForm.sound4.data),
                    easyIPAtyping(MOSearchForm.sound5.data)]

                # Ignore spaces that user left blank
                MOsounds = stripEmpty(inputList)

                # Search database for exact and partial matches
                sound1 = Sound.get(inputSound1)
                MOsets = sound1.getMOPairs(MOsounds)
                MOsets2 = getSecondBest(sound1, MOsounds, MOsets)

                # add each word id to list from every MO and strip duplicates using set
                idList = [id for MO in MOsets +
                          MOsets2 for pair in MO for id in [pair.w1.id, pair.w2.id]]
                renderedids = list(set(idList))

            else:
                print("MO search form error")
                print(MOSearchForm.errors)

        # Check if user has collected all rendered words (for toggling "remove all button")
        for id in list(renderedids):
            if id not in getCollection():
                collectedAll = False

    renderedids = json.dumps(renderedids)

    return render_template("contrasts.html",
                           pairs=pairs,
                           form=pairSearchForm,
                           form2=MOSearchForm,
                           renderedids=renderedids,
                           collectedAll=collectedAll,
                           collectedPairs=collectedPairs,
                           MOsets=MOsets,
                           MOsets2=MOsets2,
                           MOmode=MOmode,
                           searched=searched)


@user_blueprint.route("/<locale>/collection", methods=["GET", "POST"], defaults={"locale": "en"})
@user_blueprint.route("/<locale>/samling", methods=["GET", "POST"], defaults={"locale": "da"})
@ensure_locale
def collection(locale):

    form = toPDF_wrap(locale)()

    print(request.method)
    collection = []
    # Get pairs from session object
    if session.get("collection"):
        print("there's a collection")
        id_collection = session["collection"]

        for id in id_collection:
            collection.append(Word.query.get(int(id)))

    if request.method == "POST":
        print("**************************************post colle")
        if getCollection():
            if form.validate_on_submit():
                # Background file name is defined in the declaration of wtf choices in forms.py
                bgfilename = form.background.data
                template = render_template("mypdf.html", collection=collection)
                html = HTML(string=template)
                # This bit of CSS is dynamically generated, the rest is hard coded in the template
                css = CSS(
                    string='@page :left { background-image: url(/static/permaimages/' + bgfilename + '.svg);}')

                return render_pdf(html, stylesheets=[css])

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

    print("word ids: " + str(wordids))
    print("remove is " + str(remove))

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


@ user_blueprint.route("/ajax_change_language/<newlocale>", methods=["GET", "POST"])
# Receives changes from user and makes changes in session
def change_language(newlocale):
    print(request.referrer)

    if newlocale in app.config["LANGUAGES"]:
        print("lang exists")
        session["locale"] = newlocale
        session["force_session_lang"] = True
    else:
        print("lang bad: {}".format(newlocale))

    return redirect(request.referrer)
