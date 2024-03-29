from flask import g, Blueprint, session, request, redirect, render_template, jsonify, url_for, g, abort
from flask_login import current_user
import json
from user_agents import parse

from pyphen import LANGUAGES
from .helpers import getCollection, get_word_collection, json_to_ints, manageCollection, pairCollected, stripEmpty, ensure_locale, count_as_used, order_MOsets_by_image, refresh_session_news
from application.models import Word, Sound, SearchedPair
from .models import Userimage
from ..admin.models import News
from application import db, app, mail
from .forms import SearchSounds, SearchMOs, toPDF_wrap, contactForm
from flask_weasyprint import HTML, CSS, render_pdf
from application.content_management import Content
from application.admin.filehelpers import validate_image
import stripe
from flask_mail import Message
import datetime
import time




user_blueprint = Blueprint("user_blueprint", __name__,
                           static_folder="static", template_folder="templates")


# Set locale in application context before requests, "da" is default if no choice is stored in session
@app.before_request
def before_request_callback():

    locale = session.get("locale")
    g.locale = session.get("locale")

    if not locale:
        print("\nNo locale in session. Getting locale from user agent.\n")
        print(request.headers.get('User-Agent'))
        browser_lang = request.accept_languages.best_match(
            app.config["LANGUAGES"])

        session["locale"] = browser_lang
        g.locale = browser_lang
        if not browser_lang:
            print("No locale from user agent. Defaulting to da")
            session["locale"] = "da"
            g.locale = "da"


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

    if not session.get("news_last_refreshed"):
        refresh_session_news()
    if datetime.datetime.now() - session["news_last_refreshed"] > datetime.timedelta(minutes=15):
        refresh_session_news()



@app.after_request
def after_request_callback(response):
    # request_time = session.get("before_request_time")
    # if request_time:
    #     print("Request took {} s".format(time.time() - request_time))
    return response


