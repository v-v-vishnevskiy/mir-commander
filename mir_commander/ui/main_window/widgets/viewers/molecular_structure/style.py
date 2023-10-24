from typing import Any

from mir_commander.consts import DIR
from mir_commander.utils.config import Config


class Style:
    _instances: dict[int, "Style"] = {}

    def __new__(cls, key: int, config: Config) -> "Style":
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

        self.__default_style = default_style
        self.__styles = styles
        self.__current = styles[0]
        self.set_style(config["style.current"])

    def __getitem__(self, key: str) -> Any:
        return self.__current[key]

    def set_style(self, name: str):
        for style in self.__styles:
            if style["name"] == name:
                self.__current = style
                break
        else:
            self.__current = self.__default_style

    def __set_style(self, index: int) -> int:
        i_min = 0
        i_max = len(self.__styles) - 1

        i = min(i_max, max(i_min, index))
        self.__current = self.__styles[i]
        return i

    def set_prev_style(self) -> bool:
        name_current = self.__current["name"]
        for i, style in enumerate(self.__styles):
            if style["name"] == name_current:
                return self.__set_style(i - 1) != i
        return False

    def set_next_style(self) -> bool:
        name_current = self.__current["name"]
        for i, style in enumerate(self.__styles):
            if style["name"] == name_current:
                return self.__set_style(i + 1) != i
        return False
