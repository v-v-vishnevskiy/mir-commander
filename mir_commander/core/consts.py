import sys
from pathlib import Path

FROZEN = getattr(sys, "frozen", False)


class DIR:
    APP = Path(sys.executable).parent if FROZEN else Path(__file__).parent.parent.parent
    HOME_MIRCMD = Path.home() / ".mircmd"
    MIRCMD_BIN = HOME_MIRCMD / "bin"
    MIRCMD_PLUGINS = HOME_MIRCMD / "plugins"
    MIRCMD_LOGS = HOME_MIRCMD / "logs"
    INTERNAL_PLUGINS = APP / "plugins"
    RESOURCES = APP / "resources"
