from PIL.Image import new
from application.exceptions import invalidImageError
from flask import flash, current_app
from application import db
# import decimal
import copy
import os
from sqlalchemy.sql import func
from sqlalchemy import or_, and_
from .admin.filehelpers import store_image, ensureThumbnail
from ipapy import is_valid_ipa


word_grouping = db.Table('groupwords',
                         db.Column('group_id', db.Integer,
                                   db.ForeignKey('groups.id')),
                         db.Column('word_id', db.Integer,
                                   db.ForeignKey('words.id'))
                         )

group_sounds = db.Table('groupsounds',
                        db.Column('group_id', db.Integer,
                                  db.ForeignKey('groups.id')),
                        db.Column('sound_id', db.Integer,
                                  db.ForeignKey('sounds.id')),
                        db.UniqueConstraint('group_id', 'sound_id')
                        )


group_pairs = db.Table('grouppairs',
                       db.Column('group_id', db.Integer,
                                 db.ForeignKey('groups.id')),
                       db.Column('pair_id', db.Integer,
                                 db.ForeignKey('pairs.id'))
                       )


class Sound(db.Model):
    """ So far this table is made exclusively for association groups with all its sounds """
    __tablename__ = "sounds"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sound = db.Column(db.String(), nullable=False)

    groups = db.relationship(
        "Group",
        secondary=group_sounds,
        back_populates="sounds", lazy="dynamic")
    db.UniqueConstraint('sound')

    @ classmethod
    def get(cls, soundString=None, soundStringList=None):
        """ Converts both sounds and lists of sounds to Sound objects, stores them if new and returns either list or single entity """

        def fixSoundTyping(soundString):
            # Fix g and r IPA typos that are definitely typos
            newSound = ""
            for char in soundString:
                if char == 'ɡ':
                    char = 'g'
                elif char == 'r':
                    char = 'ʁ'
                newSound += char

            return newSound

        def objectifyAndAddSound(fixedSound):
            thisSound = cls.query.filter_by(sound=fixedSound).first()

            if not thisSound:
                print("'{}' is a new sound.".format(fixedSound))
                thisSound = Sound(sound=fixedSound)
                db.session.add(thisSound)
                db.session.flush()

            return thisSound

        if soundString:
            # If sound is a string given by user as opposed to Sound object

            if isinstance(soundString, str):

                fixedSound = fixSoundTyping(soundString)
                thisSound = objectifyAndAddSound(fixedSound)

            else:
                thisSound = soundString

            # Assumes that thisSound is a Sound object?
            return thisSound

        if soundStringList:
            soundList = []
            for sound in soundStringList:

                if isinstance(sound, str):
                    fixedSound = fixSoundTyping(sound)
                    sound = objectifyAndAddSound(fixedSound)

                soundList.append(sound)
            return soundList

    def getContrasts(self, sound2):
        """ return a list of pairs\n
        The list is sorted so all word1 have the same sound.\n
        If no such pair exists list will be empty """

        sound1 = self

        if sound2 != "*":
            # Make a query for populating the contrasts to be returned in the list
            clauseA = and_(Pair.s1 == sound1,
                           Pair.s2 == Sound.get(soundString=sound2))
            clauseB = and_(Pair.s1 == Sound.get(soundString=sound2),
                           Pair.s2 == sound1)
        else:
            clauseA = Pair.s1 == sound1
            clauseB = Pair.s2 == sound1

        contrastsQuery = db.session.query(Pair).filter(or_(
            clauseA, clauseB)).all()

        # Order the items returned from query, add to instances of Contrast and append to contrasts list
        contrasts = []
        if contrastsQuery:
            contrasts = sound1.orderedPairs(contrastsQuery)
        else:
            print("This pair didn't exist. Suggestions?")

        return contrasts

    def orderedPairs(self, pairs, sound2List=None):
        """ (Sound) Sorts a given list of pairs so sound1 is self. Throws out pairs without sound1==self\n
        If sound2List is given, only returns a list of pairs if all contrasts are present """

        # Arranging words in pairs so given sound always comes first.
        swappedPairs = []
        for pair in pairs:
            if pair.s1 is self:
                pass
            elif pair.s2 is self:
                pair = Pair(id=pair.id, s1=pair.s2,
                            s2=pair.s1, w1=pair.w2, w2=pair.w1)
            else:
                continue
            swappedPairs.append(pair)

        pairs = swappedPairs

        # If sound2list is given, filter out pairs where s2 is not in list
        if sound2List:
            print("")
            filteredPairs = []
            # Convert strings to Sound objects in case they're strings
            newSound2List = Sound.get(soundStringList=sound2List)

            # Filter out pairs without wanted sound2
            for pair in pairs:
                if pair.s2 in newSound2List:
                    filteredPairs.append(pair)
                    # print("appending pair: {}".format(pair.textify()))

            if len(filteredPairs) == len(sound2List):
                # This is where it checks if all sound2s are present. Can be modified with a minimum criterion.
                pairs = filteredPairs
            else:
                pairs = []

        return pairs

    def getMOPairs(self, sound2List=[]):
        """ (Sound) Returns 2D array.\n
        Takes a key sound and a list of opposition sounds.\n
        Searches in relevant groups for Multiple Oppositions and returns\n
        a list of lists containg MO-sets for each group. """

        groups = db.session.query(Group).all()
        relevantGroups = []

        # Filter out groups that don't have all the sounds
        sound2s = Sound.get(soundStringList=sound2List)
        for group in groups:
            if all(elem in group.sounds for elem in (sound2s + [self])):
                relevantGroups.append(group)
                # print("Group {} has all the sounds!".format(group.id))

        # Search relevant groups and add their MO-sets to pair list
        pairLists = []
        for group in relevantGroups:

            groupMOs = self.orderedPairs(group.pairs, sound2List)
            if groupMOs:
                pairLists.append(groupMOs)

        return pairLists


