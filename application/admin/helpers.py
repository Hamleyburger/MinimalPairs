from flask import request
import os
from flask import current_app
from PIL import Image
import os
import filecmp
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
    print("store image running")
    directory = current_app.config["IMAGE_UPLOADS"]
    filename = generateFilename(image.filename, directory)
    print("file name will be {}".format(filename))

    # Store original (is removed if it turns out to be duplicate)
    image.save(os.path.join(directory, filename))
    print("hi")

    # Make thumbnail if file is  actually new
    oldFilename = uniqueFile(directory, filename)
    if filename == oldFilename:
        size = 128, 128
        thumb = Image.open(image)
        thumb.thumbnail(size)
        thumb.save(os.path.join(
            current_app.config["IMAGE_UPLOADS"] + "/thumbnails", "thumbnail_" + filename))
    else:
        # File already existed, so we use the old one
        filename = oldFilename

    return filename


def generateFilename(filename, directory):
    """ Checks filename uniqueness and generates new by adding number """

    nameFound = False
    if filename in os.listdir(directory):

        i = 0
        while nameFound is False:
            # Separate name from extension to add number
            name, ext = os.path.splitext(filename)
            nameSuggestion = name + "(" + str(i) + ")" + ext
            i += 1

            if nameSuggestion not in os.listdir(directory):
                filename = nameSuggestion
                nameFound = True

    return filename


def uniqueFile(directory, filename):
    """ Checks if new file is duplicate. If yes delete new and return old. """

    file1 = directory + "/" + filename
    for oldfilename in os.listdir(directory):
        # Don't compare the file we just stored to itself
        if oldfilename != filename:
            file2 = directory + "/" + oldfilename
            if filecmp.cmp(file1, file2):
                # It's a duplicate. Delete and set filename to old
                os.remove(file1)
                filename = oldfilename
                break

    return filename
