
class userNotFoundError(Exception):
    pass


class invaldPasswordError(Exception):
    pass


class invalidImageError(Exception):
    def __init__(self, msg='Image error', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
