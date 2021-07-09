from flask_user.user_manager import UserManager
from application import db, app
from flask_user import UserMixin, UserManager
import datetime
import os
from flask import jsonify, url_for
from .helpers import get_uid
import sentry_sdk
from alembic.op import drop_constraint


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

    def store(file, wordid, cropped=False):
        """ Validates and stores image. Remeber to set cropped to True if it's a cropped version or it won't be used. Returns url_for saved image """

        user_id = get_uid()
        temp_path = os.path.join(
            app.config["TEMP_UPLOADS"], user_id)
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)

        try:

            # Save file
            file.save(os.path.join(
                temp_path, wordid))
            print("image saved in: {}".format(os.path.join(
                temp_path, wordid)))
            static_path = os.path.join("tempuploads", user_id, wordid)
            private_url = url_for("static",
                                  filename=static_path)

            # Create database entry (keeps track of relationship, status and paths, not content)
            print("query user image")
            userimage = db.session.query(Userimage).filter_by(
                staticpath=static_path).first()
            if userimage:
                print("set cropped")
                userimage.cropped = cropped
                userimage.created_date = datetime.datetime.utcnow
            else:
                print("define user image")
                userimage = Userimage(
                    fullpath=os.path.join(temp_path, wordid),
                    staticpath=static_path,
                    userid=user_id,
                    wordid=int(wordid),
                    cropped=cropped
                )
                print("add user image")
                db.session.add(userimage)
                print("commit")
                db.session.commit()

            return private_url

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise e(
                "Apologies! There was a problem storing the image. Dev has been notified.")
