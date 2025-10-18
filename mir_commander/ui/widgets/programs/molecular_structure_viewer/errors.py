class Error(Exception):
    pass


class CalcError(Error):
    pass


class EmptyScalarFieldError(Error):
    pass


class SurfaceNotFoundError(Error):
    pass
