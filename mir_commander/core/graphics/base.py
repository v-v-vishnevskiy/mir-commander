class Resource:
    __slots__ = "name"

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"
