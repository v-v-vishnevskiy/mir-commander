from .plugin import Details, Plugin


class ResourcesDetails(Details):
    pass


class ResourcesPlugin(Plugin):
    details: ResourcesDetails
