from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from mir_commander.core.graphics.utils import color_to_qcolor

from .config import TextOverlayConfig


class TextOverlay(QWidget):
    def __init__(self, parent: QWidget, config: TextOverlayConfig, text: str = ""):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        self._config = config
        self._text = text
        self._label = QLabel(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self._label)

        self.set_config(config)
        self._update_text()

    def _get_alignment(self):
        alignment = 0
        if "left" in self._config.text_alignment:
            alignment |= Qt.AlignmentFlag.AlignLeft
        if "right" in self._config.text_alignment:
            alignment |= Qt.AlignmentFlag.AlignRight
        if "top" in self._config.text_alignment:
            alignment |= Qt.AlignmentFlag.AlignTop
        if "bottom" in self._config.text_alignment:
            alignment |= Qt.AlignmentFlag.AlignBottom
        if "center" in self._config.text_alignment:
            alignment |= Qt.AlignmentFlag.AlignCenter
        return alignment

    def _get_font(self):
        font = QFont()
        font.setPointSize(self._config.font_size)
        font.setBold(self._config.font_bold)
        font.setFamily(self._config.font_family)
        return font

    def _update_size(self):
        temp_label = QLabel()
        temp_label.setFont(self._get_font())
        temp_label.setText(self._text)
        temp_label.setWordWrap(True)

        size = temp_label.sizeHint()

        self.resize(size.width() + 20, size.height() + 20)

    def _update_colors(self):
        style = f"""
            QLabel {{
                color: rgb({self._color.red()}, {self._color.green()}, {self._color.blue()});
                background-color: rgba({self._background_color.red()}, {self._background_color.green()},
                                        {self._background_color.blue()}, {self._background_color.alpha()});
                border-radius: 5px;
                padding: 2px;
            }}
        """

        self._label.setStyleSheet(style)

    def _update_text(self):
        self._label.setText(self._text)
        self._update_size()

    def set_config(self, config: TextOverlayConfig, skip_position: bool = False):
        self._config = config

        self._color = color_to_qcolor(config.color, alpha=False)
        self._background_color = color_to_qcolor(config.background_color)

        if not skip_position:
            self.move(QPoint(*config.position))

        self._update_colors()
        self._label.setAlignment(self._get_alignment())
        self._label.setFont(self._get_font())
        self._update_text()

    def set_text(self, text: str):
        self._text = text
        self._update_text()

    def set_position(self, position: QPoint):
        self.move(position)
