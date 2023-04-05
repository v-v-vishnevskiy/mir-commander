from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout

from mir_commander.widgets.settings.section import Section


class General(Section):
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addLayout(self._language_ui)
        layout.addStretch(1)

        return layout

    def setup_data(self):
        self._setup_language_data()

    @property
    def _language_ui(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        self.cb_language = QComboBox()

        layout.addWidget(QLabel(self.tr("Language:")), 0, Qt.AlignLeft)
        layout.addWidget(self.cb_language, 1, Qt.AlignLeft)

        return layout

    def _setup_language_data(self):
        self._languages = [(self.tr("System"), "system"), ("English", "en"), ("Русский", "ru")]
        language = self.settings.value("language", "system")
        current_index = 0
        for i, item in enumerate(self._languages):
            self.cb_language.addItem(*item)
            if item[1] == language:
                current_index = i
        self.cb_language.setCurrentIndex(current_index)
        self.cb_language.currentIndexChanged.connect(self._new_language)

    @Slot()
    def _new_language(self, index: int):
        self.settings.setValue("language", self._languages[index][1])
        # TODO: Show message about restart program
