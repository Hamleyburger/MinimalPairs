from flask import request
import os
from flask import current_app
from PIL import Image
import imghdr
import filecmp
from ..exceptions import invalidImageError

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

# validate_image is in helpers.py because it's used from different forms (add and change)
def validate_image(image):
    valid_formats = ["jpg", "jpeg", "png"]
    valid_extension = [".jpg", ".jpeg", ".png"]
    max_image_size = 3000000

    image.seek(0, os.SEEK_END)
    size = image.tell()
    # seek to its beginning, so you might save it entirely
    image.seek(0)
    if size > max_image_size:
        print("File is > 2.9 mb")
        raise invalidImageError("Image must be less than 3 MB")

    print("checking for format")
    print(str(imghdr.what(image)))
    if imghdr.what(image) not in valid_formats:
        print("invalid image format")
        raise invalidImageError("Image must be .jpg or .png")

    if not image.filename.lower().endswith(tuple(valid_extension)):
        print("wrong extension!")
        raise invalidImageError("Image file extension must be .jpg or .png")


def store_image(image):
    """ Stores image and thumbnail on server if not already there.\n Returns appropriate file name """
    print("store image running")

    directory = current_app.config["IMAGE_UPLOADS"]
    uniquefilename = generateFilename(image.filename, directory)

    print("validating image")
    validate_image(image)

    print("Finished validating. File name will be {}".format(uniquefilename))
    print("***")
    # Store original (is removed if it turns out to be duplicate)
    image.save(os.path.join(directory, uniquefilename))
    print("saved image")

    # Make thumbnail if file is  actually new

    # ensure file uniqueness
    properfilename = uniqueFile(directory, uniquefilename)

    # ensure thumbnail
    properfilename = ensureThumbnail(directory, properfilename, image)

    return properfilename


def ensureThumbnail(directory, filename, image):

    thumbnaildir = directory + "/thumbnails"
    thumbnailfilename = "thumbnail_" + filename

    if os.path.isfile(thumbnaildir + thumbnailfilename):
        print("this thumbnail exists already")
    else:
        print("this thumb didn't exist")

        size = 128, 128
        thumb = Image.open(image)
        thumb.thumbnail(size)
        thumb.save(os.path.join(
            thumbnaildir, thumbnailfilename))

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
    """ Ensure file uniqueness. Checks if new file is actually duplicate. Returns name for the correct file. """

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
