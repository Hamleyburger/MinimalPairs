from werkzeug.utils import redirect
from application.models import Pair
import json
from flask import session, g, request, redirect, url_for, abort
from application.models import Sound
import functools
from application import app
from ..content_management import Content
import uuid
from PIL import Image as PIL_Image


# Decorator: redirect with localized url if no locale
def ensure_locale(func):
    @functools.wraps(func)
    def decorated(*args, **kwargs):

        g.showglobe = True

        # Gets locale from url's args (only routes with locale in url are decorated)
        firstarg = request.path.split('/', 2)[1]

        # Handle cases where first arg is not locale
        if firstarg == "":
            firstarg = session["locale"]
        elif firstarg not in app.config['LANGUAGES']:
            # Abort (remember that only localized routes have this decorator.)
            abort(404)

        # decide whether kwarg["locale"] should be taken from URL or session
        if not session.get("force_session_lang"):
            # force_session_lang is if the language button was pressed
            session["locale"] = firstarg
            kwargs["locale"] = firstarg
        else:
            kwargs["locale"] = session["locale"]
            session.pop("force_session_lang")

        # Find optimal/canonical URL and redirect if canonical is different
        current_path = request.path
        canonical_path = url_for(request.endpoint, *args, **kwargs)

        if str(current_path) != str(canonical_path):
            return redirect(canonical_path, 301)
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


def getCollection():
    """ saves you the time of checking if session['collection'] exists """

    if not session.get("collection"):
        session["collection"] = []

    return session["collection"]


def manageCollection(wordids, remove=False):
    """ Takes a list of word ids and adds them or removes them if remove is True """
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


def easyIPAtyping(typedSound):
    """ Translates some keyboard inputs to the characters in the Sound table """

    if typedSound.isascii():
        print("typed sound is ascii")

    easyTypableSounds = {
        'r': 'ʁ',
        'sj': 'ɕ',
        'ng': 'ŋ',
        'ɡ': 'g'
    }

    if typedSound in easyTypableSounds:
        typedSound = easyTypableSounds[typedSound]

    # Change single characters in case of clusters
    newSound = ""
    for char in typedSound:
        if char == 'ɡ':
            char = 'g'
        elif char == 'r':
            char = 'ʁ'
        newSound += char

    return typedSound


def stripEmpty(inputs):
    """ Returns the input list minus any empty strings """
    outputs = []
    for input in inputs:
        if not input == '':
            outputs.append(input)
    return outputs


def getSecondBest2(sound1: Sound, MOsounds, completeMatches):
    """ Return list of partially matching MO sets with words that haven't already been used\n
    MOsounds: Original list of sounds\n
    completeMatches: Complete matches that have already been found """

    # Check what's already used to avoid duplicates
    usedMOsets = completeMatches.copy()
    usedKeyWords = []
    partialMatches = []
    for MOset in usedMOsets:
        usedKeyWords.append(MOset[0].w1)

    if len(MOsounds) > 2:
        reducedSoundLists = []
        # Loops through all potential sound lists where one sound is removed
        for ignoredSound in MOsounds:
            print("checking where {} is ignored".format(ignoredSound))
            reducedList = []
            for sound in MOsounds:
                if sound != ignoredSound:
                    reducedList.append(sound)
            reducedSoundLists.append(reducedList)

            # Search for all MOsets with reduced list (also potential dupes).
            newMOsets = sound1.getMOPairs(reducedList)
            if newMOsets:
                print("found one")
                # add if not dupe
                approved = True
                for MOset in newMOsets:
                    if MOset[0].w1 in usedKeyWords:
                        approved = False
                if approved:
                    print("adding")
                    partialMatches.append(MOset)
                    usedMOsets.append(MOset)
                else:
                    print("not approved")
            else:
                print("No complete MO sets for this combination")


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

            # Search for all MOsets with reduced list (including dupes).
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


def get_uid():
    """ Returns user id as string """
    uid = session.get("user_id")
    if not uid:
        uid = str(uuid.uuid4())
        session["user_id"] = uid
    print("user has id: {}".format(uid))
    return str(uid)


def custom_images_in_collection(collection):
    """ Takes a collection of WORDS and returns a dict {id: 'staticpath'} user's own cropped images """

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
