from typing import Any

from PySide6.QtCore import QPoint, QPropertyAnimation, QRect, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QMouseEvent, QRegion, QResizeEvent
from PySide6.QtWidgets import (
    QColorDialog,
    QDockWidget,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMdiSubWindow,
    QMenu,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class Link(QLabel):
    def __init__(self, text: str, url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._text = text
        self._url = url

        self.setTextFormat(Qt.TextFormat.RichText)
        self.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction | Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.setText(f"<a href='{url}'>{text}</a>")
        self.setOpenExternalLinks(True)

    def update_url(self, url: str):
        self._url = url
        self.setText(f"<a href='{url}'>{self._text}</a>")

    def update_text(self, text: str):
        self._text = text
        self.setText(f"<a href='{self._url}'>{text}</a>")


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

    def __init__(self, color: QColor = QColor(255, 255, 255, a=255), alpha: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color = color
        self._set_style_sheet(color)
        self.clicked.connect(self.clicked_handler)
        self._color_dialog_kwargs: dict[str, Any] = (
            {"options": QColorDialog.ColorDialogOption.ShowAlphaChannel} if alpha else {}
        )

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
        color = QColorDialog.getColor(initial=self._color, parent=self, **self._color_dialog_kwargs)
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
        if event.button() == Qt.MouseButton.LeftButton:
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


class TitleBarIcon(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setScaledContents(True)


class TitleBarButton(QPushButton):
    pass


class MdiSubWindowTitleBar(QFrame):
    def __init__(self, parent: QMdiSubWindow):
        super().__init__(parent)
        self._parent = parent
        self._drag_position = QPoint()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._icon = TitleBarIcon()

        self._title = QLabel()

        self._minimize_button = TitleBarButton()
        self._minimize_button.setObjectName("minimize")
        self._minimize_button.setProperty("active", False)
        self._minimize_button.clicked.connect(self._toggle_minimize)

        self._maximize_button = TitleBarButton()
        self._maximize_button.setObjectName("maximize")
        self._maximize_button.setProperty("active", False)
        self._maximize_button.clicked.connect(self._toggle_maximize)

        self._close_button = TitleBarButton()
        self._close_button.setObjectName("close")
        self._close_button.clicked.connect(self._close)

        layout.addWidget(self._icon, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addStretch()
        layout.addWidget(self._title, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addStretch()
        layout.addWidget(self._minimize_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._maximize_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._close_button, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.setLayout(layout)

    def _toggle_minimize(self):
        if self._parent.isMinimized():
            self._parent.showNormal()
        else:
            if self._parent.isMaximized():
                # PATCH: to really minimize the window, we need to show it normal first
                self._parent.showNormal()
            self._parent.showMinimized()

    def _toggle_maximize(self):
        if self._parent.isMaximized():
            self._parent.showNormal()
        else:
            if self._parent.isMinimized():
                # PATCH: to really maximize the window, we need to show it normal first
                self._parent.showNormal()
            self._parent.showMaximized()

    def _close(self):
        self._parent.close()

    def set_icon(self, icon: QIcon):
        self._icon.setPixmap(icon.pixmap(64, 64))

    def set_title(self, title: str):
        self._title.setText(title)

    def set_active(self, active: bool):
        self._title.setEnabled(active)
        self._icon.setEnabled(active)

    def update_state(self, state: Qt.WindowState):
        self._minimize_button.setProperty("active", False)
        self._maximize_button.setProperty("active", False)
        if state & Qt.WindowState.WindowMinimized:
            self._minimize_button.setProperty("active", True)
        elif state & Qt.WindowState.WindowMaximized:
            self._maximize_button.setProperty("active", True)

        self._minimize_button.style().polish(self._minimize_button)
        self._minimize_button.update()

        self._maximize_button.style().polish(self._maximize_button)
        self._maximize_button.update()

    def mousePressEvent(self, event: QMouseEvent):
        if self._parent.isMaximized() or self._parent.isMinimized():
            event.ignore()
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self._parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._parent.isMaximized() or self._parent.isMinimized():
            event.ignore()
            return

        if event.buttons() == Qt.MouseButton.LeftButton:
            self._parent.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximize()
            event.accept()


class MdiSubWindowBody(QFrame):
    def __init__(self, widget: QWidget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._widget = widget
        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addWidget(widget)
        self.setLayout(self._layout)


class ResizableContainer(QFrame):
    def __init__(self, parent: QMdiSubWindow):
        super().__init__(parent)
        self._parent = parent

        self._resize_edge = ""
        self._margin = 6

        self.setMouseTracking(True)

    def _get_resize_edge(self, pos: QPoint) -> str:
        rect = self.rect()
        x, y = pos.x(), pos.y()
        w, h = rect.width(), rect.height()
        m = self._margin

        on_left = x <= m
        on_right = x >= w - m
        on_top = y <= m
        on_bottom = y >= h - m

        if on_top and on_left:
            return "top_left"
        elif on_top and on_right:
            return "top_right"
        elif on_bottom and on_left:
            return "bottom_left"
        elif on_bottom and on_right:
            return "bottom_right"
        elif on_left:
            return "left"
        elif on_right:
            return "right"
        elif on_top:
            return "top"
        elif on_bottom:
            return "bottom"
        return ""

    def _update_cursor(self, edge: str):
        cursor_map = {
            "top": Qt.CursorShape.SizeVerCursor,
            "bottom": Qt.CursorShape.SizeVerCursor,
            "left": Qt.CursorShape.SizeHorCursor,
            "right": Qt.CursorShape.SizeHorCursor,
            "top_left": Qt.CursorShape.SizeFDiagCursor,
            "bottom_right": Qt.CursorShape.SizeFDiagCursor,
            "top_right": Qt.CursorShape.SizeBDiagCursor,
            "bottom_left": Qt.CursorShape.SizeBDiagCursor,
        }

        self.setCursor(cursor_map.get(edge, Qt.CursorShape.ArrowCursor))

    def _perform_resize(self, global_pos: QPoint):
        delta = global_pos - self._resize_start_mouse_pos
        new_geometry = QRect(self._resize_start_geometry)

        if "left" in self._resize_edge:
            new_geometry.setLeft(self._resize_start_geometry.left() + delta.x())
        if "right" in self._resize_edge:
            new_geometry.setRight(self._resize_start_geometry.right() + delta.x())
        if "top" in self._resize_edge:
            new_geometry.setTop(self._resize_start_geometry.top() + delta.y())
        if "bottom" in self._resize_edge:
            new_geometry.setBottom(self._resize_start_geometry.bottom() + delta.y())

        min_size = self._parent.minimumSize()
        if new_geometry.width() >= min_size.width() and new_geometry.height() >= min_size.height():
            self._parent.setGeometry(new_geometry)

    def resizeEvent(self, event: QResizeEvent):
        rect = self.rect()
        m = self._margin
        mask = QRegion(rect)
        mask -= QRegion(rect.adjusted(m, m, -m, -m))
        self.setMask(mask)
        super().resizeEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._parent.isMaximized() or self._parent.isMinimized():
            event.ignore()
            self.setCursor(Qt.CursorShape.ArrowCursor)
            return

        if self._resize_edge:
            self._perform_resize(event.globalPosition().toPoint())
            event.accept()
            return

        edge = self._get_resize_edge(event.position().toPoint())
        self._update_cursor(edge)

    def mousePressEvent(self, event: QMouseEvent):
        if self._parent.isMaximized() or self._parent.isMinimized():
            event.ignore()
            return

        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            edge = self._get_resize_edge(pos)
            if edge:
                self._resize_edge = edge
                self._resize_start_geometry = self._parent.geometry()
                self._resize_start_mouse_pos = event.globalPosition().toPoint()
                self.grabMouse()
                event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self._resize_edge:
            self._resize_edge = ""
            self.releaseMouse()

            # Update cursor after releasing
            edge = self._get_resize_edge(event.position().toPoint())
            self._update_cursor(edge)

            event.accept()


class NotificationButton(QPushButton):
    pass


class Notification(QWidget):
    def __init__(self, text: QLabel, actions: list[QWidget], options: QMenu | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setCursor(Qt.CursorShape.ArrowCursor)

        self._close_button = NotificationButton()
        self._close_button.setObjectName("close")
        self._close_button.clicked.connect(self.hide)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        self.setLayout(layout)

        header_layout = QHBoxLayout()
        # header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(text)

        self._options = options
        if options:
            self._options_button = NotificationButton()
            self._options_button.setObjectName("options")
            self._options_button.clicked.connect(self._show_options_menu)
            header_layout.addWidget(self._options_button)
        header_layout.addWidget(self._close_button)

        layout.addLayout(header_layout)

        actions_layout = QHBoxLayout()
        # actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.addStretch(1)
        for action in actions:
            actions_layout.addSpacing(10)
            actions_layout.addWidget(action)

        layout.addLayout(actions_layout)

        self._shadow_effect = QGraphicsDropShadowEffect(self)
        self._shadow_effect.setBlurRadius(30)
        self._shadow_effect.setColor(QColor(0, 0, 0, 100))
        self._shadow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self._shadow_effect)

        self.adjustSize()

        self.hide()

    def _show_options_menu(self):
        if self._options:
            self._options.exec(self.mapToGlobal(self._options_button.pos()))

    def show(self):
        self.raise_()
        self.adjustSize()
        super().show()

    def update_position(self):
        if widget := self.parentWidget():
            parent_rect = widget.rect()
            my_height = self.height()

            margin_x = 20
            margin_y = 40

            y = parent_rect.height() - my_height - margin_y

            self.move(margin_x, y)
