from flask_user.user_manager import UserManager
from application import db, app
from flask_user import UserMixin, UserManager


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
