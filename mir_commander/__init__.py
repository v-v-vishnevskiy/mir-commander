from importlib.metadata import version

try:
    __version__ = version("mir-commander")
except Exception:
    __version__ = "unknown"
