from flask import Blueprint, session, request, redirect, render_template, flash, jsonify, url_for, make_response, g, abort, send_from_directory
import json
from user_agents import parse

from pyphen import LANGUAGES
from .helpers import getCollection, get_word_collection, json_to_ints, manageCollection, pairCollected, easyIPAtyping, stripEmpty, getSecondBest, ensure_locale, custom_images_in_collection, count_as_used, hasimage, order_MOsets_by_image, refresh_session_news
import random
from application.models import Word, Group, Sound, SearchedPair
from .models import User, Userimage
from ..admin.models import News
from application import db, app
from .forms import SearchSounds, SearchMOs, toPDF_wrap
from flask_weasyprint import HTML, CSS, render_pdf
from application.content_management import da_content, en_content, Content
from application.admin.filehelpers import validate_image
import os
from werkzeug.utils import secure_filename
import sentry_sdk



user_blueprint = Blueprint("user_blueprint", __name__,
                           static_folder="static", template_folder="templates")


# Set locale in application context before requests, "da" is default if no choice is stored in session
@app.before_request
def before_request_callback():

    locale = session.get("locale")
    g.locale = session.get("locale")
    if not locale:
        print("\nNo locale in session\n")
        print(request.headers.get('User-Agent'))
        browser_lang = request.accept_languages.best_match(
            app.config["LANGUAGES"])

        session["locale"] = browser_lang
        g.locale = browser_lang
        if not browser_lang:
            session["locale"] = "da"
            g.locale = "da"
        print("session locale set before request: {}".format(session["locale"]))

    if not session.get("userimages"):
        session["userimages"] = {}

    if not session.get("manifest"):
        useragent = parse(request.user_agent.string)
        browser = useragent.browser.family.lower()
        if browser == "safari":
            print("safari")
            session["manifest"] = "apple/manifest.webmanifest"
        else:
            session["manifest"] = "manifest.webmanifest"

    if not session.get("collection"):
        if app.config["DEBUG"]:
            session["collection"] = []
        else:
            session["collection"] = []

    if not session.get("news"):
        session["news"] = refresh_session_news()


@app.after_request
def after_request_callback(response):

    # print stuff here for debugging

    return response


@user_blueprint.route("/", methods=["GET"])
@ensure_locale
def index(locale):
    """ cute front page """

    return render_template("index.html")


@user_blueprint.route("/lukmigind/", methods=["GET", "POST"])
def adminLogin():
    """login for admin (user must know URL and no option of registering or feedback)"""
    
    return redirect(url_for('user.login'))


@user_blueprint.route(f"/info-om-ord/<word_id>/", methods=["GET"])
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
            'static', filename='images/thumbnails/' + word.image.name)))

        groups = word.groups

        return render_template("wordinfo.html", word=word, pairLists=pairLists, MOsets=MOsets, groups=groups)
    else:
        abort(404)



@user_blueprint.route("/find-kontraster/", methods=["GET", "POST"])
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
    sound1 = None
    sound2 = None

    if request.method == "POST":
        if (request.form["searchBtn"] == "pair"):
            searched = True
            if pairSearchForm.validate_on_submit():

                # Easy keyboard typing enabled:
                inputSound1 = easyIPAtyping(pairSearchForm.sound1.data)
                inputSound2 = easyIPAtyping(pairSearchForm.sound2.data)

                sound1 = Sound.get(inputSound1)
                if inputSound2 == "*":
                    sound2 = "*"
                else:
                    sound2 = Sound.get(inputSound2)
                pairs = sound1.getContrasts(inputSound2)
                SearchedPair.add(inputSound1, inputSound2, len(pairs))

                pairs_with_images = []
                pairs_without_images = []

                # Sort pair list so pairs with images come on top
                for pair in pairs:
                    if hasimage(pair):
                        pairs_with_images.append(pair)
                    else:
                        pairs_without_images.append(pair)
                pairs = pairs_with_images + pairs_without_images


                # Make a lists of ids rendered to determine if they're in collection
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
            searched = True
            if MOSearchForm.validate_on_submit():
                print("MOsearchform validated")


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
                print("Getting MO sets...")
                MOsets = sound1.getMOPairs(MOsounds)
                MOsets = order_MOsets_by_image(MOsets)
                print("Getting second best MO sets...")
                MOsets2 = getSecondBest(sound1, MOsounds, MOsets)
                MOsets2 = order_MOsets_by_image(MOsets2)

                for inputSound2 in MOsounds:
                    SearchedPair.add(inputSound1, inputSound2)

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
                           sound1=sound1,
                           sound2=sound2,
                           form=pairSearchForm,
                           form2=MOSearchForm,
                           renderedids=renderedids,
                           collectedAll=collectedAll,
                           collectedPairs=collectedPairs,
                           MOsets=MOsets,
                           MOsets2=MOsets2,
                           MOmode=MOmode,
                           searched=searched)


