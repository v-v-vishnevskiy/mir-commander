from PySide6.QtCore import QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent
from PySide6.QtWidgets import (
    QColorDialog,
    QDockWidget,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class DockWidget(QDockWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.BottomDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.setObjectName(f"Dock.{self._get_name()}")
        self.setContentsMargins(0, 0, 0, 0)

    def _get_name(self) -> str:
        return self.__class__.__name__


class ColorButton(QPushButton):
    color_changed = Signal(QColor)

    def __init__(self, color: QColor = QColor(255, 255, 255, a=255), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color = color
        self._set_style_sheet(color)
        self.clicked.connect(self.clicked_handler)

    @property
    def color(self) -> QColor:
        return self._color

    def _set_style_sheet(self, color: QColor):
        color_name = color.name(QColor.NameFormat.HexArgb) if self.isEnabled() else "gray"
        self.setStyleSheet(f"ColorButton {{ background-color: {color_name}; }}")

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


class StackItemHeader(QFrame):
    def __init__(self, title: str, layout_widget: "StackItemLayout"):
        super().__init__()

        self._parent = layout_widget

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._icon = QFrame()
        self._icon.setObjectName("mircmd-stack-item-header-icon")

        label = QLabel(title)
        label.setObjectName("mircmd-stack-item-header-label")

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
        self._icon.setProperty("expanded", self._parent.expanded)
        self._icon.style().polish(self._icon)
        self._icon.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._parent.toggle_expand()
        self._apply_style()
        event.accept()


class StackItemLayout(QVBoxLayout):
    def __init__(self, title: str, widget: QWidget, expanded: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setObjectName("mircmd-group-layout-widget-scroll-area")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(widget)

        self._expanded = expanded
        self._widget = widget
        self._widget_height = self._widget_current_height = self._widget.sizeHint().height()
        self._animation_max = QPropertyAnimation(scroll_area, b"maximumHeight")
        self._animation_max.setDuration(200)
        self._animation_min = QPropertyAnimation(scroll_area, b"minimumHeight")
        self._animation_min.setDuration(200)

        self.addWidget(StackItemHeader(title=title, layout_widget=self))
        self.addWidget(scroll_area)

        if self._expanded:
            scroll_area.setMinimumHeight(widget.sizeHint().height())
            scroll_area.setMaximumHeight(widget.sizeHint().height())
        else:
            scroll_area.setMinimumHeight(0)
            scroll_area.setMaximumHeight(0)

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


class VerticalStackLayout(QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

    def add_widget(self, title: str, widget: QWidget, expanded: bool = True, *args, **kwargs):
        super().addLayout(StackItemLayout(title, widget, expanded), *args, **kwargs)