class Group(db.Model):
    __tablename__ = "groups"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    members = db.relationship(
        "Word",
        secondary=word_grouping,
        back_populates="groups", lazy="dynamic")

    sounds = db.relationship(
        "Sound",
        secondary=group_sounds,
        back_populates="groups", lazy="dynamic")

    pairs = db.relationship(
        "Pair",
        secondary=group_pairs,
        back_populates="groups", lazy="dynamic")


    def __str__(self):
        """ Prints a group """
        string = "Group {}: ".format(self.id)
        for word in self.members:
            string = string + "{}, ".format(word)
        return string


    def add(self, word=None, words=[]):
        """ Adds word or word list to caller group. Avoids duplicates. No commit. """
        if word:
            words.append(word)

        if words:
            for word in words:
                if word not in self.members:
                    print("Adding \"{}\" to group {}".format(word.word, self.id))
                    self.members.append(word)

    def addPairs(self, pairs=[], pair=None):
        """ Takes a list of pairs or a pair and adds to group's collection """
        if pair:
            pairs.append(pair)
        if pairs:
            print("")
            for pair in pairs:
                if pair not in self.pairs:
                    self.pairs.append(pair)

    def updateSounds(self, pairs):
        """ Extracts sounds from pairs, adds to group. Also adds to database if new. """

        soundSet = set()

        # Make sure sounds are unique by adding to set
        for pair in pairs:
            soundSet.add(pair.s1)
            soundSet.add(pair.s2)

        # Append these sounds to group
        groupsounds = self.sounds
        for sound in soundSet:
            if sound not in groupsounds:
                self.sounds.append(sound)
                print("added '{}' to group {}".format(sound.sound, self.id))

    def textify(self):
        """ Prints a group """
        print("Group {}:".format(self.id))
        for word in self.members:
            print(word.word, end=", ")
        print("")
        return None

    def has_two_members_of(self, words):

        acquainted_members = 0

        for member in self.members:
            if member in words:
                acquainted_members += 1

        if acquainted_members >= 2:
            return True

    @classmethod
    def check(cls, ko):
        """ Checks a word and its partners to see if they can be grouped.\n
        Adds to or creates a group if they can. This is (should be) run\n
        whenever two words are paired.\n
        Returns a group if the word was added in one """

        db.session.flush()
        koCandidateSets = []
        return_groups = []

        print("checking word '{}' to see if it can be grouped anywhere.".format(ko.word))
        # Check if new word has mutual friends with its partners
        for to in ko.allPartners():
            for tøbo in to.allPartners():
                if ko in tøbo.allPartners():
                    # If they do have mutual friends, add them to set or make new
                    added = False
                    if koCandidateSets:
                        for toList in koCandidateSets:
                            if all(words in toList for words in [ko, to]):
                                if tøbo not in toList:
                                    toList.append(tøbo)

                                added = True

                    if not added:
                        # print("Since '{}' and '{}' both know '{}' we put them in a candidate list to see if they're already grouped ".format(
                        #     ko.word, to.word, tøbo.word))
                        newList = [ko, to, tøbo]
                        koCandidateSets.append(newList)

        if koCandidateSets:
            # Add to appropriate group or make new
            return_groups = Group.group(koCandidateSets)

        return return_groups

    @classmethod
    def group(cls, candidateLists: list):
        """ Checks a lists of words lists to see if groups already exist for those lists\n
        Returns any groups[] found or created group """

        groups = cls.query.all()
        modifiedGroups = []

        def addGroupAndAll(group, candidates):

            group.add(words=candidates)
            # Candidates should already be added to group
            pairs = Pair.allPairCombinations(group.members)
            group.addPairs(pairs=pairs)
            group.updateSounds(pairs)

            return group

        for candidates in candidateLists:
            print("checking candidate list: {}".format(candidates))
            added = False
            for group in groups:
                counter = 0
                for member in group.members:
                    if member in candidates:
                        counter += 1
                        if counter == 2:  # it means there are two members from candidates existing in a group, meaning the rest of the candidates belong in this group too
                            print("found group")
                            group = addGroupAndAll(group, candidates)
                            modifiedGroups.append(group)
                            added = True
                            break
                if added:
                    # If we've found or added a group, don't check the next groups for this candidate list
                    break
                        

            if not added:
                newGroup = Group()
                db.session.add(newGroup)
                group = addGroupAndAll(newGroup, candidates)
                db.session.flush()
                print("\nMade new group ({}):".format(group.id), end="")

                for member in group.members:
                    print(member.word + ", ", end='')
                print("")
                # Behøver jeg modifiedgroups?
                modifiedGroups.append(group)

        return modifiedGroups

    @classmethod
    def updateMeta(cls):  # Group
        """ Finds all pairs in a group and updates its collection of pairs and sounds """
        groups = db.session.query(cls).all()
        for group in groups:
            soundList = []
            pairs = group.pairs
            for pair in pairs:
                if pair.s1 not in soundList:
                    soundList.append(pair.s1)
                if pair.s2 not in soundList:
                    soundList.append(pair.s2)
            groupsounds = group.sounds
            for sound in soundList:
                if sound not in groupsounds:
                    group.sounds.append(sound)


