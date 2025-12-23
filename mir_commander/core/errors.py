class CoreError(Exception):
    pass


class PluginError(CoreError):
    pass


class PluginRegistrationError(PluginError):
    pass


class PluginNotFoundError(PluginError):
    pass


class PluginDisabledError(PluginError):
    pass


class ConfigError(CoreError):
    pass


class LoadProjectError(CoreError):
    pass


class ProjectNodeNotFoundError(CoreError):
    pass


class NetworkError(CoreError):
    pass
