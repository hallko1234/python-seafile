class ClientHttpError(Exception):
    """
    This exception is raised if the returned HTTP response
    is not as expected.
    """
    def __init__(self, code, message):
        super().__init__()
        self.code = code
        self.message = message

    def __str__(self):
        return f'ClientHttpError[{self.code}: {self.message}]'


class DoesNotExist(Exception):
    """
    Raised when a matching resource cannot be found.
    """
    def __init__(self, msg):
        super().__init__()
        self.msg = msg

    def __str__(self):
        return f'DoesNotExist: {self.msg}'
