from flask import request
import os
import shutil
from flask import current_app
from PIL import Image
import imghdr
import time
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
    valid_formats = ["jpg", "jpeg", "png", "svg"]
    valid_extension = [".jpg", ".jpeg", ".png", ".svg"]
    max_image_size = 3000000

    fileExists(image, current_app.config["IMAGE_UPLOADS"])

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

    # check if file exists and set filename if not
    uniquefilename = fileExists(image, directory)
    if not uniquefilename:
        uniquefilename = generateFilename(image.filename, directory)

        # only validate if new file
        print("validating image")
        validate_image(image)

        print("Finished validating. File name will be {}".format(uniquefilename))
        print("***")
        # Store original (is removed if it turns out to be duplicate)
        image.save(os.path.join(directory, uniquefilename))
        print("saved image")

    # ensure thumbnail
    ensureThumbnail(directory, uniquefilename, image)

    return uniquefilename


def ensureThumbnail(directory, filename, image=None):
    """ makes sure there's a thumbnail and returns filename """

    thumbnaildir = directory + "/thumbnails"
    thumbnailfilename = filename

    if os.path.isfile(thumbnaildir + thumbnailfilename):
        print("this thumbnail exists already")
    else:
        if filename.lower().endswith((".jpg", ".png", ".jpeg")):

            # raster images are resized for thumbnail*
            size = 200, 200
            thumb = Image.open(image)
            thumb.thumbnail(size)
            thumb.save(os.path.join(
                thumbnaildir, thumbnailfilename))
        elif filename.lower().endswith(".svg"):
            # svg are not resized, but simply copied as thumbnail* to thumbnail dir
            print("svg")
            image = os.path.join(directory + "/" + filename)
            print("osjoin: {}".format(image))
            shutil.copy(image, thumbnaildir)
            dst_image = os.path.join(thumbnaildir, filename)
            newname = os.path.join(thumbnaildir, thumbnailfilename)
            print("putting {} in {}".format(newname, thumbnaildir))
            os.rename(dst_image, newname)

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


def fileExists(file, directory):
    """ Checks if file exists in directory. Returns filename of existing file or None  """
    tmpdir = directory + "/check_file"
    os.mkdir(tmpdir)
    file1 = os.path.join(tmpdir, "check_file")
    file.save(file1)
    for filename in os.listdir(directory):
        file2 = directory + "/" + filename
        if filecmp.cmp(file1, file2):
            print("exists")
            shutil.rmtree(tmpdir)
            return os.path.basename(file2)
    print("not exists")
    shutil.rmtree(tmpdir)
    return None
