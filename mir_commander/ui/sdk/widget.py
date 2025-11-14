from time import monotonic
from typing import Any, Self, cast

from PySide6.QtCore import QCoreApplication, QEvent, QObject, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QAction, QColor, QMouseEvent, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDockWidget,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListView,
    QMenu,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStatusBar,
    QTableView,
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

    @classmethod
    def translate(cls, text: str | TrString) -> str:
        if text and isinstance(text, TrString):
            return QCoreApplication.translate(cls.__name__, text).format(*text.format_args, **text.format_kwargs)
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
        super().setWindowTitle(self.translate(value))

    def retranslate_ui(self):
        self.setWindowTitle(self.__window_title)


class DockWidget(Widget, QDockWidget):
    """The basic class for dockable widgets.

    Has been created as a wrapper of QDockWidget
    for simple handling of translation.
    """

    def __init__(self, title: str, *args, **kwargs):
        self.__title = title
        super().__init__(self.translate(title), *args, **kwargs)

        self.setObjectName(f"Dock.{self.__class__.__name__}")
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.BottomDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.setContentsMargins(0, 0, 0, 0)

    def setWindowTitle(self, value: str):
        self.__title = value
        super().setWindowTitle(self.translate(value))

    def retranslate_ui(self):
        self.setWindowTitle(self.__title)


class Label(Widget, QLabel):
    def __init__(self, text: str, parent: QWidget | None = None):
        self.__text = text
        self.__tooltip: str | None = None
        super().__init__(self.translate(text), parent)

    def setText(self, value: str):
        self.__text = value
        super().setText(self.translate(value))

    def setToolTip(self, value: str):
        self.__tooltip = value
        super().setToolTip(self.translate(value))

    def retranslate_ui(self):
        self.setText(self.__text)
        if self.__tooltip is not None:
            self.setToolTip(self.__tooltip)


class PushButton(Widget, QPushButton):
    def __init__(self, text: str, parent: QWidget | None = None):
        self.__text = text
        super().__init__(self.translate(text), parent)

    def setText(self, value: str):
        self.__text = value
        super().setText(self.translate(value))

    def retranslate_ui(self):
        self.setText(self.__text)


