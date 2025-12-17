from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QComboBox, QGroupBox, QHBoxLayout, QLabel, QSpinBox, QVBoxLayout

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
        layout.addWidget(self._font_ui)
        layout.addStretch(1)

        return layout

    def backup_data(self):
        self._backup["language"] = self.app_config.language
        self._backup["font_family"] = self.app_config.font.family
        self._backup["font_size"] = self.app_config.font.size

    def restore_backup_data(self):
        self.app_config.language = self._backup["language"]
        self.l_language_warning.setVisible(False)
        self.app_config.font.family = self._backup["font_family"]
        self.app_config.font.size = self._backup["font_size"]
        self.l_font_warning.setVisible(False)

    def restore_defaults(self):
        default_config = AppConfig()
        default_language = default_config.language
        language_changed = default_language != self._backup["language"]
        self.l_language_warning.setVisible(language_changed)
        self.app_config.language = default_language

        default_font_family = default_config.font.family
        default_font_size = default_config.font.size
        font_changed = (
            default_font_family != self._backup["font_family"] or default_font_size != self._backup["font_size"]
        )
        self.l_font_warning.setVisible(font_changed)
        self.app_config.font.family = default_font_family
        self.app_config.font.size = default_font_size

        self.setup_data()

    def setup_data(self):
        self._setup_language_data()
        self._setup_font_data()

    def post_init(self):
        self.cb_language.currentIndexChanged.connect(self._language_changed)
        self.cb_font_family.currentIndexChanged.connect(self._font_changed)
        self.sb_font_size.valueChanged.connect(self._font_changed)

    @property
    def _language_ui(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        self._languages = [(self.tr("System"), "system"), ("English", "en"), ("Русский", "ru")]
        self.cb_language = QComboBox()
        for item in self._languages:
            self.cb_language.addItem(*item)

        self.l_language = QLabel(self.tr("Language:"))

        self.l_language_warning = QLabel(self.tr("Language will be changed after restarting the program"))
        self.l_language_warning.setObjectName("mircmd-warning")
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

    @property
    def _font_ui(self) -> QGroupBox:
        group_box = QGroupBox(self.tr("Font"))
        layout = QHBoxLayout()

        # Font family
        self._font_families = [
            (self.tr("System"), "system"),
            ("Inter", "inter"),
        ]
        self.cb_font_family = QComboBox()
        for item in self._font_families:
            self.cb_font_family.addItem(*item)

        self.l_font_family = QLabel(self.tr("Family:"))

        # Font size
        self.sb_font_size = QSpinBox()
        self.sb_font_size.setMinimum(8)
        self.sb_font_size.setMaximum(72)
        self.sb_font_size.setSuffix(" px")

        self.l_font_size = QLabel(self.tr("Size:"))

        # Warning label
        self.l_font_warning = QLabel(self.tr("Font will be changed after restarting the program"))
        self.l_font_warning.setObjectName("mircmd-warning")
        self.l_font_warning.setVisible(False)

        layout.addWidget(self.l_font_family, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.cb_font_family, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.l_font_size, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.sb_font_size, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.l_font_warning, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)

        group_box.setLayout(layout)
        return group_box

    def _setup_font_data(self):
        # Block signals to avoid triggering _font_changed during setup
        self.cb_font_family.blockSignals(True)
        self.sb_font_size.blockSignals(True)

        index = self.cb_font_family.findData(self.app_config.font.family)
        self.cb_font_family.setCurrentIndex(index)
        self.sb_font_size.setValue(self.app_config.font.size)

        # Update UI state based on current settings
        self._update_font_ui_state()

        # Unblock signals
        self.cb_font_family.blockSignals(False)
        self.sb_font_size.blockSignals(False)

    def _update_font_ui_state(self):
        """Update enabled/disabled state of font UI elements based on current settings."""
        is_system_font = self.app_config.font.family == "system"
        # Size spinbox is disabled when system font is selected
        self.sb_font_size.setEnabled(not is_system_font)
        self.l_font_size.setEnabled(not is_system_font)

    @Slot()
    def _font_changed(self):
        new_font_family = self._font_families[self.cb_font_family.currentIndex()][1]
        new_font_size = self.sb_font_size.value()

        font_changed = new_font_family != self._backup["font_family"] or new_font_size != self._backup["font_size"]
        self.l_font_warning.setVisible(font_changed)

        self.app_config.font.family = new_font_family  # type: ignore[assignment]
        self.app_config.font.size = new_font_size

        # Update UI state
        self._update_font_ui_state()
