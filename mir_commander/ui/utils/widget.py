from typing import Optional

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QDialog, QDockWidget, QLabel, QPushButton, QWidget


class Translator:
    """Translator class.

    A special class, which implements changeEvent handler.
    Classes implementing widgets with translatable elements
    must inherit this class.
    """

    @staticmethod
    def tr(value: str):
        return value

    def _tr(self, value: str) -> str:
        return QCoreApplication.translate(self.__class__.__name__, value)

    def retranslate_ui(self):
        pass

    def changeEvent(self, event: QEvent):
        """Handling only LanguageChange events and calling retranslate_ui"""

        if event.type() == QEvent.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)  # type: ignore


class Dialog(Translator, QDialog):
    def setWindowTitle(self, value: str):
        self.__window_title = value
        super().setWindowTitle(self._tr(value))

    def retranslate_ui(self):
        self.setWindowTitle(self.__window_title)


class DockWidget(Translator, QDockWidget):
    def __init__(self, title: str, parent: Optional[QWidget] = None):
        self.__title = title
        super().__init__(self._tr(title), parent)

    def setWindowTitle(self, value: str):
        self.__title = value
        super().setWindowTitle(self._tr(value))

    def retranslate_ui(self):
        self.setWindowTitle(self.__title)


class Label(Translator, QLabel):
    def __init__(self, text: str, parent: Optional[QWidget] = None):
        self.__text = text
        super().__init__(self._tr(text), parent)

    def setText(self, value: str):
        self.__text = value
        super().setText(self._tr(value))

    def retranslate_ui(self):
        self.setText(self.__text)


class PushButton(Translator, QPushButton):
    def __init__(self, text: str, parent: Optional[QWidget] = None):
        self.__text = text
        super().__init__(self._tr(text), parent)

    def setText(self, value: str):
        self.__text = value
        super().setText(self._tr(value))

    def retranslate_ui(self):
        self.setText(self.__text)
