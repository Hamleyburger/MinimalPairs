from datetime import datetime
from PIL.Image import new
import PIL.Image as pil_image
from application.exceptions import invalidImageError
from application import exceptions
from flask import flash, current_app
from application import db, app
# import decimal
import copy
import os
from sqlalchemy.sql import func
from sqlalchemy import or_, and_
from .admin.filehelpers import store_image, ensureThumbnail
from ipapy import is_valid_ipa
from werkzeug.utils import secure_filename
import os
import time


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

sound_pairs = db.Table('soundpairs',
                        db.Model.metadata,
                       db.Column('sound_id', db.Integer,
                                 db.ForeignKey('sounds.id'), primary_key=True),
                       db.Column('pair_id', db.Integer,
                                 db.ForeignKey('pairs.id'), primary_key=True)
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
        back_populates="sounds", lazy="select")
    
    pairs = db.relationship(
        "Pair",
        secondary=sound_pairs, backref="sounds")


    db.UniqueConstraint('sound')


    def __str__(self):
        return"[{}]".format(self.sound)


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
                elif char == 'å':
                    char = 'ɔ'

                newSound += char

            newSound = newSound.replace("ʊ̯", "w")
            newSound = newSound.replace("ɪ̯", "j")
            newSound = newSound.replace("sp", "sb")
            newSound = newSound.replace("st", "sd")
            newSound = newSound.replace("sk", "sg")

            if newSound != soundString:
                print("fixSoundTyping fixed {} to {}".format(soundString, newSound))

            return newSound

        def objectifyAndAddSound(fixedSound):

            # Check that syllabic and nonsyllabic are not combined

            thisSound = cls.query.filter_by(sound=fixedSound).first()

            if not thisSound:
                try:
                    print("'{}' is a new sound. Checking. ".format(fixedSound))
                    Sound.isvalidsound(fixedSound)
                    thisSound = Sound(sound=fixedSound)
                    db.session.add(thisSound)
                    db.session.flush()
                except Exception as e:
                    raise e

            return thisSound

        if soundString:
            # If sound is a string given by user as opposed to Sound object

            if isinstance(soundString, str): # if string and not Sound object

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

    @ classmethod
    def syllable_safe(cls, soundString):
        """  skal bruges efter easy IPA typing """

        nonsyllabics = "ptkbdgvjʁfsɕhmnŋlðw"
        syllabics = "ieɛæaɑyøœɶuoɔɒʌʊɪɐə"

        syl_sounds = 0
        nonsyl_sounds = 0

        i = 0
        while i < len(soundString):
            symbol = soundString[i]
            nextsymbol = "" if (i == len(soundString) -1) else soundString[i+1]

            if symbol in nonsyllabics:
                sylsymb = "m̩"[1]
                if nextsymbol != sylsymb:
                    nonsyl_sounds += 1
                else:
                    syl_sounds += 1
            elif symbol in syllabics:
                nonsylsymb = "ɐ̯"[1]
                if nextsymbol != nonsylsymb:
                    syl_sounds += 1
                else:
                    nonsyl_sounds += 1
            # Hvis der overhovedet er stavelsesbærende i, så må der kun være en af det, og der må ikke være noget andet i. Hvis det er en stavelsesbærende diakritik på en konsonant, så tæller den bare ikke, så gælder den bare ikke.
            # Hvis det er et ikke-stavelsesbærende tegn efter en vokal, skal den ikke tælles som stqvelsesbærende alligevel.
            i += 1
        #print("syllabic sounds: {} - nonsyllabic sounds: {}".format(syl_sounds, nonsyl_sounds))
        if syl_sounds and nonsyl_sounds:
            raise exceptions.syllableStructureError
            return False
        if syl_sounds > 1:
            raise exceptions.multiSyllableError
            return False
        return True

    @ classmethod
    def isvalidsound(cls, soundString):
        """ checks syllable safety and other validity checks """
        validity = True
        try:
            Sound.syllable_safe(soundString)
            i = 0
            while i < len(soundString):
                symbol = soundString[i]
                nextsymbol = "" if (i == len(soundString) -1) else soundString[i+1]
                if symbol == nextsymbol:
                    raise exceptions.doubleSoundError
                    validity = False
                i+=1
        except Exception as e:
            raise e
            validity = False

        
        return validity

        # if it is single it can have -, else it can't
        # * asterisk is solely for search form and must be dealt with on input.
        pass


    def getContrasts(self, sound2):
        """ Gets all pairs with self sound and sound2, returns a list of pairs\n
        The list is sorted so all word1 have the same sound.\n
        If no such pair exists list will be empty """
        start_time = time.time()

        sound1 = self

        if sound2.sound != "*":
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
            contrasts = sound1.order_pairs_by_sound(contrastsQuery)
        else:
            print("This pair didn't exist. Suggestions?")

        print("getContrasts for {}-{} took {}\n".format(self, sound2, time.time() - start_time))
        return contrasts

    def order_pairs_by_sound(self, pairs):
        """ (Sound) Sorts a given list of pairs so sound1 is self. Throws out pairs without sound1==self\n
        Returns every pair from a group where sound 1 is the same, but word 1 is NOT necessarily the same:\n
        (kor, Thor - klor, glor) <-- k is sound1 """
        

        # Arranging words in pairs so given sound always comes first.
        swappedPairs = []
        for pair in pairs:
            if pair.s1 is self:
                pass
            elif pair.s2 is self:
                pair = Pair(id=pair.id, s1=pair.s2,
                            s2=pair.s1, w1=pair.w2, w2=pair.w1, isinitial=pair.isinitial)
            else:
                continue
            swappedPairs.append(pair)

        pairs = swappedPairs
        return pairs

    def getMOPairs(self, sound2List=[]):
        """ (Sound) Returns 2D array of MOsets.\n
        Takes a key sound and a list of opposition sounds.\n
        Searches in relevant groups for Multiple Oppositions and returns\n
        a list of lists containg MO-sets for each group. """

        def group_pairs_by_w1(inputList):
            """ Takes a list and returns lists: Returns list of pair_lists where word 1 is the same in each list """
            newLists = []

            if not inputList:
                return newLists

            for checkpair in inputList: # pairList's pairs each need to be checked to be distributed into w1-unique lists
                add_to_pairList = False # see if checkpair can be added to any of the pairlists in newlists, if not, add to new list in newlists
                for pairList in newLists:
                    for savedpair in pairList:
                        if checkpair.w1 == savedpair.w1:
                            # if yes we can add checkpair to pairList in newlist adn we can break this loop
                            add_to_pairList = True
                            break
                    if add_to_pairList:
                        pairList.append(checkpair)
                        break
                if not add_to_pairList:
                    newLists.append([checkpair])

            return newLists


        relevant_groups = []
        all_valid_MOsets = []
        sound2s = Sound.get(soundStringList=sound2List)
        sound1and2s = sound2s + [self]
        groups = db.session.query(Group).all()

        # Filter out groups that don't have enough of the desired sounds
        for group in groups:
            intersection = list(set(group.sounds).intersection(sound1and2s))
            if len(intersection) > 2:
                relevant_groups.append(group)

        for group in relevant_groups:

            # sort, order and filter pairs for easier check
            pairs_by_sound = self.order_pairs_by_sound(group.pairs)
            all_MOsets = group_pairs_by_w1(pairs_by_sound)

            for MOset_candidate in all_MOsets:
                moset = MOsetclass.create_valid(self, sound2s, MOset_candidate)
                if moset:
                    all_valid_MOsets.append(moset)
        
        return all_valid_MOsets


