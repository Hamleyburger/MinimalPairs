from flask import request
import os
from flask import current_app
from PIL import Image
# Helpers is being used by models
# Helpers so far handles session, decorators for views and stock API


# from flask import session


# def clearSessionExcept(*argv):
#    """ Pops any item from session that is not provided as string argument.\n
#    csrf_token must be preserved for wtforms validation to work.\n
#    _flashes must be preserved for messages to be flashed """
#    for key in list(session):
#        if key not in argv:
#            session.pop(key)

def store_image(image):
    """ Stores image and thumbnail on server if not already there.\n Returns appropriate file name """

    directory = current_app.config["IMAGE_UPLOADS"]
    filename = generateFilename(image.filename, directory)

    # Store original
    image.save(os.path.join(directory, filename))

    # TODO: When image is saved, check if it is identical to any of the
    # images in the folder. If it is, delete it again and return the name of
    # the identical image. Else also generate thumbnail

    # Store thumbnail wil Pillow (PIL)
    size = 128, 128
    thumb = Image.open(image)
    thumb.thumbnail(size)
    thumb.save(os.path.join(
        current_app.config["IMAGE_UPLOADS"] + "/thumbnails", "thumbnail_" + filename))

    return filename


def generateFilename(filename, directory):
    nameFound = False
    if filename in os.listdir(directory):
        i = 0
        while nameFound is False:

            name, ext = os.path.splitext(filename)
            nameSuggestion = name + "(" + str(i) + ")" + ext
            i += 1

            if nameSuggestion in os.listdir(directory):
                continue
            else:
                filename = nameSuggestion
                nameFound = True
    return filename
