from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QPlainTextEdit,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from mir_commander import __version__


class About(QDialog):
    """Dialog with information about the program."""

    def __init__(self, license_text: str, *args, **kwargs):
        super().__init__(*args, **kwargs | dict(modal=True))

        layout = QVBoxLayout(self)
        layout.addLayout(self._header())
        layout.addWidget(self._tab_widget(license_text))

        self.setLayout(layout)

        self.setWindowTitle(self.tr("About Mir Commander"))

    def _header(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        label = QLabel()
        pixmap = QPixmap(":/core/icons/app.png")
        pixmap.setDevicePixelRatio(5.0)
        label.setPixmap(pixmap)
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(5)
        title_label = QLabel("Mir Commander")
        title_label.setObjectName("mircmd-about-title-label")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        version_label = QLabel(self.tr("Version {}").format(__version__))
        version_label.setObjectName("mircmd-about-version-label")
        layout.addWidget(version_label, alignment=Qt.AlignmentFlag.AlignCenter)
        return layout

    def _tab_widget(self, license_text: str) -> QTabWidget:
        widget = QTabWidget()
        widget.addTab(self._about_page(), self.tr("About"))
        widget.addTab(self._authors_page(), self.tr("Authors"))
        widget.addTab(self._license_page(license_text), self.tr("License"))
        return widget

    def _about_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(
            QLabel(
                self.tr(
                    "A modern, powerful graphical user interface for molecular structure modeling and investigation."
                ),
                wordWrap=True,
                textInteractionFlags=Qt.TextInteractionFlag.TextSelectableByMouse,
            ),
        )
        layout.addSpacing(20)
        grid_layout = QGridLayout()
        grid_layout.addWidget(QLabel(self.tr("Home Page:")), 0, 0)
        grid_layout.addWidget(self._create_link_label("https://mircmd.com/"), 0, 1)
        grid_layout.addWidget(QLabel(self.tr("Telegram News:")), 1, 0)
        grid_layout.addWidget(self._create_link_label("https://t.me/mir_commander"), 1, 1)
        grid_layout.setColumnStretch(1, 1)
        layout.addLayout(grid_layout)
        layout.addStretch(1)
        widget.setLayout(layout)
        return widget

    def _authors_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addLayout(self._create_author(self.tr("Yury V. Vishnevskiy"), "yu.v.vishnevskiy@gmail.com"))
        layout.addSpacing(30)
        layout.addLayout(self._create_author(self.tr("Valery V. Vishnevskiy"), "v.v.vishnevskiy@gmail.com"))
        layout.addStretch(1)
        widget.setLayout(layout)
        return widget

    def _license_page(self, license_text: str) -> QPlainTextEdit:
        widget = QPlainTextEdit(license_text)
        widget.setReadOnly(True)
        return widget

    def _create_author(self, name: str, email: str) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.addWidget(QLabel(name), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._create_link_label(email, is_email=True), alignment=Qt.AlignmentFlag.AlignCenter)
        return layout

    def _create_link_label(self, url: str, is_email: bool = False) -> QLabel:
        mail = "mailto:" if is_email else ""
        label = QLabel()
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction | Qt.TextInteractionFlag.TextSelectableByMouse
        )
        label.setText(f"<a href='{mail}{url}'>{url}</a>")
        label.setOpenExternalLinks(True)
        return label
