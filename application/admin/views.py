from flask import Blueprint, session, request, redirect, render_template, flash, jsonify, url_for
# from .helpers import clearSessionExcept
from application.models import Word, Pair, Sound, Group
from .forms import AddForm, AddPairForm
from application import db, app
from .helpers import store_image
from flask_user import roles_required

admin_blueprint = Blueprint(
    "admin_blueprint", __name__, url_prefix="/admin", static_folder="static", template_folder="templates")


@admin_blueprint.route("/add", methods=["GET"])
@roles_required('Admin')
def add():
    """admin stuff"""
    Group.updateMeta()
    session.pop("homonyms", None)
    session.pop("existingPairs", None)
    form = AddForm()
    pairForm = AddPairForm()
    pairForm.word1.choices = [(str(word.id), word.word + " (" + word.cue + ")")
                              for word in db.session.query(Word).all()]
    pairForm.pairs.choices = [(str(word.id), word.word + " (" + word.cue + ")")
                              for word in db.session.query(Word).all()]
    wordToRemember_id = session.get("word1") if session.get("word1") else None
    pairForm.word1.default = wordToRemember_id
    pairForm.process()

    return render_template("add.html", form=form, pairForm=pairForm)


@admin_blueprint.route("/add_word", methods=["POST"])
@roles_required('Admin')
def add_word():
    session.pop("homonyms", None)
    session.pop("existingPairs", None)
    form = AddForm()
    pairForm = AddPairForm()
    pairForm.word1.choices = [(str(word.id), word.word + " (" + word.cue + ")")
                              for word in db.session.query(Word).all()]
    pairForm.pairs.choices = [(str(word.id), word.word + " (" + word.cue + ")")
                              for word in db.session.query(Word).all()]

    if form.cancel.data:
        return redirect(url_for("admin_blueprint.add"))
    if form.validate_on_submit():
        print("was valid")

        image_name = None

        if request.files["image"]:
            image_name = store_image(request.files["image"])

        if form.add.data or form.addAnyway.data:
            print("adding from view")
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
    session.pop("homonyms", None)
    session.pop("existingPairs", None)
    form = AddForm()
    pairForm = AddPairForm()
    pairForm.word1.choices = [(str(word.id), word.word + " (" + word.cue + ")")
                              for word in db.session.query(Word).all()]
    pairForm.pairs.choices = [(str(word.id), word.word + " (" + word.cue + ")")
                              for word in db.session.query(Word).all()]

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


@ admin_blueprint.route("/upload_image", methods=["POST"])
@roles_required('Admin')
def upload_image():
    return "Image uploaded"


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
# Receives a word id and returns words in a way so client can see which pairs already exist
def ajax_possible_pairs():
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
