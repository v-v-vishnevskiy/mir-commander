class CoreError(Exception):
    pass


class LoadProjectError(CoreError):
    pass


class FileManagerError(CoreError):
    pass


class FileExporterNotFoundError(FileManagerError):
    pass


class FileImporterNotFoundError(FileManagerError):
    pass
