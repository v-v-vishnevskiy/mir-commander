from typing import Any, Callable, Dict, List, Optional

from mir_commander.utils.config import Config


class Settings:
    """The class of Settings.

    Additionally implements functions for in-memory
    getting, setting and setting to default values,
    without touching the actual config file.
    Also provides methods for massive applying and restoring of settings.
    """

    def __init__(self, config: Config):
        self._config = config
        self._changes: Dict[str, Any] = {}
        self._applied_changes: Dict[str, Any] = {}
        self._defaults: Dict[str, Any] = {}
        self._apply_callbacks: Dict[str, List[Callable]] = {}
        self._restore_callbacks: Dict[str, Callable] = {}
        self._changed_callback: Callable = lambda: None

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any):
        self.set(key, value, False)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        if key in self._changes:
            return self._changes[key]
        elif self._config.contains(key):
            return self._config[key]
        else:
            return self._defaults.get(key, default)

    def set(self, key: str, value: Any, write: bool = True):
        current_value = self._config[key]
        if write:
            if current_value != value:
                self._config[key] = value
                for fn in self._apply_callbacks.get(key, []):
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
            if self._config[key] != value:
                self._changes[key] = value
        self._changed_callback()

    @property
    def has_changes(self) -> bool:
        return bool(self._changes)

    def set_changed_callback(self, fn: Callable):
        self._changed_callback = fn

    def add_apply_callback(self, key: str, fn: Callable):
        if key not in self._apply_callbacks:
            self._apply_callbacks[key] = []
        self._apply_callbacks[key].append(fn)

    def add_restore_callback(self, key: str, fn: Callable):
        self._restore_callbacks[key] = fn

    def apply(self, all: bool = False):
        if all:
            for callbacks in self._apply_callbacks.values():
                for fn in callbacks:
                    fn()
        else:
            for key in self._changes.keys():
                for fn in self._apply_callbacks.get(key, []):
                    fn()
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
            self._config[key] = value
