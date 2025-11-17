from PySide6.QtCore import QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent
from PySide6.QtWidgets import QColorDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget


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


class _GroupHeaderWidget(QFrame):
    def __init__(self, title: str, layout_widget: "_GroupLayoutWidget"):
        super().__init__()

        self._parent = layout_widget

        self.setFixedHeight(20)
        self.setStyleSheet("QFrame { padding: 2px; background-color: #D0D0D0; }")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._icon = QFrame()
        self._icon.setFixedSize(16, 16)

        label = QLabel(title)
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
        if self._parent.expanded:
            self._icon.setStyleSheet("QFrame { image: url(:/core/icons/arrow-down.png); }")
        else:
            self._icon.setStyleSheet("QFrame { image: url(:/core/icons/arrow-right.png); }")

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._parent.toggle_expand()
        self._apply_style()
        event.accept()


class _GroupLayoutWidget(QVBoxLayout):
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

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
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


class GroupVBoxLayout(QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

    def add_widget(self, title: str, widget: QWidget, expanded: bool = True, *args, **kwargs):
        super().addLayout(_GroupLayoutWidget(title, widget, expanded), *args, **kwargs)
