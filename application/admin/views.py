from flask import Blueprint, session, request, redirect, render_template, flash, jsonify, url_for, json
from application.models import SearchedPair, Word, Pair, Sound, Group, PermaImage
from application.user.helpers import refresh_session_news
from .models import News# admin models
from ..user.models import Userimage 
from .forms import AddForm, AddPairForm, ChangePairForm, NewsForm, PermaimageForm
from application import db, app
from .filehelpers import store_image, configure_add_template
from flask_user import roles_required
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import os
from sqlalchemy import desc
import time

admin_blueprint = Blueprint(
    "admin_blueprint", __name__, url_prefix="/admin", static_folder="static", template_folder="templates")


@admin_blueprint.before_request
def before_request_callback():
    session["locale"] = "da"
    print("****** before request callback: session locale was set to da")


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
        artist_name = ""
        # Store image if there was one
        if request.files["image"]:
            image_name = store_image(request.files["image"])
            if form.artist.data:
                artist_name = form.artist.data

        # Add word to db and also store in session
        wordToRemember = Word.add(word=form.word.data,
                                  cue=form.cue.data, image=image_name, artist=artist_name)
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

    def get_group_index(field_id):
        """ generate classname to identify which s2 fields to autofill
        based on which groups the suggestions came from. This function is
        used in jinja template to set classes for fields for suggested partners so
        admin_scripts.js can transfer input sound1 across similar fields """

        suglists = session.get("partner_suggestion_lists")
        if suglists:
            for groupindex, suglist in enumerate(suglists):
                for id, sound, initial in suglist:
                    if int(field_id) == id:
                        return "{}".format(groupindex)
        return ""

    return render_template("add.html", form=form, pairForm=pairForm, get_group_index=get_group_index)


@ admin_blueprint.route("/change", methods=["GET", "POST"])
@roles_required('Admin')
def change():

    """ just for changing images """
    if request.method == "POST":

        if request.files:
            id = int(request.form.get("newwordid"))
            word = Word.change(id, newword=request.form.get("newword"),
                        newcue=request.form.get("newcue"), newimg=request.files["newimg"], newartist=request.form.get("newartist"))
            #news = db.session.query(News).filter_by(word=word)
            #if news:
            #    refresh_session_news()
            # But it only refreshes my own session news so no point

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
                print("valid change pair form")
                if request.form.get("submit") == "save":
                    s1 = form.s1.data
                    s2 = form.s2.data
                    word1 = pair.w1
                    word2 = pair.w2


                    db.session.delete(pair)
                    db.session.commit()
                    word1.pair(word2, s1, s2, pair.isinitial) # implement initial

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
            imagepath = None

            # Check if word is provided by checking if not None
            if word_id != None:
                word = Word.query.get(word_id)

            if form.image.data:
                print(type(form.image.data))
                filename = secure_filename(form.image.data.filename)
                static_path = app.config["STATIC_PATH"]
                news_imagepath = "/permaimages/newsimages/" + filename
                form.image.data.save(static_path + news_imagepath)
                imagepath = news_imagepath


            news = News(
                title=title,
                title_en=title_en,
                text=text,
                text_en=text_en,
                date_posted=date_posted,
                word=word,
                imagepath=imagepath
            )

            db.session.add(news)
            db.session.commit()

        else:
            for name, error in form.errors.items():
                flash(u"{}".format(str(name) + ": " + str(error[0])), "danger")

        return redirect(url_for("admin_blueprint.write_news"))
    return render_template("news.html", form=form)


@admin_blueprint.route("/add_image",  methods=["GET", "POST"])
@roles_required('Admin')
def add_image():
    form = PermaimageForm()
    repeatpatterns = db.session.query(PermaImage).filter_by(type="repeatpattern").all()

    if request.method == "POST":
        if form.validate_on_submit():
            path = PermaImage.store_and_get_path(form.image.data, "/repeatpatterns/")
            display_width = form.display_width.data
            display_name_da = form.display_name_da.data
            display_name_en = form.display_name_en.data
            repeatpattern = PermaImage(
                path=path,
                display_width = display_width,
                display_name_da = display_name_da,
                display_name_en = display_name_en,
                type = "repeatpattern"
            )
            db.session.add(repeatpattern)
            db.session.commit()
            print("returned path: {}".format(path))
            return redirect(url_for("admin_blueprint.add_image"))
        else:
            print("form error")
    return render_template("addimage.html", form=form, repeatpatterns=repeatpatterns)


