from application import db
import decimal
from sqlalchemy.sql import func
from sqlalchemy import or_, and_
from .admin.helpers import store_image

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
                                  db.ForeignKey('sounds.id'))
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

    id = db.Column(db.Integer, primary_key=True)
    sound = db.Column(db.String(), nullable=False)

    groups = db.relationship(
        "Group",
        secondary=group_sounds,
        back_populates="sounds", lazy="dynamic")
    db.UniqueConstraint('sound')

    @ classmethod
    def get(cls, soundString):
        thisSound = cls.query.filter_by(sound=soundString).first()
        if not thisSound:
            thisSound = Sound(sound=soundString)
            db.session.add(thisSound)
        return thisSound


class Group(db.Model):
    __tablename__ = "groups"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

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

    def add(self, word=None, words=None):
        """ Adds word or word list to caller group. No commit. """
        if word:
            if word not in self.members:
                print("*****New group member***** -- \"{}\"".format(word.word))
                self.members.append(word)
                for member in self.members:
                    print(member.word + ", ", end='')
                print("")

        if words:
            for word in words:
                if word not in self.members:
                    print("*****New group member!***** -- \"{}\"".format(word.word))
                    self.members.append(word)
                    for member in self.members:
                        print(member.word + ", ", end='')
                    print("")

    def addPairs(self, pairs=[], pair=None):
        """ Takes a list of pairs or a pair and adds to group's collection """
        if pair:
            pairs.append(pair)
        if pairs:
            for pair in pairs:
                if pair not in self.pairs:
                    self.pairs.append(pair)
                    print("added pair '{}' to group".format(pair.textify()))

    def updateSounds(self, pairs):
        """ Extracts sounds from pairs, adds to group. Also adds to database if new. """
        print("running updatesounds")
        soundSet = set()
        newSoundSet = set()
        for pair in pairs:
            soundSet.update(pair.word_sound, pair.partner_sound)

        for sound in soundSet:
            print("sound found: {}".format(sound))
            newSoundSet.add(Sound.get(sound))

        for newSound in newSoundSet:
            self.sounds.append(newSound)

    @classmethod
    def check(cls, ko):
        """ Checks a word and its partners to see if they can be grouped.\n
        Adds to or creates a group if they can. """

        db.session.flush()
        koCandidateSets = []

        # Check if new word has mutual friends with its partners
        for to in ko.allPartners():
            for tøbo in to.allPartners():
                if ko in tøbo.allPartners():
                    # If they do have mutual friends, add them to set or make new
                    added = False
                    if koCandidateSets:
                        for toSet in koCandidateSets:
                            if set([ko, to]).issubset(toSet):
                                toSet.update([ko, to, tøbo])
                                added = True

                    if not added:
                        newSet = set([ko, to, tøbo])
                        koCandidateSets.append(newSet)

        if koCandidateSets:
            # Add to appropriate group or make new
            Group.group(koCandidateSets)

    @classmethod
    def group(cls, candidateSets: list):
        """ Checks a list of SETS(!!) to see if a group already exists for this set\n
        Returns group """

        groups = cls.query.all()
        modifiedGroups = []

        def addGroupAndAll(group, candidates):
            group.add(words=list(candidates))
            # Candidates should already be added to group
            pairs = Pair.allPairCombinations(
                set(group.members))
            group.addPairs(pairs=pairs)
            group.updateSounds(pairs)

            return group

        for candidates in candidateSets:
            added = False
            for group in groups:
                counter = 0
                for member in group.members:
                    if member in candidates:
                        counter += 1
                        if counter == 2:

                            print("\nI found a group that contains:")
                            for member in group.members:
                                print(" - " + member.word)

                            group = addGroupAndAll(group, candidates)

                            print("\n After addGroupAndAll it contains:")
                            for member in group.members:
                                print(" - " + member.word)

                            modifiedGroups.append(group)
                            added = True
                            break
            if not added:
                print("Making new group:")
                newGroup = Group()
                group = addGroupAndAll(newGroup, candidates)
                db.session.add(group)

                db.session.flush()
                for member in group.members:
                    print(member.word + ", ", end='')
                # Behøver jeg modifiedgroups?
                modifiedGroups.append(group)

        return modifiedGroups

    def updateMeta():
        """ Finds all pairs in a group and updates its collection of pairs and sounds """
        # TODO make it also find a list of orphans and overwrite to a file.
        pass


