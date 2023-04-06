from typing import Any, Callable, Dict, Optional

from PySide6.QtCore import QSettings


class Settings:
    def __init__(self, path: str):
        self._settings = QSettings(path, QSettings.Format.IniFormat)
        self._changes: Dict[str, Any] = {}
        self._applied_changes: Dict[str, Any] = {}
        self._defaults: Dict[str, Any] = {}
        self._apply_callbacks: Dict[str, Callable] = {}
        self._restore_callbacks: Dict[str, Callable] = {}
        self._changed_callback: Callable = lambda: None

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any):
        self.set(key, value, False)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        if key in self._changes:
            return self._changes[key]
        elif self._settings.contains(key):
            return self._settings.value(key)
        else:
            return self._defaults.get(key, default)

    def set(self, key: str, value: Any, write: bool = True):
        current_value = self._settings.value(key)
        if write:
            if current_value != value:
                self._settings.setValue(key, value)
                fn = self._apply_callbacks.get(key)
                if fn:
                    fn()
                if key in self._changes:
                    del self._changes[key]
        else:
            if current_value == value:
                if not self._applied_changes:
                    if key in self._changes:
                        del self._changes[key]
                elif key in self._applied_changes and self._applied_changes[key] == value:
                    if key in self._changes:
                        del self._changes[key]
                else:
                    self._changes[key] = value
            else:
                self._changes[key] = value
        self._changed_callback()

    def set_default(self, key: str, value: Any):
        self._defaults[key] = value

    def load_defaults(self):
        self._changes = {}
        for key, value in self._defaults.items():
            if self._settings.value(key) != value:
                self._changes[key] = value
        self._changed_callback()

    @property
    def has_changes(self) -> bool:
        return bool(self._changes)

    def set_changed_callback(self, fn: Callable):
        self._changed_callback = fn

    def add_apply_callback(self, key: str, fn: Callable):
        self._apply_callbacks[key] = fn

    def add_restore_callback(self, key: str, fn: Callable):
        self._restore_callbacks[key] = fn

    def apply(self, all: bool = False):
        if all:
            for fn in self._apply_callbacks.values():
                fn()
        else:
            for key in self._changes.keys():
                if key in self._apply_callbacks:
                    self._apply_callbacks[key]()
        self._applied_changes = self._changes
        self.clear()

    def restore(self, all: bool = False):
        if all:
            for fn in self._restore_callbacks.values():
                fn()
        else:
            for key in self._changes.keys():
                if key in self._restore_callbacks:
                    self._restore_callbacks[key]()

    def clear(self):
        self._changes = {}
        self._changed_callback()

    def write(self):
        keys = set(self._changes.keys()) | set(self._applied_changes.keys())
        for key in keys:
            value = self._changes.get(key) or self._applied_changes.get(key)
            self._settings.setValue(key, value)
