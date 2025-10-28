class CoreError(Exception):
    pass


class LoadProjectError(CoreError):
    pass


class FileManagerError(CoreError):
    pass


class ItemExporterNotFoundError(FileManagerError):
    pass


class FileImporterNotFoundError(FileManagerError):
    pass