class Pair(db.Model):
    """ Contains a word1 (caller) and its partner, word2 - \n
    distinguished by sound1 (caller's sound) and sound2 """
    __tablename__ = "pairs"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)

    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    partner_id = db.Column(
        db.Integer, db.ForeignKey('words.id'), nullable=False)
    word_sound = db.Column(db.String(), nullable=False)
    partner_sound = db.Column(db.String(), nullable=False)

    # explicit/composite unique constraint.  'name' is optional.
    db.UniqueConstraint('word_id', 'partner_id', 'word_sound')

    groups = db.relationship(
        "Group",
        secondary=group_pairs,
        back_populates="pairs")

    @classmethod
    def getContrasts(cls, sound1, sound2):
        """ return a list of pairs with new attributes:\n
        word1, sound1, word2, sound2\n
        The list is sorted so all word1 have the same sound.\n
        If no such pair exists list will be empty """

        # Make a contrast class
        class Contrast(Pair):
            def __init__(self, word1=None, word2=None, sound1=None, sound2=None):
                self.word1 = word1
                self.word2 = word2
                self.sound1 = sound1
                self.sound2 = sound2

        # Make a list for containing ordered contrasts
        contrasts = []

        # Make a query for populating the contrasts to be returned in the list
        word1 = db.aliased(Word)
        word2 = db.aliased(Word)
        clauseA = and_(Pair.word_sound == sound1, Pair.partner_sound == sound2)
        clauseB = and_(Pair.word_sound == sound2, Pair.partner_sound == sound1)

        contrastsQuery = db.session.query(Pair, word1, word2).filter(or_(
            clauseA, clauseB)).join(word1, word1.id == Pair.word_id).join(word2, word2.id == Pair.partner_id).all()

        # Order the items returned from query, add to instances of Contrast and append to contrasts list
        if contrastsQuery:
            for pair, word1, word2 in contrastsQuery:

                if pair.word_sound == sound1:
                    contrast = Contrast(
                        word1=word1, word2=word2, sound1=pair.word_sound, sound2=pair.partner_sound)
                else:
                    contrast = Contrast(
                        word1=word2, word2=word1, sound1=pair.partner_sound, sound2=pair.word_sound)

                contrasts.append(contrast)
        else:
            print("This pair didn't exist. Suggestions?")

        return contrasts

    @classmethod
    def allPairCombinations(cls, wordSet):
        """ Takes a set of words and returns a LIST of all possible existing pairs """
        pairSet = set()
        for word in wordSet:
            for word2 in wordSet:
                pairs = word.getPairs(word2)
                if pairs:
                    pairSet.update(pairs)
        return list(pairSet)

    # Some id is displayed even if pair is not committed yet
    def textify(self):
        string = "{}: {} ({}) vs. {} ({})".format(self.id, Word.query.get(
            self.word_id).word, self.word_sound, Word.query.get(self.partner_id).word, self.partner_sound)
        return string