class Pair(db.Model):
    """ Contains a word1 (caller) and its partner, word2 - \n
    distinguished by sound1 (caller's sound) and sound2 """
    __tablename__ = "pairs"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    partner_id = db.Column(
        db.Integer, db.ForeignKey('words.id'), nullable=False)
    word_sound_id = db.Column(
        db.Integer, db.ForeignKey('sounds.id'), nullable=False)
    partner_sound_id = db.Column(
        db.Integer, db.ForeignKey('sounds.id'), nullable=False)

    # These sounds should be replaced
    word_sound = db.Column(db.String())
    partner_sound = db.Column(db.String())

    # Each pair has a word 1 (word) and a word 2 (partner)
    w1 = db.relationship("Word", primaryjoin="Pair.word_id==Word.id")
    w2 = db.relationship("Word", primaryjoin="Pair.partner_id==Word.id")

    s1 = db.relationship("Sound", primaryjoin="Pair.word_sound_id==Sound.id")
    s2 = db.relationship(
        "Sound", primaryjoin="Pair.partner_sound_id==Sound.id")

    # explicit/composite unique constraint.  'name' is optional.
    db.UniqueConstraint('word_id', 'partner_id', 'word_sound', 'sound1t')

    groups = db.relationship(
        "Group",
        secondary=group_pairs,
        back_populates="pairs")

    def __str__(self):
        string = "{}: {} / {} - ({} vs. {})".format(self.id, self.w1.word,
                                                    self.w2.word, self.s1.sound, self.s2.sound)
        return string



    @classmethod
    def allPairCombinations(cls, wordSet):
        """ Takes a list of words and returns a list of all possible existing pairs between them"""

        pairList = []
        for word in wordSet:
            for word2 in wordSet:
                pairs = word.getPairs(word2)
                if pairs:
                    pairList.extend(pairs)

        return pairList

    # Some id is displayed even if pair is not committed yet
    def textify(self):
        string = "{}: {} / {} - ({} vs. {})".format(self.id, self.w1.word,
                                                    self.w2.word, self.s1.sound, self.s2.sound)
        return string


