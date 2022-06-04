from flask import Blueprint, session, request, redirect, render_template, flash, jsonify, url_for, json
from application.models import Word, Pair, Sound, Group
from application.user.helpers import refresh_session_news
from .models import News # admin models
from .forms import AddForm, AddPairForm, ChangePairForm, NewsForm
from application import db, app
from .filehelpers import store_image, configure_add_template
from flask_user import roles_required
from datetime import datetime

admin_blueprint = Blueprint(
    "admin_blueprint", __name__, url_prefix="/admin", static_folder="static", template_folder="templates")


@admin_blueprint.before_request
def before_request_callback():
    session["locale"] = "en"
    print("****** session locale was set to english")


@admin_blueprint.route("/add", methods=["GET"])
@roles_required('Admin')
def add():
    """admin stuff"""
    Group.updateMeta()
    form = AddForm()
    pairForm = AddPairForm()
    configure_add_template(pairForm, db.session.query(Word).all())

    wordToRemember_id = session.get("word1") if session.get("word1") else None
    pairForm.word1.default = wordToRemember_id
    pairForm.process()

    return render_template("add.html", form=form, pairForm=pairForm)


@admin_blueprint.route("/add_word", methods=["POST"])
@roles_required('Admin')
def add_word():
    form = AddForm()
    pairForm = AddPairForm()
    configure_add_template(pairForm, db.session.query(Word).all())

    if form.cancel.data:
        return redirect(url_for("admin_blueprint.add"))

    if form.validate_on_submit():
        print("was valid")

        # first store word without image
        image_name = None
        # Store image if there was one
        if request.files["image"]:
            image_name = store_image(request.files["image"])

        # Add word to db and also store in session
        wordToRemember = Word.add(word=form.word.data,
                                  cue=form.cue.data, image=image_name)
        session["word1"] = str(wordToRemember.id)

        db.session.commit()

        return redirect(url_for("admin_blueprint.add"))
    else:
        for name, error in form.errors.items():
            flash(u"{}".format(str(name) + ": " + str(error[0])), "danger")

    return render_template("add.html", form=form, pairForm=pairForm)


@ admin_blueprint.route("/add_pairs", methods=["POST"])
@roles_required('Admin')
def add_pairs():
    form = AddForm()
    pairForm = AddPairForm()
    configure_add_template(pairForm, db.session.query(Word).all())

    if pairForm.validate_on_submit():
        print("pairform valid")
        db.session.commit()
        return redirect(url_for("admin_blueprint.add"))
    else:
        print(pairForm.errors)

    return render_template("add.html", form=form, pairForm=pairForm)


@ admin_blueprint.route("/change", methods=["GET", "POST"])
@roles_required('Admin')
def change():
    if request.method == "POST":

        if request.files:
            id = int(request.form.get("newwordid"))
            Word.change(id, newword=request.form.get("newword"),
                        newcue=request.form.get("newcue"), newimg=request.files["newimg"])

        return redirect(request.url)

        # print(word)
    words = Word.query.all()
    return render_template("change.html", words=words)

@ admin_blueprint.route("/change/pairs", methods=["GET", "POST"])
@roles_required('Admin')
def change_pairs():
    form = ChangePairForm()
    if request.args.get("word"):
        word_id = request.args.get('word')
        word = Word.query.get(int(word_id))
        pairs = word.getPairs()

        if request.method == "POST":

            pair_id = form.pair_id.data
            pair = Pair.query.get(int(pair_id))

            if form.validate():
                if request.form.get("submit") == "save":
                    s1 = form.s1.data
                    s2 = form.s2.data
                    word1 = pair.w1
                    word2 = pair.w2
                    word1.pair(word2, s1, s2)

                elif request.form.get("submit") == "delete":
                    db.session.delete(pair)
                    db.session.commit()
            else:
                print(form.errors)
                flash("Form invalid")

        pairs = word.getPairs()
        return render_template("change_pairs.html", word=word, pairs=pairs, form=form)
    else:
        flash("the requested URL needs the word argument: ?word=<id>")
        return redirect(url_for("admin_blueprint.change", form=form))




@ admin_blueprint.route("/upload_image", methods=["POST"])
@roles_required('Admin')
def upload_image():
    return "Image uploaded"


