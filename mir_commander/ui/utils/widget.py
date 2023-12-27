from time import monotonic
from typing import Any

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtGui import QAction, QStandardItem
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDockWidget,
    QGroupBox,
    QLabel,
    QListView,
    QMenu,
    QPushButton,
    QSpinBox,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QWidget,
)


class TrString(str):
    pass


class Translator:
    """Translator class.

    Classes implementing widgets with translatable elements
    must inherit this class.
    """

    @staticmethod
    def tr(value: str) -> TrString:
        return TrString(value)

    def _tr(self, text: str) -> str:
        if not text:
            return text
        return QCoreApplication.translate(self.__class__.__name__, text) if isinstance(text, TrString) else text


class Widget(Translator):
    """
    A special class, which implements changeEvent handler.
    """

    def retranslate_ui(self):
        pass

    def changeEvent(self, event: QEvent):
        """Handling only LanguageChange events and calling retranslate_ui"""

        if event.type() == QEvent.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)  # type: ignore


class Dialog(Widget, QDialog):
    def setWindowTitle(self, value: str):
        self.__window_title = value
        super().setWindowTitle(self._tr(value))

    def retranslate_ui(self):
        self.setWindowTitle(self.__window_title)


class DockWidget(Widget, QDockWidget):
    def __init__(self, title: str, parent: QWidget | None = None):
        self.__title = title
        super().__init__(self._tr(title), parent)

    def setWindowTitle(self, value: str):
        self.__title = value
        super().setWindowTitle(self._tr(value))

    def retranslate_ui(self):
        self.setWindowTitle(self.__title)


class Label(Widget, QLabel):
    def __init__(self, text: str, parent: QWidget | None = None):
        self.__text = text
        super().__init__(self._tr(text), parent)

    def setText(self, value: str):
        self.__text = value
        super().setText(self._tr(value))

    def retranslate_ui(self):
        self.setText(self.__text)


class PushButton(Widget, QPushButton):
    def __init__(self, text: str, parent: QWidget | None = None):
        self.__text = text
        super().__init__(self._tr(text), parent)

    def setText(self, value: str):
        self.__text = value
        super().setText(self._tr(value))

    def retranslate_ui(self):
        self.setText(self.__text)


class GroupBox(Widget, QGroupBox):
    def __init__(self, text: str, parent: QWidget | None = None):
        self.__text = text
        super().__init__(self._tr(text), parent)

    def setTitle(self, value: str):
        self.__text = value
        super().setTitle(self._tr(value))

    def retranslate_ui(self):
        self.setTitle(self.__text)


class CheckBox(Widget, QCheckBox):
    def __init__(self, text: str, parent: QWidget | None = None):
        self.__text = text
        super().__init__(self._tr(text), parent)

    def setText(self, value: str):
        self.__text = value
        super().setText(self._tr(value))

    def retranslate_ui(self):
        self.setText(self.__text)


class SpinBox(Widget, QSpinBox):
    def __init__(self, parent: QWidget | None = None):
        self.__suffix = ""
        super().__init__(parent)

    def setSuffix(self, value: str):
        self.__suffix = value
        super().setSuffix(self._tr(value))

    def retranslate_ui(self):
        if self.__suffix:
            self.setSuffix(self.__suffix)


class ComboBox(Widget, QComboBox):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.__items: list[str] = []

    def addItem(self, text: str, userData: Any = None):
        self.__items.append(text)
        super().addItem(self._tr(text), userData)

    def removeItem(self, index: int):
        self.__items.pop(index)
        super().removeItem(index)

    def retranslate_ui(self):
        for i, text in enumerate(self.__items):
            self.setItemText(i, self._tr(text))


class ListView(Widget, QListView):
    def retranslate_ui(self):
        root = self.model().invisibleRootItem()
        for i in range(root.rowCount()):
            root.child(i).retranslate()


class StandardItem(Translator, QStandardItem):
    def __init__(self, text: str):
        super().__init__(self._tr(text))
        self.__text = text

    def retranslate(self):
        super().setText(self._tr(self.__text))

    def setText(self, text: str):
        self.__text = text
        super().setText(self._tr(text))


class TabWidget(Widget, QTabWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.__labels: list[str] = []

    def addTab(self, page: QWidget, label: str):
        self.__labels.append(label)
        super().addTab(page, self._tr(label))

    def removeTab(self, index: int):
        self.__labels.pop(index)
        super().removeTab(index)

    def retranslate_ui(self):
        for i, label in enumerate(self.__labels):
            self.setTabText(i, self._tr(label))


class Action(Translator, QAction):
    def __init__(self, text: str, parent: QWidget | None = None, *args, **kwargs):
        super().__init__(self._tr(text), parent, *args, **kwargs)
        self.__text = text

    def retranslate(self):
        super().setText(self._tr(self.__text))

    def setText(self, text: str):
        self.__text = text
        super().setText(self._tr(text))


class Menu(Widget, QMenu):
    def __init__(self, title: str = "", parent: QWidget | None = None):
        super().__init__(self._tr(title), parent)
        self.__title = title

    def setTitle(self, title: str):
        self.__title = title
        super().setTitle(self._tr(title))

    def set_enabled(self, flag: bool):
        for action in self.actions():
            menu = action.menu()
            if menu:
                menu.set_enabled(flag)
            action.setEnabled(flag)

    def retranslate_ui(self):
        for action in self.actions():
            if isinstance(action, Action):
                action.retranslate()
        self.setTitle(self.__title)


class StatusBar(Widget, QStatusBar):
    def showMessage(self, message: str, timeout: int = 0):
        self.__message = message
        self.__timeout = timeout
        self.__monotonic = monotonic()
        super().showMessage(self._tr(message), timeout)

    def retranslate_ui(self):
        if self.currentMessage():
            self.showMessage(self.__message, self.__timeout - (int(monotonic() - self.__monotonic) * 1000))


class ToolBar(Widget, QToolBar):
    def __init__(self, title: str = "", parent: QWidget | None = None):
        super().__init__(self._tr(title), parent)
        self.__title = title

    def setTitle(self, title: str):
        self.__title = title
        super().setWindowTitle(self._tr(title))

    def retranslate_ui(self):
        for action in self.actions():
            if isinstance(action, Action):
                action.retranslate()
        self.setTitle(self.__title)