class Word(db.Model):
    """ Has ortographical representations of words """
    __tablename__ = "words"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    word = db.Column(db.String(), nullable=False)
    cue = db.Column(db.String(), server_default="")
    img_id = db.Column(db.Integer, db.ForeignKey(
        'images.id'), nullable=True, server_default="1")

    def __str__(self):
        return "<{}>".format(self.word)

    # Relationships
    image = db.relationship("Image", back_populates="words")
    # partners = db.relationship("Word", secondary="pairs",
    #                          backref=db.backref("users", lazy=True))
    partners = db.relationship(
        'Word',
        secondary="pairs",
        primaryjoin=id == Pair.word_id,
        secondaryjoin=id == Pair.partner_id,
        backref=db.backref('words')
    )

    groups = db.relationship(
        "Group",
        secondary=word_grouping,
        back_populates="members")

    userimages = db.relationship(
        "Userimage", backref=db.backref('word'), cascade="all, delete")

    def __str__(self):
        return "{} <{}>".format(self.word, self.id)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        else:
            print("{} and {} are not the same type".format(str(self), str(other)))
            return False

    @classmethod
    def homonyms(cls, word):
        """ Returns a list of homonyms or None if no homonyms """
        homonyms = db.session.query(Word).filter_by(word=word).all()
        if homonyms:
            return homonyms
        else:
            return None

    @classmethod
    def add(cls, word, image=None, cue=None):
        """ Adds string as word to database and an optional image name\n
        If any of them exist, asks whether to replace or make homonymous entry\n
        Remember to first call store_image to get appropriate file name in\n
        case of duplicates"""

        print("WORD ADD")

        # If word exists, figure out if it's homonymous or same
        entry = db.session.query(Word).filter_by(word=word).all()
        if not entry:
            entry = Word(word=word)
            if cue is not None:
                entry.cue = cue
            print("Adding new word, id: '{}', '{}'".format(entry.id, entry.word))
            db.session.add(entry)
        else:
            if cue == "":
                cue = None

            entry = Word(word=word, cue=cue)
            print("Adding homonym '{}' with cue '{}'".format(
                entry.word, entry.cue))
            db.session.add(entry)

        db.session.flush()

        print(image)
        print("image is ^^^")
        # If added img is in db already connect old img
        if image != None and image != "":

            print("Image is not none or ''.")
            img = db.session.query(Image).filter_by(name=image).first()
            if not img:
                print("Image does not exist in database")
                img = Image(name=image)
            elif entry in img.words:
                print("This image is already connected to this word.")
                return
            if (entry.img_id != 1):
                print("This word has img id {}".format(entry.img_id))
                answer = input("Replace? y/n:")
                if answer == "y":
                    pass
                else:
                    # No need to worry about not adding new word since we'd never get here if word was new.
                    print("Aborting. No changes were made")
                    return

            print("adding new image to word")
            entry.image = img
            db.session.add(img)

        # Returning word object for optional use
        return entry

    @classmethod
    def change(cls, id, newword="", newcue="", newimg=""):
        """ For admin to change entries. Anything goes.\n
        id(required), newword, newcue, newimg\n
        returns word or None if trying to link to unexisting image"""

        # Finds the word to change
        word = Word.query.filter_by(id=id).first()

        # Changes what must be changed
        if newword != "":
            word.word = newword
        if newcue != "":
            if newcue == "-":
                newcue = ""
            word.cue = newcue
        if newimg != "":
            try:
                print("trying to store image")
                image = Image.store(newimg)  # return appropriate image object
                word.image = image
            except Exception as e:
                print(e)
                flash(e, "danger")

        print("Commit from 'change'")
        db.session.commit()

        Image.cleanImages()

        return word

    def pair(self, word2, sound1, sound2):
        """ word2 is the word to pair with. Sound1 is own sound. Sound2 is opposite sound\n
        Always put the longest cluster combinations as possible, so they can be reduced """
        
        sound1 = str(Sound.get(sound1).sound)
        sound2 = str(Sound.get(sound2).sound)
        print("attempting to pair {} {}".format(sound1, sound2))

        db.session.flush()

        if((self.id == word2.id)):
            print("Not pairing same word...")
            return

        # check if this particular pair exists
        if self.pairExists(word2, sound1, sound2):
            return

        newPair = Pair(w1=self, w2=word2,
                       s1=Sound.get(soundString=sound1), s2=Sound.get(soundString=sound2))
        db.session.add(newPair)
        db.session.commit()

        pairs = self.getReducedPairs(word2, sound1, sound2, pairList=[])

        pairs.append(newPair)

        db.session.bulk_save_objects(pairs)
        # Prøv her (eller efter commit?) at lave rekursivt tjek af lydstrenge
        db.session.commit()

        any_groups = Group.check(self)

        for group in any_groups:
            group.textify()

        return pairs

    def pairExists(self, word2, sound1, sound2):
        """ Returns True if pair exists with these sounds """
        # check if this particular pair exists
        if self.getPairs(word2):
            for pair in self.getPairs(word2):
                if (sound1 == pair.s1.sound and sound2 == pair.s2.sound) or (sound1 == pair.s2.sound and sound2 == pair.s1.sound):
                    return True
            return False

    def getReducedPairs(self, word2, sound1, sound2, pairList=[]):
        """ Recursive function. Reduces pairs (subtracts mutual sounds) until\n
        nothing left to reduce.\n
        pairList is passed from within the function and will have new pairs\n
        added to it until finished."""

        # This function returns if there are no clusters in any of the sounds.
        if (len(sound1) > 1) or (len(sound2) > 1):

            # Find common chars
            commonChars = []
            for char in sound1:
                if char in sound2:
                    commonChars.append(char)

            # Helper function for reducing clusters
            def removeChar(char, sound1, sound2):
                """ Checks if char occurs in start or end in both clusters
                \n Returns -1 if end, 0 if start """

                if not (sound1.startswith(char) and sound2.startswith(char)):
                    if not (sound1.endswith(char) and sound2.endswith(char)):
                        print(
                            "{} {} - '{}' has a bad position".format(sound1, sound2, char))
                        return None
                    else:
                        # Ends with same char, meaning index -1
                        return -1
                else:
                    # Starts with same char meaning index 0
                    return 0

            def reduceSounds(cluster, index):
                """ Returns new sound (/reduced cluster)\n
                Removes char from sound and replaces empty sounds with 'Ø' """

                newSound = list(cluster)
                newSound[index] = ""
                newSound = ''.join(newSound)
                if newSound == "":
                    newSound = "-"
                return newSound

            # Helper function to check if we already have a pair in list or database
            def pairExists(pairList, sound1, sound2, word1, word2):
                """ Returns boolean\n
                Checks if pair exists first in current list and then in database """
                exists = False
                # Check if pair exists in list
                for pair in pairList:
                    if (pair.s1.sound == sound1 and pair.s2.sound == sound2) or (pair.s1.sound == sound2 and pair.s2.sound == sound1):
                        exists = True
                # And then check if it exists in database
                if not exists:
                    if word1.pairExists(word2, sound1, sound2):
                        exists = True
                return exists

            # Recursively remove removable chars until nothing left to remove
            for char in commonChars:
                index = removeChar(char, sound1, sound2)
                if index is not None:
                    newSound1 = reduceSounds(sound1, index)
                    newSound2 = reduceSounds(sound2, index)
                    # Check if pair already exists in pairList:
                    if not pairExists(pairList, newSound1, newSound2, self, word2):
                        pair = Pair(w1=self, w2=word2,
                                    s1=Sound.get(soundString=newSound1), s2=Sound.get(soundString=newSound2))
                        db.session.add(pair)
                        db.session.flush()
                        pairList.append(pair)
                        # Recursive call:
                        self.getReducedPairs(
                            word2, newSound1, newSound2, pairList)
        return pairList

    def allPartners(self):  # Word
        """ Returns words: all caller's partners with relative sounds """

        # Make list containing all partners
        partners = self.partners
        words = self.words
        allPartners = partners + words

        return allPartners

    def getPairs(self, word2=None):
        """ Returns a list with all possible pairings\n
        \n if word2 is given, only pairings between the two words are returned
        \nReturns None if no pairs exist """
        pairs = []

        if word2:
            clause1 = and_(Pair.w1 == self, Pair.w2 == word2)
            clause2 = and_(Pair.w1 == word2, Pair.w2 == self)
            pairs = Pair.query.filter(
                or_(clause1, clause2)).all()

        else:
            pairs = Pair.query.filter(
                or_(Pair.w1 == self, Pair.w2 == self)).all()

        return pairs

    def orderedPairs(self):
        """ (Word) Orders words in pairs so first word is caller. If sound1 is given,
        \n only pairs where word 1 (caller) has sound 1 will be returned.\n
        if sound2List is given, all pairings with any of those sounds are returned"""

        # Gets all pairs for word and makes self be word1 (w1)
        pairs = self.getPairs()
        newPairs = []
        for oldPair in pairs:
            pair = Pair(id=oldPair.id, w1=oldPair.w1, w2=oldPair.w2,
                        s1=oldPair.s1, s2=oldPair.s2)
            if oldPair.w2 == self:
                pair.w1 = oldPair.w2
                pair.w2 = oldPair.w1
                pair.s1 = oldPair.s2
                pair.s2 = oldPair.s1
            newPairs.append(pair)

        # This part be replaced with function
        return newPairs

    def getMOSets(self):
        """ (Word) Gets all Multiple Opposition sets where word is key. Returns 2D array """
        pairs = self.orderedPairs()

        # Find potential sound1s:
        sound1s = []
        for pair in pairs:
            if pair.s1 not in sound1s:
                sound1s.append(pair.s1)

        # Based on sound1s find all MO-sets where word (self) is parent/key
        MOsets = []
        for sound1 in sound1s:
            MOset = []
            for pair in pairs:
                if pair.s1 is sound1:
                    MOset.append(pair)
            if len(MOset) > 1:
                MOsets.append(MOset)

        return MOsets

    def remove(self):
        """ Deletes given word and its associated pairs form database"""
        pairs = db.session.query(Pair).filter(or_(
            (Pair.w1 == self), (Pair.w2 == self))).all()

        print("word to remove: " + self.word)
        for pair in pairs:
            print("deleting " + pair.textify())
            db.session.delete(pair)
        print("deleting " + "'" + self.word + "'")
        db.session.delete(self)
        db.session.commit()

    def get_partner_suggestions(self, unadded_ids=None):
        """ Returns a list of word ids for forgotten/suggested partners based on existing partners\n
        and unadded ones whose ids must be passed in via unadded_ids """

        # Get list of the words we're assuming that this word is or will be partnered with
        expected_partners = self.partners
        for word in expected_partners:
            if word.id in unadded_ids:
                unadded_ids.remove(word.id)
        unadded_words = db.session.query(Word).filter(
            Word.id.in_(unadded_ids)).all()
        expected_partners = expected_partners + unadded_words
        print("Expected partners: {}".format(
            [word.word for word in expected_partners]))

        # Find relevant groups that have two or more expected partners.
        relevant_group_ids = []
        relevant_groups = []
        for word in expected_partners:
            for group in word.groups:
                if group.has_two_members_of(expected_partners):
                    if group.id not in relevant_group_ids:
                        relevant_group_ids.append(group.id)
                        relevant_groups.append(group)

        print("Groups that contain forgotten partners:")
        for group in relevant_groups:
            group.textify()

        # Pick out the words that are not already in ANY of expected partners (existing and AJAX picked) and suggest ids
        # Using set() to prevent duplicates since we might add from many groups
        suggest_word_ids = set()
        for group in relevant_groups:
            for word in group.members:
                if word.id != self.id:
                    if word.id not in [word.id for word in expected_partners]:
                        suggest_word_ids.add(word.id)

        return list(suggest_word_ids)


