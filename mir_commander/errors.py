class Error(Exception):
    pass


class ConfigError(Error):
    pass


class ConfigKeyError(ConfigError):
    pass


class LoadProjectError(Error):
    def __init__(self, msg: str, details: str = ""):
        super().__init__(msg)
        self.details = details


class LoadFileError(Error):
    def __init__(self, msg: str, details: str = ""):
        super().__init__(msg)
        self.details = details
