class Token:
    def __init__(self, type_, meta, location, length):
        self._type = type_
        self._meta = meta
        self._location = location
        self._length = length

    @property
    def type(self):
        return self._type

    @property
    def location(self):
        return self._location

    @property
    def length(self):
        return self._length

    @property
    def meta(self):
        return self._meta

    def __str__(self):
        return f"Token: {self._type} ({self._meta})"

    def __repr__(self):
        return f"<{self} at {id(self):#016x}>"
