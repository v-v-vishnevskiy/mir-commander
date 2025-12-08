from importlib.metadata import version

try:
    __version__ = version("mir-commander")
except Exception:
    __version__ = "unknown"

if __name__ == "__main__":
    print(__version__)