class ColorButton(QPushButton):
    color_changed = Signal(QColor)

    def __init__(self, color: QColor = QColor(255, 255, 255, a=255), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color = color
        self._set_style_sheet(color)
        self.setFixedSize(20, 20)
        self.clicked.connect(self.clicked_handler)

    @property
    def color(self) -> QColor:
        return self._color

    def _set_style_sheet(self, color: QColor):
        enabled = self.isEnabled()
        color_name = color.name(QColor.NameFormat.HexArgb) if enabled else "gray"
        border_color = "black" if enabled else "gray"
        self.setStyleSheet(
            f"QPushButton {{ border: 1px solid {border_color}; margin: 1px;background-color: {color_name}; }}"
        )

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self._set_style_sheet(self._color)

    def set_color(self, color: QColor):
        self._color = color
        self._set_style_sheet(color)

    def clicked_handler(self):
        color = QColorDialog.getColor(
            initial=self._color, parent=self, options=QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        if color.isValid():
            self._color = color
            self._set_style_sheet(color)
            self.color_changed.emit(color)


class GroupBox(Widget, QGroupBox):
    def __init__(self, text: str, parent: QWidget | None = None):
        self.__text = text
        super().__init__(self.translate(text), parent)

    def setTitle(self, value: str):
        self.__text = value
        super().setTitle(self.translate(value))

    def retranslate_ui(self):
        self.setTitle(self.__text)


class CheckBox(Widget, QCheckBox):
    def __init__(self, text: str, parent: QWidget | None = None):
        self.__text = text
        super().__init__(self.translate(text), parent)

    def setText(self, value: str):
        self.__text = value
        super().setText(self.translate(value))

    def retranslate_ui(self):
        self.setText(self.__text)


class SpinBox(Widget, QSpinBox):
    def __init__(self, parent: QWidget | None = None):
        self.__suffix = ""
        super().__init__(parent)

    def setSuffix(self, value: str):
        self.__suffix = value
        super().setSuffix(self.translate(value))

    def retranslate_ui(self):
        if self.__suffix:
            self.setSuffix(self.__suffix)


class ComboBox(Widget, QComboBox):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.__items: list[str] = []

    def addItem(self, text: str, /, userData: Any = None):  # type: ignore[override]
        self.__items.append(text)
        super().addItem(self.translate(text), userData)

    def removeItem(self, index: int):
        self.__items.pop(index)
        super().removeItem(index)

    def retranslate_ui(self):
        for i, text in enumerate(self.__items):
            self.setItemText(i, self.translate(text))


class ListView(Widget, QListView):
    def retranslate_ui(self):
        model = cast(QStandardItemModel, self.model())
        root = model.invisibleRootItem()
        for i in range(root.rowCount()):
            item = root.child(i)
            if isinstance(item, StandardItem):
                item.retranslate()


class TableView(Widget, QTableView):
    def retranslate_ui(self):
        model = cast(QStandardItemModel, self.model())

        for i in range(self.horizontalHeader().count()):
            item = model.horizontalHeaderItem(i)
            if isinstance(item, StandardItem):
                item.retranslate()

        for row in range(model.rowCount()):
            for column in range(model.columnCount()):
                item = model.item(row, column)
                if isinstance(item, StandardItem):
                    item.retranslate()


class TreeView(Widget, QTreeView):
    def retranslate_ui(self):
        model = cast(QStandardItemModel, self.model())
        root = model.invisibleRootItem()
        self._retranslate(root)

    def _retranslate(self, root_item: QStandardItem):
        for i in range(root_item.rowCount()):
            for j in range(root_item.columnCount()):
                item = root_item.child(i, j)
                if isinstance(item, StandardItem):
                    item.retranslate()
                if item.hasChildren():
                    self._retranslate(item)


class StandardItem(Translator, QStandardItem):
    def __init__(self, text: str):
        super().__init__(self.translate(text))
        self.__text = text

    def retranslate(self):
        super().setText(self.translate(self.__text))

    def setText(self, text: str):
        self.__text = text
        super().setText(self.translate(text))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(text={self.text()})"


class TabWidget(Widget, QTabWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.__labels: list[str] = []

    def addTab(self, page: QWidget, label: str, /):  # type: ignore[override]
        self.__labels.append(label)
        super().addTab(page, self.translate(label))

    def removeTab(self, index: int):
        self.__labels.pop(index)
        super().removeTab(index)

    def retranslate_ui(self):
        for i, label in enumerate(self.__labels):
            self.setTabText(i, self.translate(label))


class Action(Translator, QAction):
    def __init__(self, text: str, parent: QObject | None = None, *args, **kwargs):
        super().__init__(self.translate(text), parent, *args, **kwargs)
        self.__text = text

    def retranslate(self):
        super().setText(self.translate(self.__text))

    def setText(self, text: str):
        self.__text = text
        super().setText(self.translate(text))


class Menu(Widget, QMenu):
    def __init__(self, title: str = "", parent: QWidget | None = None):
        super().__init__(self.translate(title), parent)
        self.__title = title

    def setTitle(self, title: str):
        self.__title = title
        super().setTitle(self.translate(title))

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
        super().showMessage(self.translate(message), timeout)

    def retranslate_ui(self):
        if self.currentMessage():
            if self.__timeout is not None:
                timeout = self.__timeout - (int(monotonic() - self.__monotonic) * 1000)
            else:
                timeout = None
            self.showMessage(self.__message, timeout)


class ToolBar(Widget, QToolBar):
    def __init__(self, title: str = "", parent: QWidget | None = None):
        super().__init__(self.translate(title), parent)
        self.__title = title

    def setTitle(self, title: str):
        self.__title = title
        super().setWindowTitle(self.translate(title))

    def retranslate_ui(self):
        for action in self.actions():
            if isinstance(action, Action):
                action.retranslate()
        self.setTitle(self.__title)


class GridLayout(QGridLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(5)


class VBoxLayout(QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)


class HBoxLayout(QHBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)


class _GroupHeaderWidget(QFrame):
    def __init__(self, title: str, layout_widget: "_GroupLayoutWidget"):
        super().__init__()

        self._parent = layout_widget

        self.setFixedHeight(20)
        self.setStyleSheet("QFrame { padding: 2px; background-color: #D0D0D0; }")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._icon = QFrame()
        self._icon.setFixedSize(16, 16)

        label = Label(title)
        label.setStyleSheet("QLabel { padding: 0px; margin: 0px; }")

        layout = HBoxLayout()
        layout.addWidget(self._icon)
        layout.addSpacing(4)
        layout.addWidget(label)
        layout.addStretch()
        self.setLayout(layout)
        self._apply_style()

    def _apply_style(self):
        if self._parent.expanded:
            self._icon.setStyleSheet("QFrame { image: url(:/core/icons/arrow-down.png); }")
        else:
            self._icon.setStyleSheet("QFrame { image: url(:/core/icons/arrow-right.png); }")

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._parent.toggle_expand()
        self._apply_style()
        event.accept()


class _GroupLayoutWidget(VBoxLayout):
    def __init__(self, title: str, widget: QWidget, expanded: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setWidget(widget)
        self._scroll_area.setFrameStyle(QFrame.Shape.NoFrame)

        self._expanded = expanded
        self._widget = widget
        self._widget.setContentsMargins(5, 5, 5, 10)
        self._widget_height = self._widget_current_height = self._widget.sizeHint().height()
        self._animation_max = QPropertyAnimation(self._scroll_area, b"maximumHeight")
        self._animation_max.setDuration(200)
        self._animation_min = QPropertyAnimation(self._scroll_area, b"minimumHeight")
        self._animation_min.setDuration(200)

        self.addWidget(_GroupHeaderWidget(title=title, layout_widget=self))
        self.addWidget(self._scroll_area)

        if self._expanded:
            self._scroll_area.setMinimumHeight(widget.sizeHint().height())
            self._scroll_area.setMaximumHeight(widget.sizeHint().height())
        else:
            self._scroll_area.setMinimumHeight(0)
            self._scroll_area.setMaximumHeight(0)

    @property
    def expanded(self) -> bool:
        return self._expanded

    def toggle_expand(self):
        self._expanded = not self._expanded

        if self._expanded:
            # Expand the group
            self._animation_min.setStartValue(0)
            self._animation_max.setStartValue(0)
            self._animation_min.setEndValue(self._widget_height)
            self._animation_max.setEndValue(self._widget_height)
            self._animation_max.start()
            self._animation_min.start()
        else:
            # Collapse the group
            self._widget_height = self._widget.sizeHint().height()
            self._animation_max.setStartValue(self._widget_height)
            self._animation_min.setStartValue(self._widget_height)
            self._animation_max.setEndValue(0)
            self._animation_min.setEndValue(0)
        self._animation_max.start()
        self._animation_min.start()


class GroupVBoxLayout(VBoxLayout):
    def add_widget(self, title: str, widget: QWidget, expanded: bool = True, *args, **kwargs):
        super().addLayout(_GroupLayoutWidget(title, widget, expanded), *args, **kwargs)
