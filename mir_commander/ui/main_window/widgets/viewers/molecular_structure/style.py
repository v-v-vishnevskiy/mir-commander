from typing import Any

from PySide6.QtCore import QCoreApplication

from mir_commander.consts import DIR
from mir_commander.utils.config import Config


class Style:
    styles: dict[int, "Style"] = {}

    def __init__(self, default_style: Config, styles: list[Config]):
        self.__default_style = default_style
        self.__styles = styles
        self.__current = styles[0]

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

    @classmethod
    def style(cls, project) -> "Style":
        project_id = id(project)
        if project_id not in cls.styles:
            global_config = QCoreApplication.instance().config
            config = global_config.nested("widgets.viewers.molecular_structure")
            default_style = config.nested("style.default")

            styles = [default_style]
            for file in (DIR.CONFIG / "styles" / "viewers" / "molecule").glob("*.yaml"):
                style = Config(file)
                style.set_defaults(default_style)
                styles.append(style)
            styles.sort(key=lambda x: x["name"])

            style_instance = cls(default_style, styles)
            style_instance.set_style(config["style.current"])

            cls.styles[project_id] = style_instance
        return cls.styles[project_id]
