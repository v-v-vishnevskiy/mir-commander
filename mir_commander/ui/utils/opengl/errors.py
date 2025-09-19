class Error(Exception):
    pass


class NodeError(Error):
    pass


class NodeParentError(NodeError):
    pass


class NodeNotFoundError(NodeError):
    pass