@ admin_blueprint.route("/problems/", methods=["GET"])
@roles_required('Admin')
# Receives a word id and returns words in a way so client can see which pairs already exist
def problems():

    print("Updating pair image counts")
    start_time = time.time()
    allps = Pair.query.all()
    for p in allps:
        p.img_count = p.has_images()
    db.session.commit()
    print("took {} seconds\n".format(time.time() - start_time))


    print("Querying group problems")
    start_time = time.time()
    group_problems = Group.get_group_problems()
    print("took {} seconds\n".format(time.time() - start_time))

    word_problems = []
    pair_init_problems = []
    pair_samesound_problems = []
    pair_sound_validity_problems = []

    # Clean pair sounds
    print("Checking pair sounds")
    start_time = time.time()

    pairs = db.session.query(Pair).all()
    for p in pairs:
        if p.s1 not in p.sounds:
            p.sounds.append(p.s1)
        if p.s2 not in p.sounds:
            p.sounds.append(p.s2)
        if not p.sounds:
            print("pair has no sounds! {}".format(p))
    print("took {} seconds\n".format(time.time() - start_time))

    # Remove bad sounds
    print("Removing any bad sounds that might have come into database")
    start_time = time.time()
    sounds = Sound.query.all()
    for sound in sounds:
        try:
            Sound.isvalidsound(sound.sound)
        except:
            print("Sound not valid: {}".format(sound.sound))
            print("Found bad sound: {}".format(sound))
            db.session.delete(sound)
    print("took {} seconds\n".format(time.time() - start_time))

    print("Checking pairs for bad sounds")
    start_time = time.time()
    pairs = Pair.query.all()
    for pair in pairs:
        try:
            Sound.isvalidsound(pair.s1.sound)
            Sound.isvalidsound(pair.s2.sound)
        except:
            print("not valid pair sounds: {}".format(pair))
            pair_sound_validity_problems.append(pair)

    print("took {} seconds\n".format(time.time() - start_time))
    print("Checking searched_pairs for bad sounds")
    start_time = time.time()
    pairs = SearchedPair.query.all()
    for searched_pair in pairs:
        try:
            Sound.isvalidsound(searched_pair.s1)
            Sound.isvalidsound(searched_pair.s2)
        except:
            print("not valid sounds in searched_pair: {} - is deleted.".format(searched_pair))
            db.session.delete(searched_pair)

    db.session.commit()

    print("took {} seconds\n".format(time.time() - start_time))
    print("Checking for words with no pairs")
    start_time = time.time()
    for word in db.session.query(Word).all():
        if len(word.allPartners()) < 1:
            word_problems.append(word)

    print("took {} seconds\n".format(time.time() - start_time))
    print("Checking for pairs with undefined initial")
    start_time = time.time()
    uninit_pairs = db.session.query(Pair).filter_by(isinitial=None).all()
    pair_init_problems = []
    assumed_noninitial = []
    likely_initial = []
    unknown = []

    for p in uninit_pairs:
        str1 = p.w1.word
        str2 = p.w2.word
        smp1 = str1[0 : 3]
        smp2 = str2[0 : 3]
        if smp1.lower() == smp2.lower():
            print("assuming {} - {} is NOT initial".format(p.w1.word, p.w2.word))
            p.isinitial = False
            assumed_noninitial.append(p)
            db.session.commit()
        else:
            smp1b = str1[0 : 1]
            smp2b = str2[0 : 1]
            if smp1b.lower() != smp2b.lower():
                likely_initial.append(p)
            else:
                unknown.append(p)
    pair_init_problems = likely_initial + unknown

    print("took {} seconds\n".format(time.time() - start_time))
    print("Checking if any words have different pairs with same sounds")
    start_time = time.time()
    allwords = Word.query.all()
    for word in allwords:
        samesound_pairs = word.get_samesound_pairs()
        if samesound_pairs:
            pair_samesound_problems.extend(samesound_pairs)
    print("took {} seconds\n".format(time.time() - start_time))



    """ Get an overview of words without partners and groups with unmatched words """

    return render_template(
        "problems.html",
        group_problems=group_problems,
        word_problems=word_problems,
        pair_init_problems=pair_init_problems,
        assumed_noninitial=assumed_noninitial,
        pair_samesound_problems=pair_samesound_problems,
        pair_sound_validity_problems=pair_sound_validity_problems # Should not be possible
        )


