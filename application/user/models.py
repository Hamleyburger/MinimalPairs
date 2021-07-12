from flask_user.user_manager import UserManager
from application import db, app
from flask_user import UserMixin, UserManager
import datetime
import os
from pathlib import Path, PurePath
from flask import jsonify, url_for, session
from .helpers import get_uid
import sentry_sdk


user_roles = db.Table('user_roles',
                      db.Column('user_id', db.Integer(), db.ForeignKey(
                          'users.id', ondelete='CASCADE')),
                      db.Column('roles_id', db.Integer(), db.ForeignKey(
                          'roles.id', ondelete='CASCADE'))
                      )


class User(db.Model, UserMixin):
    """ Users can have different roles """
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    # id, username and password properties necessary for Flask-User
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')

    # Active and role will have to do with Flask-User
    active = db.Column(db.Boolean(), nullable=False, server_default='0')
    roles = db.relationship('Role', secondary='user_roles')

    # Create admin user with 'Admin' role
    @classmethod
    def setAdmin(cls, username, password, user_manager):

        if not cls.query.filter(cls.username == username).first():
            print("setting admin")
            user = cls(
                username=username,
                password=user_manager.hash_password(password),
                active=True
            )
            db.session.add(user)
            user.roles.append(Role.query.get(1))
            db.session.commit()
        else:
            print("admin ok")


# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(300))

# Define the UserRoles association table


class Userimage(db.Model):
    """ Temporary images to be deleted after some time """
    __tablename__ = "userimages"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullpath = db.Column(db.String(), nullable=False, unique=True)
    staticpath = db.Column(db.String(), nullable=False, unique=True)
    userid = db.Column(db.String(), nullable=False)
    wordid = db.Column(db.Integer, db.ForeignKey('words.id'))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    cropped = db.Column(db.Boolean, unique=False, default=False)

    @classmethod
    def store(cls, file, wordid, cropped=False):
        """ Stores a temporary user image. Remeber to set cropped to True if it's a cropped version or it won't be used. Returns url_for saved image """

        Userimage.cleanup()
        user_id = get_uid()

        try:

            print("store...")
            # find/make dir
            temp_path = os.path.join(
                app.config["TEMP_UPLOADS"], user_id)
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)

            # Save file
            file.save(os.path.join(
                temp_path, wordid))
            static_path = os.path.join("tempuploads", user_id, wordid)
            image_url = url_for("static",
                                filename=static_path)

            # Create database entry (keeps track of relationship, status and paths, not content)
            userimage = db.session.query(Userimage).filter_by(
                staticpath=static_path).first()
            if userimage:
                # If user has replaced a previous image for a particular word, update entry
                userimage.cropped = cropped
                userimage.created_date = datetime.datetime.utcnow()

            else:
                # create new db entry for saved user image
                userimage = Userimage(
                    fullpath=os.path.join(temp_path, wordid),
                    staticpath=static_path,
                    userid=user_id,
                    wordid=int(wordid),
                    cropped=cropped
                )

            db.session.add(userimage)
            # Add to session
            userimage.toSession()
            print("commit")
            db.session.commit()

            return image_url

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise e(
                "Apologies! There was a problem storing the image. Dev has been notified.")

    def remove(self):
        """ Remove the image object from database and its correponding file and session entry. """

        word_id = self.wordid
        full_path = self.fullpath
        user_id = self.userid

        if session.get("userimages"):
            if int(word_id) in session["userimages"]:
                print("this image is in the session")
                element = session["userimages"].pop(word_id)
                print("popped {}".format(element))

        if os.path.exists(full_path):
            os.remove(full_path)
        Userimage.query.filter_by(userid=user_id, wordid=word_id).delete()

        db.session.commit()

    def toSession(self):

        if not session.get("userimages"):
            session["userimages"] = {}
        session["userimages"][self.wordid] = self.staticpath

    @classmethod
    def remove_empty_dirs(cls):
        rootdir = app.config["TEMP_UPLOADS"]

        # Walk over a 3-tuple for each file
        for subdir, dirs, files in os.walk(rootdir):
            for dir in dirs:
                check_dir = os.path.join(subdir, dir)
                content = os.listdir(check_dir)
                if not content:
                    try:
                        os.rmdir(check_dir)
                        print("deleting empty dir. ")
                    except OSError as e:
                        print("Error: %s : %s" % (check_dir, e.strerror))

    @classmethod
    def remove_orphan_files(cls):
        # TODO
        # use split path and find database entries where user_id and wordid are same
        # if None remove file and dir if empty
        # return a list of full paths for running remove-file??
        print("called detect orphans")
        rootdir = app.config["TEMP_UPLOADS"]
        userimages = db.session.query(Userimage.userid, Userimage.wordid).all()

        orphans = []

        for dirpath, dirnames, filenames in os.walk(rootdir):
            for file in filenames:
                if file == ".DS_Store":
                    continue
                file_exists = False
                folder_name = PurePath(dirpath).name

                for user_id, word_id in userimages:
                    if file == str(word_id) and folder_name == user_id:
                        file_exists = True
                this_file = os.path.join(dirpath, file)
                if not file_exists:
                    print("file not exist in db. Orphan")
                    orphans.append(this_file)
                    print("this is supposed to be an orphan:".format(this_file))

        if orphans:
            print("orphans")
            for orphan in orphans:
                print(orphan)
                os.remove(orphan)

    @classmethod
    def cleanup(cls):
        """ Checks all user images in 'tempuploads' and removes the outdated ones.\n
        Also removes empty dirs in 'tempuploads' """

        userimages = cls.query.all()

        now = datetime.datetime.utcnow()

        for image in userimages:

            created = image.created_date
            age = now - created
            max_hours = 2
            interval = datetime.timedelta(hours=max_hours)

            print("age (hr, min, sec, ms): {}".format(str(age)))

            if age > interval:
                print("image deleted - more than {} hours old".format(max_hours))
                image.remove()

        cls.remove_orphan_files()
        cls.remove_empty_dirs()
