from werkzeug.utils import redirect
from application.models import Pair, Sound, Word
from application.admin.models import News
from application import db
import json
from flask import session, g, request, redirect, url_for, abort
import functools
from application import app
from ..content_management import Content
import uuid
from PIL import Image as PIL_Image




# General helpers

# Decorator: redirect with localized url if no locale
def ensure_locale(func):
    @functools.wraps(func)
    def decorated(*args, **kwargs):

        # Make sure routes with locale display globe icon for language change
        g.showglobe = True

        # decide whether kwarg["locale"] should be taken from URL or session
        if not session.get("force_session_lang"):
            # force_session_lang is if the language button was pressed
            print("force session lang is on")
            print(session.get("locale"))
            if request.args.get("locale"):
                session["locale"] = request.args.get("locale")
            
        else:
            session.pop("force_session_lang")
            print("force session lang is off")
        
        kwargs["locale"] = session["locale"]

        print("language is session: {}".format(session["locale"]))

        return func(*args, **kwargs)
    return decorated


def setlocale():

    firstarg = request.path.split('/', 2)[1]
    if firstarg in app.config['LANGUAGES']:
        session["locale"] = firstarg
    print("set ses to firstarg {}".format(firstarg))
    return session["locale"]

# turn json string into int or list of ints
def json_to_ints(json_str):
    """ Takes string input and spits out a list of ints which might contain a single item """
    wordids = json.loads(json_str)
    print(wordids)
    # kick non integers
    wordids = [id for id in wordids if isinstance(id, int)]
    # remove dupes
    wordids = list(set(wordids))
    return wordids


def invalid_IPA_convert(invalid_ipa):
    # Take a sound string and convert invalid IPA characters, 
    # if they can not be confused with more than one valid one.
    # returns string
    
    newSound = ""
    for char in invalid_ipa:
        if char == 'ɡ':
            char = 'g'
        elif char == 'r':
            char = 'ʁ'
        elif char == 'å':
            char = 'ɔ'
        newSound += char
        return newSound


def easyIPAtyping(typedSound):
    """ Translates some keyboard inputs to the characters in the Sound table """

    print("running easy IPA typing")
    if typedSound == "å":
        print("sound was å")

    easyTypableSounds = {
        'r': 'ʁ',
        'sj': 'ɕ',
        'å': 'ɔ',
        'ng': 'ŋ',
        'ɡ': 'g'
    }

    if typedSound in easyTypableSounds:
        typedSound = easyTypableSounds[typedSound]

    return typedSound


def refresh_session_news():

    some_news = db.session.query(News).order_by(News.id.desc()).limit(12).all()
    serialized_news = []

    for news in some_news:
        print(news.word)
        serialized = {
            "id": news.id,
            "title": news.title,
            "text": news.text,
            "title_en": news.title_en,
            "text_en": news.text_en,
            "date_posted": news.date_posted.date().strftime("%d-%m-%Y"),
            "word": news.word,
            "imagepath": news.imagepath
        }

        if news.word:
            serialized["word"] = {
                "word": news.word.word,
                "image_path": "images/thumbnails/{}".format(news.word.image.name),
            }

        serialized_news.append(serialized)
    
    return serialized_news
    
    #print("serialized news is:")
    #print(serialized_news)




#### Collection helpers

def getCollection():
    """ saves you the time of checking if session['collection'] exists """

    if not session.get("collection"):
        session["collection"] = []

    return session["collection"]


def get_word_collection():
    
    ids = getCollection()
    words = db.session.query(Word).filter(Word.id.in_(ids)).all()
    words_with_duplicates = []
    for id in ids:
        for word in words:
            if int(id) == word.id:
                words_with_duplicates.append(word)
    return words_with_duplicates


def manageCollection(wordids, remove=False):
    """ Takes a list of word ids and adds them or removes them if remove is True\n
    Only adds if word not already in collection """
    if not remove:
        print("adding words :)")
        for id in wordids:
            if id not in getCollection():
                getCollection().append(id)
                print(id)

    else:
        print("removing words :)")
        for id in wordids:
            if id in getCollection():
                getCollection().remove(id)
                print(id)


def pairCollected(pair: Pair):
    """ Returns True if a pair is in collection else false """
    if all(ids in getCollection() for ids in [pair.w1.id, pair.w2.id]):
        return True
    else:
        return False


def MOcollected(MO: list):

    """ Only returns True if ALL pairs in MO are collected """
    for pair in MO:
        if not pairCollected(pair):
            return False
    return False


# Count how many times a word has been made into word cards by a user (from collection)
def count_as_used(collection_ids):
    new_ids = []
    print(collection_ids)
    new_ids = list(set(collection_ids))
    print(new_ids)
    for id in new_ids:
        word = Word.query.get(id)
        word.times_used += 1

    db.session.commit()





#### Sound search helpers

