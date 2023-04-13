import os

from PySide6.QtCore import QDir, QLocale, QTranslator
from PySide6.QtWidgets import QApplication

from mir_commander.recent_projects import RecentProjects
from mir_commander.settings import Settings

CONFIG_DIR = os.path.join(QDir.homePath(), ".mircmd")


class Application(QApplication):
    """Application class. In fact, only one instance is created thereof."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.translator = QTranslator(self)
        self.settings = Settings(os.path.join(CONFIG_DIR, "config"))
        self.recent_projects = RecentProjects(os.path.join(CONFIG_DIR, "recent.json"))
        self.set_translation()

        self.settings.set_default("language", "system")
        self.settings.add_apply_callback("language", self.set_translation)

    def set_translation(self):
        """The callback called by the Settings when a setting is applied or set."""

        language = self.settings["language"]
        if language == "system":
            language = QLocale.languageToCode(QLocale.system().language())

        self.removeTranslator(self.translator)
        i18n_path = os.path.join(os.path.dirname(__file__), "..", "resources", "i18n")
        if not self.translator.load(os.path.join(i18n_path, f"app_{language}")):
            self.translator.load(os.path.join(i18n_path, "app_en"))
        self.installTranslator(self.translator)