class Group(db.Model):
    __tablename__ = "groups"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isinitial = db.Column(db.Boolean(), nullable=True)

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


    def serialize(self):
        """ Serializes a group that has serialized members and sounds """
        serialized = {
            "id": self.id,
            "members": [],
            "sounds": [],
        }
        for member in self.members:
            serialized["members"].append(member.serialize())
        for sound in self.sounds:
            serialized["sounds"].append(sound.sound)

        return serialized

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

    def remove(self):
        """ unlink words(members) and delete group """
        members = self.members.all()
        for member in members:
            self.members.remove(member)
        db.session.flush()
        db.session.delete(self)

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
            initial = None
            for pair in pairs:
                if initial == None:
                    initial = pair.isinitial
                elif initial != pair.isinitial:
                    initial = None
                    print("Pairs with different initials attempted added. Problem!")
                    break
            group.isinitial = initial
            db.session.commit()

            return group

        for candidates in candidateLists:
            added = False
            for group in groups:
                counter = 0
                for member in group.members:
                    if member in candidates:
                        counter += 1
                        if counter == 2:  # it means there are two members from candidates existing in a group, meaning the rest of the candidates belong in this group too

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
                db.session.commit()
                group = addGroupAndAll(newGroup, candidates)
                print("\nMade new group ({}) initial:".format(group.id), end="")
                print(group.isinitial)

                for member in group.members:
                    print(member.word + ", ", end='')
                print("")
                # Behøver jeg modifiedgroups?
                modifiedGroups.append(group)

        return modifiedGroups

    @classmethod
    def updateMeta(cls):  # Group
        """ Finds all pairs in a group and syncs the group's sounds with sounds in the group's pairs """
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
            for sound in groupsounds:
                if sound not in soundList:
                    group.sounds.remove(sound)
            db.session.commit()

    @classmethod
    def get_group_problems(cls):
        """ Find groups with too few members. Find grouped words that aren't matched with all group members """

        problems = []
        all_groups = Group.query.all()

        for group in all_groups:
            bad_members = []
            bad_pairs = []
            isinitial_null = False

            # CHECK FOR MISSING LINKS/UNPAIRED WORDS IN GROUP
            for word in group.members:
                missing_links = []

                for member in group.members:
                    if member != word:
                        if member not in word.allPartners():
                            missing_links.append(member.serialize())
                
                if missing_links:
                    bad_members.append({
                        "word": word.serialize(),
                        "missing_links": missing_links
                    })
            if bad_members:
                bad_group = group.serialize()
                bad_group["type"] = "Loose members"
                bad_group["bad_members"] = bad_members
                problems.append(bad_group)
            
            # CHECK FOR TOO FEW WORDS IN GROUP
            liste = list(group.members)
            if len(liste) < 3:
                bad_group = group.serialize()
                bad_group["type"] = "Too few members"
                problems.append(bad_group)
            
            # CHECK FOR PAIRS IN GROUP WITH WORDS THAT ARE NOT IN GROUP
            for pair in group.pairs:
                if (pair.w1 not in group.members) or (pair.w2 not in group.members):
                    bad_pairs.append(pair) 
            if bad_pairs:
                bad_group = group.serialize()
                bad_group["type"] = "Loose pairs"
                bad_group["bad_pairs"] = bad_pairs
                problems.append(bad_group)

            # CHECK FOR GROUPS WHERE ISINITIAL IS NOT YET DEFINED
            if group.isinitial == None:
                isinitial_null = True

            if isinitial_null:
                bad_group = group.serialize()
                bad_group["type"] = "isinitial null"
                bad_group["isinitial_null"] = True
                problems.append(bad_group)
            
        return problems


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
    isinitial = db.Column(db.Boolean(), nullable=True)

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

    # sounds = db.relationship(
    #     "Sound",
    #     secondary=sound_pairs,
    #     back_populates="pairs")


    def __str__(self):
        string = "{}: {} / {} - ({} vs. {})".format(self.id, self.w1.word,
                                                    self.w2.word, self.s1.sound, self.s2.sound)
        return string



    def sounds(self):
        """ gives you a list with the two sounds in the current pair """
        return [self.s1, self.s2]
    
    def cluster_length(self):
        """ returns 0 if no clusters, else longest cluster length of all cluster from all potential pair combinations """
        # is being used in MO-macros template to ad cluster class to MO, but has no function yet

        all_sounds = []
        pair_combinations = Pair.allPairCombinations([self.w1, self.w2])
        for pc in pair_combinations:
            all_sounds.append(pc.s1)
            all_sounds.append(pc.s2)
        max_length = 0
        for sound in all_sounds:
            length = len(sound.sound)
            if "ɐ̯" in sound.sound:
                length -= 1
            if (length > max_length) and (length > 1):
                max_length = length
        
        return max_length

    def has_images(self):
        image_count = 0
        if self.w1.image.name != "default.svg":
            image_count += 1
        if self.w2.image.name != "default.svg":
            image_count += 1
        return image_count


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