class Image(db.Model):
    """ Image name must correspond to file name in image folder """
    __tablename__ = "images"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(), nullable=False,
                     server_default='default.svg', unique=True)

    # is pointed to by at least one word. One-to-many with word.
    words = db.relationship("Word", back_populates="image")

    @classmethod
    def store(cls, imageFile):
        """ Stores file in folder if it's new\n
        Changes name if necessary\n
        Adds to database (no commit)\n
        Returns image object (not the actual file) """

        # appropriate imageName - can be old or new
        imageName = store_image(imageFile)
        image = cls.query.filter_by(name=imageName).first()

        if not image:
            image = cls(name=imageName)
            db.session.add(image)

        return image

    def remove(self):
        """ deletes image from db """
        db.session.delete(self)

        print("remove: {}".format(self.name))

        dir = current_app.config["IMAGE_UPLOADS"]
        file = os.path.join(dir, self.name)
        thumbname = self.name
        thumbdir = dir + "/thumbnails"
        thumbnail = os.path.join(thumbdir, thumbname)

        print("dir to delete; {}".format(file))

        if os.path.isfile(file):
            os.remove(file)

        if os.path.isfile(thumbnail):
            os.remove(thumbnail)

    def file(self):
        filename = self.name

        dir = current_app.config["IMAGE_UPLOADS"]
        file = os.path.join(dir, filename)

        return file

    @classmethod
    def cleanImages(cls):

        images = cls.query.all()

        # Clears out unlinked images from db
        for image in images:
            if len(image.words) == 0:
                print(
                    "Warning: this image has no connected words. Deleting: {}".format(image.name))
                image.remove()
                db.session.commit()

        # Clears out files that do not exist in db
        images = cls.query.all()
        imgdir = current_app.config["IMAGE_UPLOADS"]

        # detect and remove files that have no db links
        print("path: {}".format(current_app.root_path))
        print("searching: {}".format(imgdir))
        for file in os.listdir(imgdir):
            # make sure we're not counting subdirectories as files
            if not os.path.isdir(os.path.join(imgdir, file)):
                if not file == ".DS_Store":
                    print("file in imagedir not folder or DS_Store: {}".format(file))
                    if file not in [image.name for image in images]:
                        print(file + " not linked to a word in database... and?")
                        os.remove(os.path.join(imgdir, file))

        # make sure all images in have thumbnails
        for image in images:
            ensureThumbnail(imgdir, image.name, image.file())

        # find and delete orphan thumbnails
        for thumbnailname in os.listdir(os.path.join(imgdir, "thumbnails")):
            if thumbnailname not in os.listdir(imgdir):
                print("orphan thumbnail: {}".format(thumbnailname))
                os.remove(os.path.join(imgdir, "thumbnails", thumbnailname))

    @classmethod
    def setDefault(cls):
        default = cls.query.get(1)
        if not default:
            print("Setting default image")
            default = cls(name="default.svg")
            db.session.add(default)
            db.session.commit()
        else:
            print("default image ok")
