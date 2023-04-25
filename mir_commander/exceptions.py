class Error(Exception):
    pass


class LoadProject(Error):
    def __init__(self, msg: str, details: str = ""):
        super().__init__(msg)
        self.details = details
