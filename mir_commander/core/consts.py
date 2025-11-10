from pathlib import Path


class DIR:
    APP = Path(__file__).parent.parent.parent
    HOME_CONFIG = Path.home() / ".mircmd"
    INTERNAL_PLUGINS = APP / "plugins"
    HOME_PLUGINS = HOME_CONFIG / "plugins"
    RESOURCES = APP / "resources"
    ICONS = RESOURCES / "icons"
    TRANSLATIONS = RESOURCES / "i18n"
    FONTS = RESOURCES / "fonts"
