from tempfile import mkdtemp


class Config(object):
    DEBUG = 1
    # intercepting redirects can be set to true for debugging in browser at runtime
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SECRET_KEY = "imnotgonnausethisinproduction"
    # API_KEY = ""

    # Ensure templates are auto-reloaded
    TEMPLATES_AUTO_RELOAD = True

    # Configure session to use filesystem (instead of signed cookies)
    SESSION_FILE_DIR = mkdtemp()
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"


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
