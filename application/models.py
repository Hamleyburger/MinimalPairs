from application import db
import decimal
from sqlalchemy.sql import func
from sqlalchemy import or_
from .admin.helpers import store_image
import os
import filecmp


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
    db.UniqueConstraint('word_id', 'partner_id')


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
        If any of them exist, asks whether to replace or make homonymous entry """

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

        # If added img is in db already connect it, but ask first.
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
        """ word2 is the word to pair with. Sound1 is own sound. Sound2 is opposite sound """
        db.session.flush()
        if((self.id == word2.id) or (word2 in self.allPartners())):
            print("Word is same or already paired")
            return
        pair = Pair(word_id=self.id, partner_id=word2.id,
                    word_sound=sound1, partner_sound=sound2)
        db.session.add(pair)
        db.session.flush()
        print("'" + self.word + "' partners:")
        for partner in self.partners:
            print("p: " + partner.word)
        for word in self.words:
            print("w: " + word.word)
        print("'" + word2.word + "' partners:")
        for partner in word2.partners:
            print("p: " + partner.word)
        for word in word2.words:
            print("w: " + word.word)

        # print("word 1 partners: {}".format(self.partners))
        # print("Word 2 partners: {}".format(word2.words))

    def allPartners(self):
        """ Returns a list of all words partnered with caller \n
        Both ways are ocunted in ("partners" or "words") """
        partners = self.partners
        words = self.words
        allPartners = partners + words
        return allPartners

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
        """ Stores file if it's new\n
        Changes name if necessary\n
        Adds to database (no commit)\n 
        Returns image object (not the actual file) """

        # appropriate imageName - can be old or new
        imageName = store_image(imageFile)
        image = Image.query.filter_by(name=imageName).first()

        if not image:
            print("Adding new image object to database")
            image = Image(name=imageName)
            db.session.add(image)

        return image