class SearchedPair(db.Model):

    __tablename__ = "searched_pairs"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    s1 = db.Column(db.String(), nullable=False)
    s2 = db.Column(db.String(), nullable=False)
    times_searched = db.Column(db.Integer)
    existing_pairs = db.Column(db.Integer)
    last_searched = db.Column(db.DateTime(timezone=True), server_default=func.current_timestamp(), nullable=False)

    def __str__(self):
        return "Search: [{} {}]".format(self.s1, self.s2)

    def getPairs(self):
        """ Gets all pairs of a searched pair (sound combination) """
        sound1 = Sound.get(self.s1)
        sound2 = Sound.get(self.s2)
        pairs = []
        if sound1:
            pairs = sound1.getContrasts(sound2)
        return pairs
    

    @classmethod
    def add(cls, sound1, sound2, existing_pairs: int = None):
        """ Adds new searched pair to SearchedPairs. Make sure provided sounds are sounds or wildcards. """
        if sound1 == sound2:
            return
        clause1 = and_(cls.s1 == sound1, cls.s2 == sound2)
        clause2 = and_(cls.s1 == sound2, cls.s2 == sound1)
        searched_pair = cls.query.filter(
            or_(clause1, clause2)).first()
        if searched_pair:
            print("searched pair exists. Adding new meta")
            searched_pair.times_searched += 1
            searched_pair.last_searched = func.current_timestamp()
        else:
            print("searched is new. Adding new pair")

            searched_pair = cls(s1=sound1, s2=sound2, times_searched=1)
            db.session.add(searched_pair)
        if existing_pairs:
            searched_pair.existing_pairs = existing_pairs
        if not current_app.config["DEBUG"]:
            print("Added {}".format(searched_pair))
            db.session.commit()


