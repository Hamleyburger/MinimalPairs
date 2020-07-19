from application import db
import decimal
from sqlalchemy.sql import func


class Pair(db.Model):
    """ Contains a word and its partner - Contrast's first letter must be of lower value than the second """
    __tablename__ = "pairs"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)

    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    partner_id = db.Column(
        db.Integer, db.ForeignKey('words.id'), nullable=False)
    word_sound = db.Column(db.String(), nullable=False)
    partner_sound = db.Column(db.String(), nullable=False)

    # Each word will have a partner. Many to many.
    @classmethod
    def pair(cls, word1, word2, sound1, sound2):
        db.session.flush()
        print("words passed in: {}".format(word1.__dict__))
        pair = Pair(word_id=word1.id, partner_id=word2.id,
                    word_sound=sound1, partner_sound=sound2)
        db.session.add(pair)
        print("word 1 partners: {}".format(word1.partners))
        print("Word 2 partners: {}".format(word2.words))


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

    def homonyms(word):
        """ Returns a list of homonyms or None if no homonyms """
        homonyms = db.session.query(Word).filter_by(word=word).all()
        if homonyms:
            return homonyms
        else:
            return None

    def add(word, image=None, cue=None):
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

            print("Image is not none.")
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

        db.session.commit()

    def change(id, newword="", newcue="", newimg=""):
        """ id, newword, newcue, newimg """

        word = Word.query.filter_by(id=id).first()
        if newword is not "":
            word.word = newword
        if newcue is not "":
            word.cue = newcue
        if newimg is not "":
            image = db.session.query(Image).filter_by(name=newimg).first()

            if not image:
                print("image does not exist. Fail!")
                return False
            else:
                word.image = image

        db.session.commit()

        images = db.session.query(Image).all()
        for image in images:
            if len(image.words) is 0:
                print(
                    "Warning: this image has no connected words: {}".format(image.name))

        return True

    def get(spelling):
        if not isinstance(spelling, str):
            raise Exception("Word must be a string")

        db.session.query(Word).filter_by(word=spelling).first()


class Image(db.Model):
    """ Image name must correspond to file name in image folder """
    __tablename__ = "images"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(), nullable=False,
                     server_default='default.jpg', unique=True)

    # is pointed to by at least one word. One-to-many with word.
    words = db.relationship("Word", back_populates="image")
