from typing import Any

from .config import MolecularStructureViewerConfig


class Style:
    def __init__(self, config: MolecularStructureViewerConfig):
        self._styles = config.styles
        self.current = config.styles[0]
        self.set_style(config.current_style)

    def __getitem__(self, index: int) -> Any:
        return self.current[index]

    def set_style(self, name: str):
        for style in self._styles:
            if style.name == name:
                self.current = style
                break
        else:
            self.current = self._styles[0]

    def _set_style(self, index: int) -> int:
        i_min = 0
        i_max = len(self._styles) - 1

        i = min(i_max, max(i_min, index))
        self.current = self._styles[i]
        return i

    def set_prev_style(self) -> bool:
        for i, style in enumerate(self._styles):
            if style.name == self.current.name:
                return self._set_style(i - 1) != i
        return False

    def set_next_style(self) -> bool:
        for i, style in enumerate(self._styles):
            if style.name == self.current.name:
                return self._set_style(i + 1) != i
        return False
