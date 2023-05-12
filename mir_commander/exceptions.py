class Error(Exception):
    pass


class Config(Error):
    pass


class LoadProject(Error):
    def __init__(self, msg: str, details: str = ""):
        super().__init__(msg)
        self.details = details


class LoadFile(Error):
    def __init__(self, msg: str, details: str = ""):
        super().__init__(msg)
        self.details = details
