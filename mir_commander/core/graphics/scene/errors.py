from mir_commander.core.errors import CoreError


class SceneError(CoreError):
    pass


class NodeError(SceneError):
    pass


class NodeParentError(SceneError):
    pass


class NodeNotFoundError(SceneError):
    pass
