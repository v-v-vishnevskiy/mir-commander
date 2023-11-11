from typing import Any

from mir_commander.consts import DIR
from mir_commander.utils.config import Config


class Style:
    _instances: dict[int, "Style"] = {}

    def __new__(cls, key: int, config: Config) -> "Style":
        """
        This function is required to prevent re-reading config files when each new window is created.
        :param key: unique value
        :param config:
        """
        if key not in cls._instances:
            cls._instances[key] = super().__new__(cls)
        return cls._instances[key]

    def __init__(self, key: int, config: Config):
        default_style = config.nested("style.default")

        styles = [default_style]
        for file in (DIR.CONFIG / "styles" / "viewers" / "molecule").glob("*.yaml"):
            style = Config(file)
            style.set_defaults(default_style)
            styles.append(style)
        styles.sort(key=lambda x: x["name"])

        self._default_style = default_style
        self._styles = styles
        self._current = styles[0]
        self.set_style(config["style.current"])

    def __getitem__(self, key: str) -> Any:
        return self._current[key]

    def set_style(self, name: str):
        for style in self._styles:
            if style["name"] == name:
                self._current = style
                break
        else:
            self._current = self._default_style

    def _set_style(self, index: int) -> int:
        i_min = 0
        i_max = len(self._styles) - 1

        i = min(i_max, max(i_min, index))
        self._current = self._styles[i]
        return i

    def set_prev_style(self) -> bool:
        name_current = self._current["name"]
        for i, style in enumerate(self._styles):
            if style["name"] == name_current:
                return self._set_style(i - 1) != i
        return False

    def set_next_style(self) -> bool:
        name_current = self._current["name"]
        for i, style in enumerate(self._styles):
            if style["name"] == name_current:
                return self._set_style(i + 1) != i
        return False
