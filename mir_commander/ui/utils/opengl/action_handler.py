from typing import Any, Callable

from PySide6.QtCore import QTimer
from PySide6.QtGui import QKeyEvent, QMouseEvent

from .keymap import Keymap


class ActionHandler:
    def __init__(self, keymap: None | Keymap = None):
        self.keymap = keymap or Keymap(
            {
                "rotate_down": ["down"],
                "rotate_left": ["left"],
                "rotate_right": ["right"],
                "rotate_up": ["up"],
                "zoom_in": ["wheel_up", "="],
                "zoom_out": ["wheel_down", "-"],
            },
        )
        self._actions: dict[str, tuple[bool, Callable, tuple]] = {}
        self._to_repeat_actions: dict[str, tuple[Callable, tuple]] = {}
        self._repeatable_actions_timer = QTimer()
        self._repeatable_actions_timer.timeout.connect(self._call_action_timer)

    def add_action(self, action: str, repeatable: bool, fn: Callable, *args: Any):
        self._actions[action] = (repeatable, fn, args)

    def call_action(self, event: QKeyEvent | QMouseEvent | str, match_fn: Callable):
        action = match_fn(event)
        try:
            repeatable, fn, args = self._actions[action]
            if repeatable and isinstance(event, (QKeyEvent, QMouseEvent)):
                self._to_repeat_actions[action] = fn, args
                self._repeatable_actions_timer.start()
            else:
                fn(*args)
        except KeyError:
            pass

    def stop_action(self, event: QKeyEvent | QMouseEvent, match_fn: Callable):
        action = match_fn(event)
        try:
            repeatable, fn, args = self._actions[action]
            if repeatable and isinstance(event, (QKeyEvent, QMouseEvent)):
                del self._to_repeat_actions[action]
        except KeyError:
            pass

    def _call_action_timer(self):
        if not self._to_repeat_actions:
            self._repeatable_actions_timer.stop()
        else:
            for fn, args in self._to_repeat_actions.values():
                fn(*args)
