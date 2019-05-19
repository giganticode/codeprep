class ParsedToken(object):
    pass


class ParseableToken(object):
    """
    This class represents parts of input that still needs to be parsed
    """

    def __init__(self, val):
        if not isinstance(val, str):
            raise ValueError(f"val should be str but is {type(val)}")
        self.val = val

    def __str__(self):
        return self.val

    def __repr__(self):
        return f'{self.__class__.__name__}({self.val})'

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.val == other.val
