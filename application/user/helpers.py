from werkzeug.utils import redirect
from application.models import Pair
import json
from flask import session, g, request, redirect, url_for
from application.models import Sound
import functools
from application import app
from ..content_management import Content


# Decorator: redirect with localized url if no locale
def ensure_locale(func):
    @functools.wraps(func)
    def decorated(*args, **kwargs):

        allowed = True
        # Gets locale from url's args (only routes with locale in url are decorated)
        firstarg = request.path.split('/', 2)[1]

        if firstarg not in app.config['LANGUAGES']:
            # if url's locale is invalid, pass current session locale to redirect
            kwargs["locale"] = session["locale"]
            allowed = False

        elif session["locale"] != firstarg:

            if session.get("force_session_lang"):
                # if url's arg is different from session and session has precedence, pass session locale to redirect
                kwargs["locale"] = session["locale"]
                session.pop("force_session_lang", None)
                allowed = False
            else:

                # if url's arg is different and url has precedence, redirect to same endpoint
                # with new session locale (which will be same as url - route will be accepted next check)
                session["locale"] = firstarg
                #allowed = False

        if not allowed:
            return redirect(url_for(request.endpoint, *args, **kwargs), 302)
        else:
            return func(*args, **kwargs)

    return decorated


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
