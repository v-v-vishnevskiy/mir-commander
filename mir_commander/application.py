import os

from PySide6.QtCore import QDir, QLocale, QTranslator
from PySide6.QtWidgets import QApplication

from mir_commander.settings import Settings


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.translator = QTranslator(self)
        self.settings = Settings(os.path.join(QDir.homePath(), ".mircmd", "config"))
        self.set_translation()

        self.settings.set_default("language", "system")
        self.settings.add_apply_callback("language", self.set_translation)

    def set_translation(self):
        language = self.settings["language"]
        if language == "system":
            language = QLocale.languageToCode(QLocale.system().language())

        self.removeTranslator(self.translator)
        if not self.translator.load(f"../resources/i18n/app_{language}", os.path.dirname(__file__)):
            self.translator.load("../resources/i18n/app_en", os.path.dirname(__file__))
        self.installTranslator(self.translator)
