from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout

from mir_commander.ui.config import AppConfig

from .base import BasePage


class General(BasePage):
    """The page with the general settings.

    At this point only implements choosing language.
    The particular UI elements may migrate to other pages.
    """

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addLayout(self._language_ui)
        layout.addStretch(1)

        return layout

    def backup_data(self):
        self._backup["language"] = self.app_config.language

    def restore_backup_data(self):
        self.app_config.language = self._backup["language"]
        self.l_language_warning.setVisible(False)

    def restore_defaults(self):
        default_language = AppConfig().language
        language_changed = default_language != self._backup["language"]
        self.l_language_warning.setVisible(language_changed)
        self.app_config.language = default_language
        self.setup_data()

    def setup_data(self):
        self._setup_language_data()

    def post_init(self):
        self.cb_language.currentIndexChanged.connect(self._language_changed)

    @property
    def _language_ui(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        self._languages = [(self.tr("System"), "system"), ("English", "en"), ("Русский", "ru")]
        self.cb_language = QComboBox()
        for item in self._languages:
            self.cb_language.addItem(*item)

        self.l_language = QLabel(self.tr("Language:"))

        self.l_language_warning = QLabel(self.tr("Language will be changed after restarting the program"))
        self.l_language_warning.setStyleSheet("color: #FF6B00; font-style: italic;")
        self.l_language_warning.setVisible(False)

        layout.addWidget(self.l_language, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.cb_language, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.l_language_warning, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)

        return layout

    def _setup_language_data(self):
        index = self.cb_language.findData(self.app_config.language)
        self.cb_language.setCurrentIndex(index)

    @Slot()
    def _language_changed(self, index: int):
        new_language = self._languages[index][1]
        language_changed = new_language != self._backup["language"]
        self.l_language_warning.setVisible(language_changed)
        self.app_config.language = new_language  # type: ignore[assignment]
