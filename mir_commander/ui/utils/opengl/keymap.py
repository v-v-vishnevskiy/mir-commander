from PySide6.QtGui import QKeyEvent, QKeySequence, QMouseEvent


class Keymap:
    def __init__(self, config: None | dict[str, str] = None):
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

    def load_from_config(self, config: dict[str, str]):
        for action, key in config.items():
            self.add(action, key)

    def match_key_event(self, event: QKeyEvent) -> None | str:
        key = QKeySequence(event.keyCombination()).toString().lower().replace("num+", "")
        return self._match(key)

    def match_mouse_event(self, event: QMouseEvent) -> None | str:
        return self._match(f"mb_{event.buttons().value}")

    def match_wheel_event(self, key: str) -> None | str:
        return self._match(key)