class Word(db.Model):
    """ Has ortographical representations of words """
    __tablename__ = "words"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(), nullable=False)
    cue = db.Column(db.String(), server_default="No cue")
    img_id = db.Column(db.Integer, db.ForeignKey(
        'images.id'), nullable=True, server_default="1")

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

        # If word exists, figure out if it's homonymous or same
        entry = db.session.query(Word).filter_by(word=word).all()
        if not entry:
            entry = Word(word=word)
            if cue is not None:
                entry.cue = cue
            print("Adding new word: {}".format(entry.word))
            db.session.add(entry)
        else:
            if cue is "":
                cue = None

            entry = Word(word=word, cue=cue)
            print("Adding homonym '{}' with cue '{}'".format(
                entry.word, entry.cue))
            db.session.add(entry)

        db.session.flush()

        # If added img is in db already connect old img
        if image is not None and image is not "":

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
        print(entry)
        print("committing to session")
        # db.session.commit()

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
        if newword is not "":
            word.word = newword
        if newcue is not "":
            word.cue = newcue
        if newimg is not "":
            image = Image.store(newimg)  # return appropriate image object
            word.image = image

        print("Commit from 'change'")
        db.session.commit()

        # Check if there are idle images lying around
        images = db.session.query(Image).all()
        for image in images:
            if len(image.words) is 0:
                print(
                    "Warning: this image has no connected words: {}".format(image.name))

        return word

    def pair(self, word2, sound1, sound2):
        """ word2 is the word to pair with. Sound1 is own sound. Sound2 is opposite sound\n
        Always put the longest cluster combinations as possible, so they can be reduced """
        db.session.flush()
        if((self.id == word2.id)):
            print("Word is same")
            return

        # check if this particular pair exists
        if self.pairExists(word2, sound1):
            return

        newPair = Pair(word_id=self.id, partner_id=word2.id,
                       word_sound=sound1, partner_sound=sound2)

        pairs = self.getReducedPairs(word2, sound1, sound2, pairList=[])

        pairs.append(newPair)

        db.session.bulk_save_objects(pairs)
        # Prøv her (eller efter commit?) at lave rekursivt tjek af lydstrenge
        db.session.commit()

        Group.check(self)

    def pairExists(self, word2, sound1):
        """ Returns True if pair exists with these sounds """
        # check if this particular pair exists
        if self.getPairs(word2):
            for pair in self.getPairs(word2):
                if (sound1 == pair.word_sound) or (sound1 == pair.partner_sound):
                    print("pair exists with these sounds")
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
            def charSharesPlaces(char, sound1, sound2):
                """ Returns boolean\n
                Checks if char occurs in start vs end, and thus must not be removed """
                approved = False
                if not (sound1.startswith(char) and sound2.startswith(char)):
                    if not (sound1.endswith(char) and sound2.endswith(char)):
                        approved = False
                        print(
                            "Mutual char can't be removed because they don't share position")

                return approved

            def reduceSounds(char, cluster):
                """ Returns new sound\n
                Removes char from sound and replaces empty sounds with 'Ø' """
                newSound = cluster.replace(char, "")
                if newSound == "":
                    newSound = "Ø"
                return newSound

            # Helper function to check if we already have a pair in list or database
            def pairExists(pairList, sound1, sound2, word1, word2):
                """ Returns boolean\n
                Checks if pair exists first in current list and then in database """
                exists = False
                # Check if pair exists in list
                for pair in pairList:
                    if (pair.word_sound == sound1) or (pair.word_sound == sound2):
                        exists = True
                # And then check if it exists in database
                if not exists:
                    if word1.pairExists(word2, sound1):
                        exists = True
                return exists

            # Recursively remove removable chars until nothing left to remove
            for char in commonChars:
                if charSharesPlaces(char, sound1, sound2):
                    print("removing '{}'".format(char))
                    newSound1 = reduceSounds(char, sound1)
                    newSound2 = reduceSounds(char, sound2)

                    # Check if pair already exists in pairList:
                    if not pairExists(pairList, newSound1, newSound2, self, word2):
                        pair = Pair(word_id=self.id, partner_id=word2.id,
                                    word_sound=newSound1, partner_sound=newSound2)
                        pairList.append(pair)
                        # Recursive call:
                        self.getReducedPairs(
                            word2, newSound1, newSound2, pairList)
        return pairList

    def defineAsPartner(self, pair):
        """ Returns this partner with relative sounds"""
        if self.id == pair.partner_id:
            self.wordSound = pair.word_sound
            self.partnerSound = pair.partner_sound
        elif self.id == pair.word_id:
            self.wordSound = pair.partner_sound
            self.partnerSound = pair.word_sound
        return self

    def allPartners(self):
        """ Returns all caller's partners with relative sounds """
        # Make list containing all partners
        partners = self.partners
        words = self.words
        allPartners = partners + words
        # Removes duplicates (to be added back after processing)
        allPartners = list(dict.fromkeys(allPartners))

        # Populate list of partner objects
        allPartners_with_sound = []
        for i, partner in enumerate(allPartners):

            pairs = self.getPairs(partner)
            for pair in pairs:
                # Create new partner object and add to list
                partner = partner.defineAsPartner(pair)
                # Duplicates are added back in with their unique sound combinations
                allPartners_with_sound.insert(i, partner)

        return allPartners_with_sound

    def getPairs(self, word2):
        """ Returns a list with all possible pairings between two words\n
        Since two words can have more than one pairing (sk vs g / s vs Ø)\n
        Returns None if no pairs exist """

        clause1 = and_(Pair.word_id == self.id, Pair.partner_id == word2.id)
        clause2 = and_(Pair.word_id == word2.id, Pair.partner_id == self.id)
        pairs = Pair.query.filter(
            or_(clause1, clause2)).all()

        if not pairs:
            return None

        for pair in pairs:
            if pair.word_id == word2.id:
                # If sound 1 and 2 and swapped, swap them back
                tempW = pair.partner_id
                pair.partner_id = pair.word_id
                pair.word_id = tempW

                tempS = pair.partner_sound
                pair.partner_sound = pair.word_sound
                pair.word_sound = tempS

        return pairs

    def remove(self):
        """ Deletes given word and its associated pairs form database"""
        pairs = db.session.query(Pair).filter(or_(
            (Pair.word_id == self.id), (Pair.partner_id == self.id))).all()

        print("word to remove: " + self.word)
        for pair in pairs:
            print("deleting " + str(pair))
            db.session.delete(pair)
        print("deleting " + "'" + self.word + "'")
        db.session.delete(self)
        db.session.commit()


class Image(db.Model):
    """ Image name must correspond to file name in image folder """
    __tablename__ = "images"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(), nullable=False,
                     server_default='default.jpg', unique=True)

    # is pointed to by at least one word. One-to-many with word.
    words = db.relationship("Word", back_populates="image")

    def store(imageFile):
        """ Stores file in folder if it's new\n
        Changes name if necessary\n
        Adds to database (no commit)\n 
        Returns image object (not the actual file) """

        # appropriate imageName - can be old or new
        imageName = store_image(imageFile)
        image = Image.query.filter_by(name=imageName).first()

        if not image:
            image = Image(name=imageName)
            db.session.add(image)

        return image