class Word(db.Model):
    """ Has ortographical representations of words """
    __tablename__ = "words"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    word = db.Column(db.String(), nullable=False)
    cue = db.Column(db.String(), server_default="")
    img_id = db.Column(db.Integer, db.ForeignKey(
        'images.id'), nullable=True, server_default="1")
    times_used = db.Column(db.Integer, server_default="0", nullable=False)

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
        return "<{}>".format(self.word)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        else:
            # print("{} and {} are not the same type".format(str(self), str(other)))
            return False

    def serialize(self):
        "Serializes a word, but its partners do not have partners"
        serialized = {
            "id": self.id,
            "word": self.word,
            "cue": self.cue,
            "partners": [],
            "image": self.image.name
        }
        for partner in self.allPartners():
            serialized["partners"].append({
                "id": partner.id,
                "word": partner.word,
                "cue": partner.cue,
            })
        return serialized


    @classmethod
    def homonyms(cls, word):
        """ Returns a list of homonyms or None if no homonyms """
        homonyms = db.session.query(Word).filter_by(word=word).all()
        if homonyms:
            return homonyms
        else:
            return None

    @classmethod
    def add(cls, word, image=None, cue=None, artist=None):
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
                img = Image(name=image, artist=artist) if artist else Image(name=image)
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
    def change(cls, id, newword="", newcue="", newimg="", newartist=""):
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
                print("\n\n*********\n\nold image is: {}".format(word.image))
                image = Image.store(newimg)  # return appropriate image object
                word.image = image
            except Exception as e:
                print(e)
                flash(e, "danger")

        if newartist:
            word.image.artist = newartist

        db.session.commit()

        Image.cleanImages()

        return word

    def pair(self, word2, sound1, sound2, initial=None):
        """ word2 is the word to pair with. Sound1 is own sound. Sound2 is opposite sound\n
        Always put the longest cluster combinations as possible, so they can be reduced """
        
        s1 = Sound.get(sound1)
        s2 = Sound.get(sound2)
        sound1 = s1.sound
        sound2 = s2.sound
        print("attempting to pair {} {}".format(sound1, sound2))

        db.session.flush()

        if((self.id == word2.id)):
            print("Not pairing same word...")
            return

        # check if this particular pair exists
        if self.pairExists(word2, sound1, sound2):
            print("pair exists alerady")
            return

        newPair = Pair(w1=self, w2=word2,
                       s1=s1, s2=s2, isinitial=initial)
        newPair.sounds = [s1, s2]

        db.session.add(newPair)
        db.session.commit()


        pairs = self.getReducedPairs(word2, sound1, sound2, pairList=[], initial=initial)

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

    def getReducedPairs(self, word2, sound1, sound2, pairList=[], initial=None):
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
                                    s1=Sound.get(soundString=newSound1), s2=Sound.get(soundString=newSound2), isinitial=initial)
                        db.session.add(pair)
                        db.session.flush()
                        pairList.append(pair)
                        # Recursive call:
                        self.getReducedPairs(
                            word2, newSound1, newSound2, pairList, initial)
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

    def getRoleInGroup(self, group):
        """ For one word pairing get the version (in clusters) with the most sounds 
        / the original - for automatically suggesting pair sounds in admin.add.
        Returns sound object """

        word2 = ""
        for member in group.members:
            if member == self:
                continue
            else:
                word2 = member
                break

        incoming_pairs = self.getPairs(word2)
        pairs = self.orderPairsByWord(incoming_pairs)

        longest_sound = ""
        longest_pair = None
        for pair in pairs:
            if not longest_pair:
                longest_sound = pair.s1
                longest_pair = pair
            if len(pair.s1.sound) > len(longest_sound.sound):
                longest_sound = pair.s1
                longest_pair = pair

        return longest_pair.s1

    def orderPairsByWord(self, pairs):
        """ Takes a bunch of pairs and orders them so word1 is always w1 and s1 """
        orderedpairs = []
        for pair in pairs:
            if pair.w1 == self:
                orderedpairs.append(pair)
            else:
                flippedpair = Pair(id=pair.id, w1=pair.w2, w2=pair.w1,
                            s1=pair.s2, s2=pair.s1, isinitial=pair.isinitial)
                orderedpairs.append(flippedpair)

        return orderedpairs

    def orderedPairs(self):
        """ (Word) Orders words in pairs so first word is caller """

        # Gets all pairs for word and makes self be word1 (w1)
        pairs = self.getPairs()
        newPairs = []
        for oldPair in pairs:
            pair = Pair(id=oldPair.id, w1=oldPair.w1, w2=oldPair.w2,
                        s1=oldPair.s1, s2=oldPair.s2, isinitial=oldPair.isinitial)
            if oldPair.w2 == self:
                pair.w1 = oldPair.w2
                pair.w2 = oldPair.w1
                pair.s1 = oldPair.s2
                pair.s2 = oldPair.s1
            newPairs.append(pair)

        # This part be replaced with function
        return newPairs

    def get_full_MOsets(self):
        """ (Word) Gets unfiltered Multiple Opposition sets where word is key. Returns 2D array """
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
        """ Deletes given word and its associated pairs form database. Removes group if too small """
        pairs = db.session.query(Pair).filter(or_(
            (Pair.w1 == self), (Pair.w2 == self))).all()

        print("word to remove: " + self.word)
        for pair in pairs:
            print("deleting " + pair.textify())
            db.session.delete(pair)
        print("deleting " + "'" + self.word + "'")

        groups = self.groups

        print("deleted word's group member counts:")
        for group in groups:
            group = db.session.query(Group).filter_by(id=group.id).first()
            members = group.members.all()
            count = len(members)
            if count <= 3:
                print("this group ({}) will no longer be valid after deletion of word".format(group))
                group.remove()

        db.session.delete(self)
        db.session.commit()

    def get_partner_suggestions(self, unadded_ids=None):
        """ Returns a 2D list of triple tuples with word ids and their sounds. 
        Word ids are for suggested partners based on the groups the admin suggesged
        words belong to and the sounds are extracted by comparing each suggestion to
        the rest of the group """

        partner_suggestions = []
        admin_decided_partners = db.session.query(Word).filter(Word.id.in_(unadded_ids)).all()

        # Find relevant groups that have two or more expected partners.
        relevant_groups = []
        for word in admin_decided_partners:
            for group in word.groups:
                if group.has_two_members_of(admin_decided_partners):
                    if group not in relevant_groups:
                        relevant_groups.append(group)

        # Pick out the words that are not already the word in question or the admin decided ones 
        # (the ones we got with ajax) or already partnered with word
        # and make a list of ids for the suggested words.
        # Using set() to prevent duplicates since we might add from many groups

        for group in relevant_groups:

            group_partner_suggestions = []

            for word in group.members:
                if word.id != self.id:
                    owned_ids = []
                    for part in self.allPartners():
                        owned_ids.append(part.id)
                    if word.id not in owned_ids:
                        suggested_sound = word.getRoleInGroup(group)
                        group_partner_suggestions.append((word.id, suggested_sound.sound, group.isinitial))
            partner_suggestions.append(group_partner_suggestions)

        return partner_suggestions

    def get_samesound_pairs(self):
        pairs = self.orderedPairs()
        sound2list = []
        samesound_pairs = []
        for pair in pairs:
            if pair.s2 in sound2list:
                for p2 in pairs:
                    if (p2.s2 == pair.s2) and p2.id != pair.id:
                        if p2.s1 == pair.s1:
                            if p2.isinitial == pair.isinitial:
                                samesound_pairs.append(p2)
                                samesound_pairs.append(pair)
            sound2list.append(pair.s2)
        return samesound_pairs


