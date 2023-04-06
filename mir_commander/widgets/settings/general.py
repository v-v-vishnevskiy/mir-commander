from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout

from mir_commander.widgets.settings.category import Category


class General(Category):
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addLayout(self._language_ui)
        layout.addStretch(1)

        return layout

    def setup_data(self):
        self._setup_language_data()

    def restore_settings(self):
        print("General", self.settings["language"])
        index = self.cb_language.findData(self.settings["language"])
        self.cb_language.setCurrentIndex(index)

    def post_init(self):
        self.settings.add_restore_callback("language", self.restore_settings)

    def retranslate_ui(self):
        self.l_language.setText(self.tr("Language:"))
        self.cb_language.setItemText(0, self.tr("System"))

    @property
    def _language_ui(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        self.cb_language = QComboBox()
        self.l_language = QLabel()

        layout.addWidget(self.l_language, 0, Qt.AlignLeft)
        layout.addWidget(self.cb_language, 1, Qt.AlignLeft)

        return layout

    def _setup_language_data(self):
        self._languages = [("System", "system"), ("English", "en"), ("Русский", "ru")]
        language = self.settings["language"]
        current_index = 0
        self.cb_language.addItem(self.tr(self._languages[0][0]), self._languages[0][1])
        for i, item in enumerate(self._languages[1:], 1):
            self.cb_language.addItem(*item)
            if item[1] == language:
                current_index = i
        self.cb_language.setCurrentIndex(current_index)
        self.cb_language.currentIndexChanged.connect(self._language_changed)

    @Slot()
    def _language_changed(self, index: int):
        self.settings["language"] = self._languages[index][1]