# Sound search: Used to find MOs matching search
def stripEmpty(inputs):
    """ Returns the input list minus any empty strings """
    outputs = []
    for input in inputs:
        if not input == '':
            outputs.append(input)
    return outputs


# Sound search: Helps finding the best MOs
def getSecondBest(sound1: Sound, MOsounds, completeMatches, partialMatches=[], counter=0):
    """ Return list of partially matching MO sets with words that haven't already been used\n
    MOsounds: Original list of sounds\n
    completeMatches: Complete matches that have already been found """


    if counter == 0:
        partialMatches = []
    counter += 1

    # for debugging
    def printSets(MOsetList):
        for MOset in MOsetList:
            for pair in MOset:
                print("{}: {}".format(str(pair.w1.word), str(pair.w2.word)))
            print()

    def addReplaceMOset(MOsetList, newSet):
        added = False
        for i, MOset in enumerate(MOsetList):
            if MOset[0].w1 == newSet[0].w1:
                MOsetList[i] = newSet
                added = True
        if added == False:
            MOsetList.append(newSet)

    # Check what's already used to avoid duplicates
    usedMOsets = completeMatches.copy()

    if len(MOsounds) > 2:
        # Loops through all potential sound lists where one sound is removed
        for ignoredSound in MOsounds:
            reducedList = []
            for sound in MOsounds:
                if sound != ignoredSound:
                    reducedList.append(sound)

            # Search for all MOsets with reduced list (including dupes)
            newMOsets = sound1.getMOPairs(reducedList)
            if newMOsets:
                # append if not dupe / replace with any shorter versions
                for newMOset in newMOsets:
                    approved = True
                    for usedMOset in usedMOsets:
                        # if it has same word it's a potential dupe
                        if usedMOset[0].w1 == newMOset[0].w1:
                            # Dertermine which one to keep based on length
                            if len(newMOset) <= len(usedMOset):
                                approved = False
                    if approved:
                        # add to partialmatches for returning and to usedMOsets for checking
                        addReplaceMOset(partialMatches, newMOset)
                        addReplaceMOset(usedMOsets, newMOset)

            # Reduce list further to search for unused but shorter sets with new words.
            partialMatches = getSecondBest(
                sound1, reducedList, completeMatches=usedMOsets, partialMatches=partialMatches, counter=counter)

    return partialMatches

# Sound search: Helps ordering searched pairs so the ones with images appear first
def hasimage(pair):
    """ Checks if pair has image and returns boolean value """
    hasimage = False
    if "default" not in pair.w1.image.name or "default" not in pair.w2.image.name: 
        hasimage = True
    return hasimage

# Sound search: Helps ordering searched MOs so the ones with images appear first
def order_MOsets_by_image(MOsets):
    """ Checks a list of MOsets and sorts the sets so ones with images are first """
    all_sets = []
    sets_with_images = []
    sets_without_images = []
    for MOset in MOsets:
        MOset_has_image = False
        for pair in MOset:
            if hasimage(pair):
                MOset_has_image = True
        if MOset_has_image:
            sets_with_images.append(MOset)
        else:
            sets_without_images.append(MOset)
    all_sets = sets_with_images + sets_without_images
    return all_sets

# User models: converts user id to string.
def get_uid():
    """ Returns user id as string """
    uid = session.get("user_id")
    if not uid:
        uid = str(uuid.uuid4())
        session["user_id"] = uid
    print("user has id: {}".format(uid))
    return str(uid)


def custom_images_in_collection(collection):
    """ Use user's own uploaded images for displaying in collection.
    Takes a collection of WORDS and returns a dict {id: 'staticpath'} 
    where path points to user's own cropped images """

    image_ids = {}

    user_id = session.get("user_id")
    if not user_id:
        return image_ids

    for word in collection:
        for userimage in word.userimages:
            if userimage.userid == user_id:
                print("user has image")
                image_ids[userimage.wordid] = userimage.staticpath

    return image_ids


def resize_crop_image(file):
    """ Resizes a square image and crops an unsquared image
    (if for some reason javascript has been disabled in the
    browser and user managed to upload anyway) \n\n
    Returns PIL Image """

    im = PIL_Image.open(file)
    width, height = im.size   # Get dimensions
    original_format = im.format
    desired_width = 300
    desired_height = 300

    # Resize a square
    if width == height:
        if width > desired_width:
            im = im.resize((desired_height, desired_width))

    # Crop a rectangle:
    else:
        if width > desired_width or height > desired_height:

            if width < desired_width:
                desired_width = width
            if height < desired_height:
                desired_height = height

            left = (width - desired_width)/2
            top = (height - desired_height)/2
            right = (width + desired_width)/2
            bottom = (height + desired_height)/2

            # Crop the center of the image
            im = im.crop((left, top, right, bottom))

    im.format = original_format

    return im

