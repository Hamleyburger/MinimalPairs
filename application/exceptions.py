

class userNotFoundError(Exception):
    pass


class invaldPasswordError(Exception):
    pass


class invalidImageError(Exception):
    def __init__(self, msg='Image error', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)




# Errors in sound search with user feedback:
class multiSyllableError(Exception):
    def __init__(self, msg="Cannot have more than one syllable in a contrast", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class syllableStructureError(Exception):
    def __init__(self, msg="Cannot mix syllabic and nonsyllabic sounds in a contrast", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class doubleSoundError(Exception):
    def __init__(self, msg="The same sound has been typed twice or more in a field", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)