@ admin_blueprint.route("/stats/", methods=["GET"])
@roles_required('Admin')
# Receives a word id and returns words in a way so client can see which pairs already exist
def stats():
    """ Get an overview of what people are searching for at what content should be added. Fill out missing info in searched_pairs """

    searched_pairs = SearchedPair.query.order_by(desc(SearchedPair.last_searched)).all()

    now = datetime.now()
    print("now is now: {}".format(now))
    month_ago = now - timedelta(days=30)
    week_ago = now - timedelta(days=7)
    day_ago = now - timedelta(hours=24)
    last_3_hours = now - timedelta(hours=3)
    print("3h ago is {}".format(last_3_hours))

    last_week = []
    last_month = []
    last_day = []
    last_3h = []
    most_popular = []

    commit = False


    for searched_pair in searched_pairs:

        # Ensure that only allowed sounds are stored in searchedpairs
        # soundobject1 = Sound.get(searched_pair.s1)
        # if searched_pair.s1 != soundobject1.sound:
        #     print("found bad sound in searchedpairs")
        #     searched_pair.s1 = soundobject1.sound
        # soundobject2 = Sound.get(searched_pair.s2)
        # if searched_pair.s2 != soundobject2.sound:
        #     print("found bad sound in searchedpairs")
        #     searched_pair.s2 = soundobject2.sound


        pairs = searched_pair.get_SP_pairs()

        if pairs:
            if searched_pair.existing_pairs != None:
                if searched_pair.existing_pairs != len(pairs):
                    searched_pair.existing_pairs = len(pairs)
            else:
                searched_pair.existing_pairs = 0
        else:
            searched_pair.existing_pairs = 0
        commit = True

        if searched_pair.s1 < searched_pair.s2:
            temps1 = searched_pair.s2
            temps2 = searched_pair.s1
            searched_pair.s1 = temps1
            searched_pair.s2 = temps2
            commit = True

        if searched_pair.times_searched:
            if searched_pair.last_searched > last_3_hours:
                last_3h.append(searched_pair)
            elif searched_pair.last_searched > day_ago:
                last_day.append(searched_pair)
            elif searched_pair.last_searched > week_ago:
                last_week.append(searched_pair)
            elif searched_pair.last_searched > month_ago:
                last_month.append(searched_pair)



    # Get stats for most used words:
    most_used_words = Word.query.order_by(desc(Word.times_used)).all()
    most_used_words_wo_images = []
    for word in most_used_words:
        if len(most_used_words_wo_images) < 20:
            if word.image.name == "default.svg":
                most_used_words_wo_images.append(word)
        else:
            break
    most_used_words = most_used_words[:32]


    db.session.commit()

    last_month = [last_month[i:i+40] for i in range(0, len(last_month), 40)]


    most_popular = sorted(searched_pairs, key=lambda pair: pair.times_searched, reverse=True)[0:10]



    searches_pairs = []
    for search in most_popular:

        pairs = sorted(search.get_SP_pairs(), key=lambda pair: pair.has_images(), reverse=True)
        searches_pairs.append((search, pairs))
    if commit:
        db.session.commit()

    # Find out when someone last did something with a user image
    lastuserimages = db.session.query(Userimage).order_by(desc(Userimage.created_date)).all()
    for img in lastuserimages:
        print(img)
        print(img.staticpath)


    return render_template(
        "stats.html",
        last_3h=last_3h,
        last_day=last_day,
        last_week=last_week,
        last_month=last_month,
        searches_pairs=searches_pairs,
        most_used_words=most_used_words,
        most_used_words_wo_images=most_used_words_wo_images,
        userimgs=lastuserimages
        )


@ admin_blueprint.route("/ajax_delete_group/", methods=["POST"])
@roles_required('Admin')
# Receives changes from user and makes changes in database
def ajax_delete_group():

    group_id = int(request.form["group_id"])
    group_to_delete = Group.query.get(group_id)
    print("Deleting group {}".format(group_id))
    print(group_to_delete)
    try:
        group_to_delete.remove()
        db.session.commit()
    except Exception as e:
        return jsonify(
            message=str(e)
        )

    return jsonify(
        message="ok"
    )


