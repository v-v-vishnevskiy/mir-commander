class CoreError(Exception):
    pass


class ConfigError(CoreError):
    pass


class LoadProjectError(CoreError):
    pass


class FileManagerError(CoreError):
    pass


class FileExporterNotFoundError(FileManagerError):
    pass


class FileImporterNotFoundError(FileManagerError):
    pass


class FileImporterRegistrationError(FileManagerError):
    pass


class FileExporterRegistrationError(FileManagerError):
    pass


class ProjectNodeRegistrationError(CoreError):
    pass


class ProjectNodeNotFoundError(CoreError):
    pass


class UndefinedProgramError(CoreError):
    pass


class ProgramRegistrationError(CoreError):
    pass
