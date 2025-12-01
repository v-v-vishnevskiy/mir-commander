import sys
from pathlib import Path


class DIR:
    APP = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent.parent.parent
    HOME_CONFIG = Path.home() / ".mircmd"
    INTERNAL_PLUGINS = APP / "plugins"
    HOME_PLUGINS = HOME_CONFIG / "plugins"
    RESOURCES = APP / "resources"