@ admin_blueprint.route("/ajax_remove_from_group/", methods=["POST"])
@roles_required('Admin')
# Receives changes from user and makes changes in database
def ajax_remove_from_group():

    group_id = int(request.form["group_id"])
    obj_id = int(request.form["obj_id"])
    obj_type = request.form["obj_type"]
    group = Group.query.get(group_id)


    try:
        if obj_type == "badword":
            word = Word.query.get(obj_id)
            print("Deleting word {} from {}".format(word, group))
            group.members.remove(word)
        elif obj_type == "badpair":
            pair = Pair.query.get(obj_id)
            print("Deleting pair {} from {}".format(pair, group))
            group.pairs.remove(pair)
        else:
            raise Exception("I don't if I should delete word or pair. Object type either invalid or missing")
        db.session.commit()

    except Exception as e:
        return jsonify(
            message=str(e)
        )

    return jsonify(
        message="ok"
    )


@ admin_blueprint.route("/ajax_set_initial/", methods=["POST"])
@roles_required('Admin')
# Receives changes from user and makes changes in database
def ajax_set_initial():

    obj_id = int(request.form["obj_id"])
    obj_type = request.form["obj_type"]
    typed_value = request.form["typed_value"]
    group = None
    pair = None
    initial = None

    if obj_type == "group":
        group = Group.query.get(obj_id)
    elif obj_type == "pair":
        pair = Pair.query.get(obj_id)

    if typed_value == "y":
        initial = True
    elif typed_value == "n":
        initial = False


    try:
        if initial != None:
            if group:
                print("setting group and pairs initial to {}".format(initial))
                group.isinitial = initial
                for setpair in group.pairs:
                    setpair.isinitial = initial
                db.session.commit()

            elif pair:
                print("setting pair {} initial to {}".format(pair, initial))
                pair.isinitial = initial
                db.session.commit()
            else:
                raise Exception("No object type received.")
        else:
            raise Exception("Must provide 'y' og 'n' value to set .initial")

    except Exception as e:
        return jsonify(
            message=str(e)
        )

    return jsonify(
        message="ok"
    )


@ admin_blueprint.route("/ajax_word_changer/", methods=["POST"])
@roles_required('Admin')
# Receives changes from user and makes changes in database
def ajax_change():

    newword = request.form["newword"]
    newcue = request.form["newcue"]
    newimg = request.form["newimg"]
    word_id = request.form["id"]
    newartist = request.form.get("newartist")

    word = Word.change(id=int(word_id), newword=newword,
                       newcue=newcue, newimg=newimg, newartist=newartist)

    return jsonify(
        id=word.id,
        newword=word.word,
        newcue=word.cue,
        newimg=word.image.name,
        newartist=word.image.artist
    )


@ admin_blueprint.route("/ajax_word_delete/", methods=["POST"])
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


@ admin_blueprint.route("/ajax_possible_pairs/", methods=["POST"])
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


@ admin_blueprint.route("/ajax_suggested_pairs/", methods=["POST"])
@roles_required('Admin')
# Receives a word id and returns words in a way so client can see which pairs already exist
def ajax_suggested_pairs():
    """ Based on groups suggests words to pair """

    all_indexes = json.loads(request.form.get("all_indexes"))
    chosen_ids = json.loads(request.form.get("chosen_ids"))
    word1_id = int(request.form.get("word1_id"))
    word1 = Word.query.get(word1_id)
    partner_suggestions = [] # List of tuples
    suggestion_indexes = [] # Indexes are for converting ids back to elements in list in current chosen-field in the browser
    suggested_ids = [] # Only ids from suggested words
    suggested_inits = []

    if all_indexes and chosen_ids:

        partner_suggestion_lists = word1.get_partner_suggestions(chosen_ids)

        for index, id in enumerate(all_indexes):
            for suglist in partner_suggestion_lists:
                for suggested_id, suggested_sound, suggested_init in suglist:
                    if id == suggested_id:
                        suggestion_indexes.append(index)
                        suggested_ids.append(id)

        session["partner_suggestion_lists"] = partner_suggestion_lists

        return jsonify(
            suggestion_indexes=suggestion_indexes,
            suggested_ids=suggested_ids
        )

    return jsonify(
        error="something went wrong"
    )


@ admin_blueprint.route("/ajax_delete_news/", methods=["POST"])
@roles_required('Admin')
# Receives a word id and returns words in a way so client can see which pairs already exist
def ajax_delete_news():
    """ Receive id and delete news. Update session. Send ok back """

    try:

        news_id = json.loads(request.form.get("news_id"))
        news_to_delete = News.query.get(int(news_id))
        print("deleting news: {}".format(news_to_delete))
        img_to_delete = news_to_delete.imagepath
        if img_to_delete:
            os.remove(app.config["STATIC_PATH"] + img_to_delete)
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


