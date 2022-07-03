from flask import Blueprint, render_template, g
from application import app
import sys
import sentry_sdk

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):

    return render_template("errors/404.html"), 404


@errors.app_errorhandler(403)
def error_403(error):

    return render_template("errors/403.html"), 403


@errors.app_errorhandler(500)
@errors.app_errorhandler(Exception)
def error_500(error):
    if not app.config["DEBUG"]:
        sentry_sdk.capture_exception(error)
    else:
        raise error

    try:
        return render_template("errors/500.html"), 500
    except Exception:
        g.errorpage = True
        return render_template("errors/500.html"), 500


@errors.app_errorhandler(405)
def error_405(error):

    return render_template("errors/405.html"), 405