class Image(db.Model):
    """ Images specifically for word cards. Image name must correspond to file name in image folder """
    __tablename__ = "images"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(), nullable=False,
                     server_default='default.svg', unique=True)
    time_created = db.Column(db.DateTime(timezone=True), default=func.current_timestamp())
    # time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    artist = db.Column(db.String(), nullable=False, server_default='Alma Manley')
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
        print("cleaning images")

        images = cls.query.all()

        # Clears out unlinked images from db
        for image in images:
            if len(image.words) == 0:
                print(
                    "\n\n\nWarning: this image has no connected words. Deleting: {}".format(image.name))
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
                    #print("file in imagedir not folder or DS_Store: {}".format(file))
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


class PermaImage(db.Model):
    """ Any image belonging in permaimages. path is path from static. display width, name_da and name_en and type are optional """
    __tablename__ = "permaimages"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String(), nullable=False)
    time_created = db.Column(db.DateTime(timezone=True), default=func.current_timestamp())
    display_width = db.Column(db.Integer)
    display_name_da = db.Column(db.String())
    display_name_en = db.Column(db.String())
    artist = db.Column(db.String(), nullable=False, server_default='Alma Manley')

    type = db.Column(db.String())

    def get_thumb(self):
        basename = os.path.basename(self.path)
        thumb_path = "permaimages/thumbnails/thumb_" + basename
        return thumb_path

    @classmethod
    def store_and_get_path(cls, form_image_data, permaimages_path=""):
        """ Store image in static/permaimages/??? and return path """

        filename = secure_filename(form_image_data.filename)
        static_path = app.config["STATIC_PATH"]
        imagepath = "permaimages" + permaimages_path + filename
        save_path = static_path + "/" + imagepath
        form_image_data.save(save_path)
        print("saving in {}".format(save_path))
        return imagepath
    

        



class MOsetclass(object):
    def __new__(self, valid_sorted_pairlist):

        self.pairs = valid_sorted_pairlist
        return self.pairs
        
    
    @classmethod
    def create_valid(cls, s1: Sound, s2list: list, MOset_candidate):

        valid_MOset = []

        for pair in MOset_candidate:
            if pair.s2 in s2list:
                valid_MOset.append(pair)

        if len(valid_MOset) < 2:
            return None
        else:
            return cls(valid_MOset)
    



