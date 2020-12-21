from tempfile import mkdtemp


class Config(object):
    DEBUG = 1
    # intercepting redirects can be set to true for debugging in browser at runtime
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SECRET_KEY = "imnotgonnausethisinproductionbutitsstill32byteslong"
    # API_KEY = ""

    # Ensure templates are auto-reloaded
    TEMPLATES_AUTO_RELOAD = True

    # Configure session to use filesystem (instead of signed cookies)
    SESSION_FILE_DIR = mkdtemp()
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"

    # Specify path for uploading
    IMAGE_UPLOADS = "application/static/images"

    # FLASK_USER configs
    # Enable CSRF and disable email (as recommended by PrettyPrinted.com for flask-user)
    CSRF_ENABLED = True
    # flask-user will try to send email by default in not set to false. Will only work if email is configured.
    USER_ENABLE_EMAIL = False
    USER_REGISTER_TEMPLATE = 'flask_user/login_or_register.html'
    USER_ENABLE_REGISTER = False
    # Unauthenticated is if user is not logged in.
    # string must refer to the desired view function
    USER_UNAUTHENTICATED_ENDPOINT = 'user_blueprint.index'
    # Unauthorized is if user does not have the right role.
    USER_UNAUTHORZED_ENDPOINT = 'user_blueprint.index'
    # End of FLASK_USER configs


class ProductionConfig(Config):
    DEBUG = 0
    SECRET_KEY = "g%6åhjewhg3d%yb4v4ø%43tEugfdg<ggGDFyjf6i7åS%€yøm"
    #API_KEY = ""
    SQLALCHEMY_DATABASE_URI = "sqlite:////home/hamleyburger/???"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = 1
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SECRET_KEY = "thiskeyissecreter"
    SQLALCHEMY_DATABASE_URI = "sqlite:////Users/MacDuck/Documents/Projects/GitHub/MinimalPairs/minimalpairs.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    pass
