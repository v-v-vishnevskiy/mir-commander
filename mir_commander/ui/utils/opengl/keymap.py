from PySide6.QtGui import QKeyEvent, QKeySequence, QMouseEvent


class Keymap:
    _instances: dict[int, "Keymap"] = {}

    def __new__(cls, key: int, config: None | dict[str, list[str]] = None) -> "Keymap":
        """
        This function is required to prevent re-reading config files when each new window is created.
        :param key: unique value
        :param config:
        """
        if key not in cls._instances:
            cls._instances[key] = super().__new__(cls)
        return cls._instances[key]

    def __init__(self, key: int, config: None | dict[str, list[str]] = None):
        self._map: dict[str, str] = {}

        if config is not None:
            self.load_from_config(config)

    def _match(self, key: str) -> None | str:
        try:
            return self._map[key]
        except KeyError:
            return None

    def add(self, action: str, key: str):
        # sorting the sequence
        ranks = {"meta": 0, "ctrl": 1, "alt": 2, "shift": 3}
        key = "+".join(sorted(key.replace(" ", "").split("+"), key=lambda x: ranks.get(x, 9999)))

        self._map[key] = action

    def load_from_config(self, config: dict[str, list[str]]):
        for action, keys in config.items():
            for key in keys:
                self.add(action, key)

    def match_key_event(self, event: QKeyEvent) -> None | str:
        key = QKeySequence(event.keyCombination()).toString().lower().replace("num+", "")
        return self._match(key)

    def match_mouse_event(self, event: QMouseEvent) -> None | str:
        return self._match(f"mb_{event.button().value}")

    def match_wheel_event(self, key: str) -> None | str:
        return self._match(key)
