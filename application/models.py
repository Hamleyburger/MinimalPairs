from application import db
# import decimal
import copy
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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sound = db.Column(db.String(), nullable=False)

    groups = db.relationship(
        "Group",
        secondary=group_sounds,
        back_populates="sounds", lazy="dynamic")
    db.UniqueConstraint('sound')

    @ classmethod
    def get(cls, soundString=None, soundStringList=None):
        if soundString:
            if isinstance(soundString, str):
                thisSound = cls.query.filter_by(sound=soundString).first()
                if not thisSound:
                    print("'{}' is a new sound.".format(soundString))
                    thisSound = Sound(sound=soundString)
                    db.session.add(thisSound)
                    db.session.flush()
            else:
                thisSound = soundString
            return thisSound
        if soundStringList:
            soundList = []
            for sound in soundStringList:
                if isinstance(sound, str):
                    sound = cls.query.filter_by(sound=sound).first()
                    if not sound:
                        print("'{}' is a new sound.".format(soundString))
                        sound = Sound(sound=soundString)
                        db.session.add(sound)
                        db.session.flush()
                soundList.append(sound)
            return soundList

    def getContrasts(self, sound2):
        """ return a list of pairs\n
        The list is sorted so all word1 have the same sound.\n
        If no such pair exists list will be empty """

        sound1 = self

        # Make a query for populating the contrasts to be returned in the list
        clauseA = and_(Pair.s1 == sound1,
                       Pair.s2 == Sound.get(soundString=sound2))
        clauseB = and_(Pair.s1 == Sound.get(soundString=sound2),
                       Pair.s2 == sound1)
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
                    print("appending pair: {}".format(pair.textify()))

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
                print("Group {} has all the sounds!".format(group.id))

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

    def add(self, word=None, words=[]):
        """ Adds word or word list to caller group. No commit. """
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
                    print("Group: added pair '{}'".format(pair.textify()))

    def updateSounds(self, pairs):
        """ Extracts sounds from pairs, adds to group. Also adds to database if new. """

        soundSet = set()

        # Make sure sounds are unique by adding to set
        for pair in pairs:
            soundSet.add(pair.s1)
            soundSet.add(pair.s2)

        # Append these sounds to group
        bob = self.sounds
        for sound in soundSet:
            if sound not in bob:
                print("added '{}' to group {}".format(sound.sound, self.id))
                self.sounds.append(sound)

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

                            group = addGroupAndAll(group, candidates)
                            modifiedGroups.append(group)
                            added = True
                            break
            if not added:
                newGroup = Group()
                group = addGroupAndAll(newGroup, candidates)
                db.session.add(group)
                db.session.flush()
                print("\nMade new group ({}):".format(group.id), end="")

                for member in group.members:
                    print(member.word + ", ", end='')
                print("")
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

    @classmethod
    def allPairCombinations(cls, wordSet):
        """ Takes a set of words and returns a LIST of all possible existing pairs between them"""

        pairSet = set()
        for word in wordSet:
            for word2 in wordSet:
                pairs = word.getPairs(word2)
                if pairs:
                    pairSet.update(pairs)

        return list(pairSet)

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
            print("Adding new word, id: '{}', '{}'".format(entry.id, entry.word))
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
            print("Not pairing same word...")
            return

        # check if this particular pair exists
        if self.pairExists(word2, sound1):
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

        Group.check(self)

        return pairs

    def pairExists(self, word2, sound1):
        """ Returns True if pair exists with these sounds """
        # check if this particular pair exists
        if self.getPairs(word2):
            for pair in self.getPairs(word2):
                if (sound1 == pair.s1.sound) or (sound1 == pair.s2.sound):
                    print("Pair exists with these sounds already!")
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
                """ Returns new sound\n
                Removes char from sound and replaces empty sounds with 'Ø' """

                newSound = list(cluster)
                newSound[index] = ""
                newSound = ''.join(newSound)
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
                    if (pair.s1.sound == sound1) or (pair.s1.sound == sound2):
                        exists = True
                # And then check if it exists in database
                if not exists:
                    if word1.pairExists(word2, sound1):
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

    def allPartners(self):
        """ Returns words: all caller's partners with relative sounds """
        # TODO: This should be done differently
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
        sound1s = set()
        for pair in pairs:
            sound1s.add(pair.s1)

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


class Image(db.Model):
    """ Image name must correspond to file name in image folder """
    __tablename__ = "images"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

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
