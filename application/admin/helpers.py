from flask import request
import os
from flask import current_app
from PIL import Image
# Helpers is being used by models
# Helpers so far handles session, decorators for views and stock API


#from flask import session


# def clearSessionExcept(*argv):
#    """ Pops any item from session that is not provided as string argument.\n
#    csrf_token must be preserved for wtforms validation to work.\n
#    _flashes must be preserved for messages to be flashed """
#    for key in list(session):
#        if key not in argv:
#            session.pop(key)

def store_image(image):
    """ Stores image on server and saves name in database.\n Returns file name """

    # Resize and save thumbnail separately with name modification
    # Check if image exists rather than file name. If name is same and img
    # different rename

    # Store original
    image.save(os.path.join(
        current_app.config["IMAGE_UPLOADS"], image.filename))

    # Store thumbnail wil Pillow (PIL)
    size = 128, 128
    thumb = Image.open(image)
    thumb.thumbnail(size)
    thumb.save(os.path.join(
        current_app.config["IMAGE_UPLOADS"] + "/thumbnails", "thumbnail_" + image.filename))

    return image.filename