@user_blueprint.route("/", methods=["GET"])
@ensure_locale
def index(locale):

    """ cute front page """

    db.session.commit()
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

        MOsets = word.get_full_MOsets()
        for x in MOsets:
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


    pairSearchForm = SearchSounds()
    MOSearchForm = SearchMOs()

    # Pagination check variables
    pairSearch = False # Only pairs are relevant for pagination
    oldSearch = False

    # Search and display variables
    pairs = []  # Pairs resulting from search
    MOsets = []  # MOs exact matches
    MOsets2 = []  # MOs partial matches
    renderedids = []  # ids on user's screen
    collectedAll = True  # For accurate button condition on reload
    collectedPairs = []  # For accurate button condition on reload
    MOmode = False  # Show MO form when user last searched for MOs
    searched = False
    sound1_object = None
    sound2_object = None
    searched_sounds_list = ["", "", "", "", ""] # For user feedback on front end



    # Figure out whether to get search query outside form validation
    if not request.args.get("page"):
        session.pop("latest_sound_search", None)
    elif session.get("latest_sound_search"):
        oldSearch = True
        if len(session["latest_sound_search"]) == 2:
            pairSearch = True
    


    if request.method == "POST":
        
        if (request.form["searchBtn"] == "pair"):

            searched = True

            if pairSearchForm.validate_on_submit():

                pairSearch = True
                
                # Get all necessary data having to do with when the form is submitted:
                sound1_str = pairSearchForm.sound1.data
                sound2_str = pairSearchForm.sound2.data
                sound1_object = Sound.get(sound1_str)
                sound2_object = Sound.get(sound2_str)

                session["latest_sound_search"] = [sound1_object.id, sound2_object.id]


            else:
                print("error in pair form: ")
                print(pairSearchForm.errors)
                for field, errormsg in pairSearchForm.errors.items():
                    for msg in errormsg:
                        g.errorfeedback = msg
                        if "csrf" in msg.lower():
                            g.errorfeedback = Content()["unknown_or_csrf_error"]


        if request.form["searchBtn"] == "MO":
            MOmode = True
            searched = True
            if MOSearchForm.validate_on_submit():

                # Convert common typos to what user actually meant
                sound1_str = MOSearchForm.sound1.data
                inputList = [
                    MOSearchForm.sound2.data,
                    MOSearchForm.sound3.data,
                    MOSearchForm.sound4.data,
                    MOSearchForm.sound5.data]

                # Ignore spaces that user left blank
                MOsounds = stripEmpty(inputList)

                # Search database for exact and partial matches
                sound1_object = Sound.get(sound1_str)
                searched_sounds_list[0] = sound1_object.sound

                for i, sound in enumerate(MOsounds):
                    append_sound = Sound.get(sound)
                    searched_sounds_list[i+1] = append_sound.sound


                print("Getting best and 2nd best MO sets...")
                all_MOsets = sound1_object.getMOPairs(MOsounds)
                for MOset in all_MOsets:
                    if len(MOset) == len(MOsounds):
                        MOsets.append(MOset)
                    else:
                        MOsets2.append(MOset)

                MOsets = order_MOsets_by_image(MOsets)
                MOsets2 = order_MOsets_by_image(MOsets2)
                MOsets2 = sorted(MOsets2, key=len, reverse=True)


                if not (current_user.is_authenticated and current_user.has_role("Admin")):
                    for sound2_str in MOsounds:
                        SearchedPair.add(sound1_str, sound2_str)

                # add each word id to list from every MO and strip duplicates using set
                idList = [id for MO in MOsets +
                          MOsets2 for pair in MO for id in [pair.w1.id, pair.w2.id]]
                renderedids = list(set(idList))

            else:
                print("MO search form error")
                print(MOSearchForm.errors)
                for field, errormsg in MOSearchForm.errors.items():
                    for msg in errormsg:
                        g.errorfeedback = msg
                        if "csrf" in msg.lower():
                            g.errorfeedback = Content()["unknown_or_csrf_error"]

    if pairSearch:
        # do all pair search here so pagination object can be carried over between requests
        page = request.args.get("page", 1, type=int)
        if oldSearch:
            s1id = int(session.get("latest_sound_search")[0])
            s2id = int(session.get("latest_sound_search")[1])
            sound1_object = Sound.query.get(s1id)
            sound2_object = Sound.query.get(s2id)
            sound1_str = sound1_object.sound
            sound2_str = sound2_object.sound
   
        searched_sounds_list[0] = sound1_str
        searched_sounds_list[1] = sound2_str

        # Even with image load time taken into concideration a long search result takes much longer to load
        pairs = sound1_object.getContrasts(sound2_object, page=page, per_page=10)


        # searched_pairs only triggers for non admin users
        if not (current_user.is_authenticated and current_user.has_role("Admin")):
            if not oldSearch:
                SearchedPair.add(sound1_str, sound2_str, len(pairs.items))


        # Make a lists of ids rendered to determine if they're in collection on the front end
        for pair in pairs.items:
            idlist = [pair.w1.id, pair.w2.id]
            renderedids.extend(idlist)
            if pairCollected(pair):
                collectedPairs.extend([pair.id])
        


    # Check if user has collected all rendered words (for toggling "remove all button")
    for id in list(renderedids):
        if id not in getCollection():
            collectedAll = False #  Just to see if the ollect all button should be red or not

    renderedids = json.dumps(renderedids)


    return render_template("contrasts.html",
                           pairs=pairs,
                           sound1=sound1_object,
                           sound2=sound2_object,
                           searched_sounds_list=searched_sounds_list,
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
    choice_objects = form.choice_objects

    collection_ids = getCollection()
    collection = []


    # Retrieve pair objects from session ids
    for id in collection_ids:
        collection.append(Word.query.get(int(id)))
    

    # POST request for basic word card PDF (other pdfs are generated and served with ajax: see pdf_maker_script.js and ajax_get_boardgame_filenames() here )
    if request.method == "POST":
        if getCollection():

            if form.validate_on_submit():
                # Background file name is defined in the declaration of wtf choices in forms.py

                selected_bg = choice_objects[int(form.background.data)]
                bgfilename = selected_bg.path
                template = render_template("mypdf.html", collection=collection)
                html = HTML(string=template, base_url=request.base_url)

                # This is bad code and proves that I need to make a db table for repeat patterns
                bg_px_size = str(selected_bg.display_width)


                # This bit of CSS is dynamically generated, the rest is hard coded in the template
                css = CSS(
                    string='@page :left { background-image: url(/static/' + bgfilename + '); background-size: ' + bg_px_size + 'px;}')
                
                if not (current_user.is_authenticated and current_user.has_role("Admin")):
                    count_as_used(collection_ids)

                #return render_template("mypdf.html", collection=collection)
                return render_pdf(html, stylesheets=[css])
            else:
                for error in form.background.errors:
                    print(error)

    return render_template("collection.html", collection=collection, form=form, choice_objects=choice_objects)


@user_blueprint.route(f"/donation/", methods=["GET"])
@ensure_locale
def donation(locale):

    stripe_products = stripe.Product.search(query="metadata['type']:'donation'")

    products = []
    for product in stripe_products:

        this_product = {}
        this_price = stripe.Price.retrieve(product["default_price"])
        amount = int(this_price["unit_amount"] / 100) # comes out in øre

        this_product["id"] = product["id"]
        this_product["name"] = product["name"]
        this_product["amount"] = amount
        if product["images"]:
            this_product["image_url"] = product["images"][0]
        else:
            this_product["image_url"] = ""
    
        products.append(this_product)

    def get_amount(product):
        return int(product["amount"])
    products.sort(reverse=False, key=get_amount) # (sort function passes list item to key function automatically)

    return render_template("stripe/donation.html", products=products)


@user_blueprint.route(f"/kontakt/", methods=["GET", "POST"])
@ensure_locale
def contact(locale):

    form = contactForm()
    recaptcha_key = app.config["RECAPTCHA_PUBLIC_KEY"]
    sent = ""
    name = form.name.data
    email = form.email.data
    message = form.message.data
    if request.args.get("sent"):
        sent = request.args.get("sent")

    if request.method == "POST":
        if form.validate_on_submit():
            try:
                with app.app_context():
                    msg = Message(subject="Besked fra {}".format(name),
                                sender=email,
                                recipients=[app.config.get("EGEN_MAIL")], # replace with your email for testing
                                body="{}:\n{}".format(email, message))
                    mail.send(msg)
                sent = "yes"
                return redirect(url_for('user_blueprint.contact', sent=sent, locale=locale))
            except Exception as e:
                raise e
    
    return render_template("contact.html", form=form, recaptcha_key=recaptcha_key, sent=sent)



@user_blueprint.route(f"/tak/", methods=["GET"])
@ensure_locale
def thankyou(locale):
    session_id = request.args.get("session_id")
    text = ""
    love = None
    if session_id:

        try:
            stripe_session = stripe.checkout.Session.retrieve(session_id)
            text = Content()["text_thankyou"]
            love = True

        except Exception as e:
            print(e)
            text = Content()["text_notthankyou"]
            love = False
    else:
        text = Content()["text_notthankyou"]
        love = False

    return render_template("stripe/thankyou.html", text=text, love=love)


@user_blueprint.route(f"/betaling-annulleret/", methods=["GET"])
@ensure_locale
def cancelled(locale):

    return render_template("stripe/cancelled.html")


@ user_blueprint.route("/ajax_get_stripe_key/") # can this be made post method only?
def get_stripe_key():

    stripe_config = {"publicKey": app.config["STRIPE_PUBLIC_KEY"]}
    return jsonify(stripe_config)


@user_blueprint.route("/ajax-create-checkout-session", methods=['GET', 'POST'])
def create_checkout_session():

    success_url = url_for('user_blueprint.thankyou', _external=True) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = url_for('user_blueprint.cancelled', _external=True)

    stripe.api_key = app.config["STRIPE_SECRET_KEY"]

    try:

        product_id = request.get_json()["product_id"]
        product = stripe.Product.retrieve(product_id)
        price = stripe.Price.retrieve(product["default_price"])
        price_id = price["id"]

        # TODO: Use json to get product id and use this to get price id to create the price of donation


        # Create new Checkout Session for the order
        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        checkout_session = stripe.checkout.Session.create(
            success_url=success_url,
            cancel_url=cancel_url,
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "quantity": 1,
                    "price": price_id,
                }
            ]
        )
        print("Checkout session id: {}".format(checkout_session["id"]))
        return jsonify({"sessionId": checkout_session["id"]})
    except Exception as e:
        raise e
        return jsonify(error=str(e)), 403



@ user_blueprint.route("/ajax_add2collection/", methods=["POST"])
# Receives changes from user and makes changes in session
def ajax_add2collection():

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


@ user_blueprint.route("/change_language/<newlocale>/", methods=["GET"])
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
    duplicates_needed = words_needed - len(words)
    if duplicates_needed > 0:
        for i in range(duplicates_needed):
            j = i % number_of_words
            words.append(words[j])
    elif duplicates_needed < 0:
        excess = duplicates_needed * -1
        for num in range(excess):
            words.pop()

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





