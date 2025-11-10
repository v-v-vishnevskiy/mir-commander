import logging
import logging.config
from logging import getLogger

from .consts import DIR


def setup():
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {"format": "%(levelname)-7s %(message)s"},
                "file": {"format": "%(asctime)s %(levelname)-7s %(name)s - %(message)s"},
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "console",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "file",
                    "filename": DIR.HOME_CONFIG / "logs.log",
                    "mode": "w",
                    "encoding": "utf-8",
                    "backupCount": 1,
                    "maxBytes": 5 * 1024 * 1024,
                },
            },
            "root": {"level": "DEBUG", "handlers": ["console", "file"]},
        }
    )
    logging.getLogger("cclib").setLevel(logging.CRITICAL)


__all__ = ["setup", "getLogger"]