@user_blueprint.route("/samling/", methods=["GET", "POST"])
@ensure_locale
def collection(locale):

    form = toPDF_wrap(locale)()
    print(request.method)
    collection_ids = getCollection()
    collection = []
    custom_image_ids = []

    # Retrieve pair objects from session ids
    for id in collection_ids:
        collection.append(Word.query.get(int(id)))
    custom_image_ids = custom_images_in_collection(collection)

    # POST request for basic word card PDF (other pdfs are generated and served with ajax: see pdf_maker_script.js and ajax_get_boardgame_filenames() here )
    if request.method == "POST":
        if getCollection():
            if form.validate_on_submit():
                # Background file name is defined in the declaration of wtf choices in forms.py
                bgfilename = form.background.data
                template = render_template("mypdf.html", collection=collection)
                html = HTML(string=template, base_url=request.base_url)

                # This bit of CSS is dynamically generated, the rest is hard coded in the template
                css = CSS(
                    string='@page :left { background-image: url(/static/permaimages/' + bgfilename + '.png);}')
                
                count_as_used(collection_ids)

                return render_pdf(html, stylesheets=[css])

    return render_template("collection.html", collection=collection, form=form)


@ user_blueprint.route("/ajax_add2collection/", methods=["POST"])
# Receives changes from user and makes changes in session
def ajax_add2collection():

    print("add to collection with ajax")
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


@ user_blueprint.route("/ajax_remove_from_collection/", methods=["POST"])
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


@ user_blueprint.route("/ajax_collect_many/", methods=["POST"])
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


@ user_blueprint.route("/ajax_clear/", methods=["POST"])
# Receives changes from user and makes changes in session
def ajax_clear():

    session["collection"] = []
    print("User cleared collection")
    return jsonify(
        session=getCollection()
    )


@ user_blueprint.route("/ajax_change_language/<newlocale>/", methods=["GET", "POST"])
# Receives changes from user and makes changes in session
def change_language(newlocale):

    if newlocale in app.config["LANGUAGES"]:
        print("clicked valid lang button: {}".format(newlocale))
        session["locale"] = newlocale
        session["force_session_lang"] = True
    else:
        print("lang bad: {}".format(newlocale))

    print("redirect request referrer: {}".format(request.referrer))
    print("endpoint: {}".format(request.endpoint))
    redirect_url = request.referrer
    if redirect_url == None:
        redirect_url = url_for('user_blueprint.index', locale=newlocale)
    return redirect(redirect_url)


@ user_blueprint.route("/ajax_upload_image/", methods=["POST"])
# For user to upload image to be cropped
def upload_image():

    if request.files.get("file"):
        file = request.files["file"]

        print("checking image: {}".format(file.filename))
        try:
            validate_image(file)
            wordid = request.form.get("upload_word_id")
            private_url = Userimage.store(file, wordid)
            print("returned to upload_image")
            return jsonify({'path': private_url})

        except Exception as e:
            print(e)
            return jsonify({'error': 'There was a problem uploading the image.'})
    return jsonify({'error': 'Missing file'})


@ user_blueprint.route("/ajax_validate_image/", methods=["POST"])
# For validating the image with python
def validate_browser_image():

    if request.files.get("image"):
        file = request.files["image"]

        print("validating image: {}".format(file.filename))
        try:
            validate_image(file, temp=True)
            print("validated, returning True")
            print(jsonify({'valid': True}))
            return jsonify({'valid': True})

        except Exception as e:
            print(e)
            return jsonify({'error': str(e), 'valid': False})

    return jsonify({'error': 'Missing file'})


@ user_blueprint.route("/ajax_duplicate_in_collection/", methods=["POST"])
# Receives changes from user and makes changes in session
def ajax_duplicate_in_collection():

    print("you wanna duplicate a word?")
    word_id = int(request.form["id"])
    word = Word.query.get(int(word_id))
    if word:
        print(word)
        session["collection"].append(word_id)

    return jsonify(
        session=getCollection()
    )

@ user_blueprint.route("/ajax_get_boardgame_filenames/", methods=["POST"])
# Receives changes from user (required number of words/images) and makes changes in session ()
def ajax_get_boardgame_filenames():

    ids_words_paths = []
    words = get_word_collection()
    number_of_words = len(words)

    # See how many duplicates are required to fill word count and add them to "words" (in front end - session remains unchanged)
    if number_of_words == 0:
        return "no words"
    words_needed = (int(request.form.get("count")))
    print("words needed: {}".format(words_needed))
    duplicates_needed = words_needed - len(words)
    if duplicates_needed > 0:
        for i in range(duplicates_needed):
            j = i % number_of_words
            words.append(words[j])
    elif duplicates_needed < 0:
        excess = duplicates_needed * -1
        for num in range(excess):
            print("popping word: {}".format(words[-1]))
            words.pop()
        print(duplicates_needed*-1)
        print("need to kick words")
    
    print(len(words))
    print(words)
    #random.shuffle(words)

    # Create JSON objects from all words, both with custom user images and originals
    for word in words:
        # custom user images
        if word.id in session["userimages"]: 
            ids_words_paths.append(
            {   "id": word.id,
                "word": word.word,
                "path": session["userimages"][word.id]
            }
            )
        # originals
        else: 
            ids_words_paths.append(
            {
                "id": word.id,
                "word": word.word,
                "path": "images/" + word.image.name
            }
            )

    json_words = json.dumps(ids_words_paths, ensure_ascii=False)
    session["pdf_wiz_word_list"] = ids_words_paths

    return json_words

