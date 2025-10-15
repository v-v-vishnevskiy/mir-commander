from time import monotonic
from typing import Any, Self, cast

from PySide6.QtCore import QCoreApplication, QEvent, QObject, Qt
from PySide6.QtGui import QAction, QMouseEvent, QStandardItem
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDockWidget,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListView,
    QMenu,
    QPushButton,
    QSpinBox,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


class TrString(str):
    format_args: tuple[Any, ...] = tuple()
    format_kwargs: dict[str, Any] = dict()

    def format(self, *args: Any, **kwargs: Any) -> Self:
        self.format_args = args
        self.format_kwargs = kwargs
        return self


class Translator:
    """Translator class.

    Classes implementing widgets with translatable elements
    must inherit this class.
    """

    @staticmethod
    def tr(value: str, *args: Any, **kwargs: Any) -> TrString:
        return TrString(value)

    def _tr(self, text: str | TrString) -> str:
        if text and isinstance(text, TrString):
            return QCoreApplication.translate(self.__class__.__name__, text).format(
                *text.format_args, **text.format_kwargs
            )
        return text


class TR:
    @staticmethod
    def tr(value: str) -> str:
        return QCoreApplication.translate("TR", value)


class Widget(Translator):
    """
    A special class, which implements changeEvent handler.
    """

    def retranslate_ui(self):
        pass

    def changeEvent(self, event: QEvent):
        """Handling only LanguageChange events and calling retranslate_ui"""

        if event.type() == QEvent.Type.LanguageChange:
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
        self.__tooltip: str | None = None
        super().__init__(self._tr(text), parent)

    def setText(self, value: str):
        self.__text = value
        super().setText(self._tr(value))

    def setToolTip(self, value: str):
        self.__tooltip = value
        super().setToolTip(self._tr(value))

    def retranslate_ui(self):
        self.setText(self.__text)
        if self.__tooltip is not None:
            self.setToolTip(self.__tooltip)


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

    def addItem(self, text: str, /, userData: Any = None):  # type: ignore[override]
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
        root = self.model().invisibleRootItem()  # type: ignore[attr-defined]
        for i in range(root.rowCount()):
            root.child(i).retranslate()


class TreeView(Widget, QTreeView):
    def retranslate_ui(self):
        root = self.model().invisibleRootItem()  # type: ignore[attr-defined]
        self._retranslate(root)

    def _retranslate(self, root_item: QStandardItem):
        for i in range(root_item.rowCount()):
            for j in range(root_item.columnCount()):
                item = root_item.child(i, j)
                try:
                    item.retranslate()  # type: ignore[attr-defined]
                except AttributeError:
                    pass  # it can be a QStandardItem, which doesn't have a retranslate method
                if item.hasChildren():
                    self._retranslate(item)


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

    def addTab(self, page: QWidget, label: str, /):  # type: ignore[override]
        self.__labels.append(label)
        super().addTab(page, self._tr(label))

    def removeTab(self, index: int):
        self.__labels.pop(index)
        super().removeTab(index)

    def retranslate_ui(self):
        for i, label in enumerate(self.__labels):
            self.setTabText(i, self._tr(label))


class Action(Translator, QAction):
    def __init__(self, text: str, parent: QObject | None = None, *args, **kwargs):
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

    def set_enabled_actions(self, flag: bool):
        for action in self.actions():
            menu = cast(Menu, action.menu())
            if menu:
                menu.set_enabled_actions(flag)
            action.setEnabled(flag)

    def retranslate_ui(self):
        for action in self.actions():
            if isinstance(action, Action):
                action.retranslate()
        self.setTitle(self.__title)


class StatusBar(Widget, QStatusBar):
    def showMessage(self, message: str, timeout: int | None = 10000):
        self.__message = message
        self.__timeout = timeout
        self.__monotonic = monotonic()
        super().showMessage(self._tr(message), timeout)

    def retranslate_ui(self):
        if self.currentMessage():
            if self.__timeout is not None:
                timeout = self.__timeout - (int(monotonic() - self.__monotonic) * 1000)
            else:
                timeout = None
            self.showMessage(self.__message, timeout)


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


class _GroupHeaderWidget(QFrame):
    def __init__(self, title: str, layout_widget: "_GroupLayoutWidget"):
        super().__init__()

        self._parent = layout_widget

        self.setFixedHeight(20)
        self.setStyleSheet("QFrame { border: 0px solid black; padding: 2px; background-color: #D0D0D0; }")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._icon = QFrame()
        self._icon.setFixedSize(16, 16)

        label = Label(title)
        label.setStyleSheet("QLabel { padding: 0px; margin: 0px; }")

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._icon)
        layout.addSpacing(4)
        layout.addWidget(label)
        layout.addStretch()
        self.setLayout(layout)
        self._apply_style()

    def _apply_style(self):
        if self._parent.collapsed:
            self._icon.setStyleSheet("QFrame { image: url(:/icons/general/arrow-right.png); }")
        else:
            self._icon.setStyleSheet("QFrame { image: url(:/icons/general/arrow-down.png); }")

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._parent.toggle_collapse()
        self._apply_style()


class _GroupLayoutWidget(QVBoxLayout):
    def __init__(self, title: str, widget: QWidget, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._collapsed = False
        self._widget = widget

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        self.addWidget(_GroupHeaderWidget(title=title, layout_widget=self))
        self.addWidget(self._widget)

    @property
    def collapsed(self) -> bool:
        return self._collapsed

    def toggle_collapse(self):
        self._collapsed = not self._collapsed

        if self._collapsed:
            self._widget.hide()
            self.removeWidget(self._widget)
        else:
            self.insertWidget(1, self._widget)
            self._widget.show()


class GroupVBoxLayout(QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

    def add_widget(self, title: str, widget: QWidget, *args, **kwargs):
        super().addLayout(_GroupLayoutWidget(title, widget), *args, **kwargs)