@admin_blueprint.route("/write_news",  methods=["GET", "POST"])
@roles_required('Admin')
def write_news():
    session["news"] = refresh_session_news()
    form = NewsForm()
    if request.method == "POST":
        if form.validate_on_submit():

            if form.submit_news.data:
                print("submit news pressed")
            else:
                print("submit news not pressed huh!")


            title = request.form.get("title")
            title_en = request.form.get("title_en")
            text = request.form.get("text")
            text_en = request.form.get("text_en")
            date_posted_input = request.form.get("date_posted")
            date_posted = datetime.strptime(date_posted_input, '%Y-%m-%d %H:%M:%S')
            word_id = request.form.get("word")
            word = None
            # Check if word is provided by checking if not None
            if word_id != None:
                word = Word.query.get(word_id)

            if title:
                print("title exists")

            if title_en:
                print("title_en exists")

            if text:
                print("text exists")

            if text_en:
                print("text_en exists")
            
            news = News(
                title=title,
                title_en=title_en,
                text=text,
                text_en=text_en,
                date_posted=date_posted,
                word=word
            )

            db.session.add(news)
            db.session.commit()

        else:
            for name, error in form.errors.items():
                flash(u"{}".format(str(name) + ": " + str(error[0])), "danger")

        return redirect(url_for("admin_blueprint.write_news"))
    return render_template("news.html", form=form)


@ admin_blueprint.route("/ajax_word_changer", methods=["POST"])
@roles_required('Admin')
# Receives changes from user and makes changes in database
def ajax_change():
    print("running ajax")
    newword = request.form["newword"]
    newcue = request.form["newcue"]
    newimg = request.form["newimg"]
    word_id = request.form["id"]

    print("id: {}, new word: {}, new cue: {}, new image: {}".format(
        word_id, newword, newcue, newimg))

    word = Word.change(id=int(word_id), newword=newword,
                       newcue=newcue, newimg=newimg)

    return jsonify(
        id=word.id,
        newword=word.word,
        newcue=word.cue,
        newimg=word.image.name
    )


@ admin_blueprint.route("/ajax_word_delete", methods=["POST"])
@roles_required('Admin')
# Receives changes from user and makes changes in database
def ajax_delete():

    print("getting word id with ajax")
    word_id = request.form["id"]
    word = Word.query.get(int(word_id))
    print("Deleting: " + str(word.word))
    word.remove()

    return jsonify(
        id=word.id
    )


@ admin_blueprint.route("/ajax_possible_pairs", methods=["POST"])
@roles_required('Admin')
def ajax_possible_pairs():
    """ Greys out/inactivates already paired words and keeps the rest black/choosable/possible.\n
    Not to be confused with 'suggested pairs' """
    # Receives a word id and returns words in a way so client can see which pairs already exist
    word_id = request.form["id"]
    word = Word.query.get(int(word_id))
    partners = word.allPartners()
    partner_ids = []
    for partner in partners:
        partner_ids.append(partner.id)
        partner_ids.append(word.id)
    return jsonify(
        id=partner_ids
    )


@ admin_blueprint.route("/ajax_suggested_pairs", methods=["POST"])
@roles_required('Admin')
# Receives a word id and returns words in a way so client can see which pairs already exist
def ajax_suggested_pairs():
    """ Based on groups suggests words to pair """

    word1 = Word.query.get(1)
    all_indexes = json.loads(request.form.get("all_indexes"))
    chosen_ids = json.loads(request.form.get("chosen_ids"))
    #chosen_ids = []
    suggested_ids = []
    suggested_indexes = []

    if all_indexes and chosen_ids:

        suggested_ids = word1.get_partner_suggestions(chosen_ids)

        for index, id in enumerate(all_indexes):
            if id in suggested_ids:
                suggested_indexes.append(index)

        print("suggested indexes: {}".format(suggested_indexes))
        return jsonify(
            suggested_indexes=suggested_indexes,
            suggested_ids=suggested_ids
        )

    return jsonify(
        error="something went wrong"
    )



@ admin_blueprint.route("/ajax_delete_news", methods=["POST"])
@roles_required('Admin')
# Receives a word id and returns words in a way so client can see which pairs already exist
def ajax_delete_news():
    """ Receive id and delete news. Update session. Send ok back """

    try:

        news_id = json.loads(request.form.get("news_id"))
        news_to_delete = News.query.get(int(news_id))
        print("deleting news: {}".format(news_to_delete))
        db.session.delete(news_to_delete)
        db.session.commit()
        session["news"] = refresh_session_news()
        
        return jsonify(
            message="ok"
        )
    except Exception as e:
        return jsonify(
            message="Server error in ajax_delete_news: {}".format(e)
        )


