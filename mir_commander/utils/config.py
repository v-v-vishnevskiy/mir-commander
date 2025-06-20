import logging
from pathlib import Path
from typing import Any, Literal, Optional

import yaml
from pydantic import BaseModel, Field

from mir_commander import exceptions

logger = logging.getLogger(__name__)


class Toolbars(BaseModel):
    icon_size: int = 20


class Tree(BaseModel):
    icon_size: int = 20


class ProjectDock(BaseModel):
    tree: Tree = Tree()


class Docks(BaseModel):
    project: ProjectDock = ProjectDock()


class Keymap(BaseModel):
    item_next: list[str] = ["ctrl+right"]
    item_prev: list[str] = ["ctrl+left"]
    style_next: list[str] = ["ctrl+down"]
    style_prev: list[str] = ["ctrl+up"]
    rotate_down: list[str] = ["down"]
    rotate_left: list[str] = ["left"]
    rotate_right: list[str] = ["right"]
    rotate_up: list[str] = ["up"]
    save_image: list[str] = ["s"]
    toggle_atom_selection: list[str] = ["mb_1"]
    toggle_projection: list[str] = ["p"]
    zoom_in: list[str] = ["wheel_up", "="]
    zoom_out: list[str] = ["wheel_down", "-"]


class Projection(BaseModel):
    mode: Literal["perspective", "orthographic"] = "perspective"
    fov: float = Field(
        default=45.0, ge=35.0, le=90.0, description="works with perspective mode only"
    )


class Background(BaseModel):
    color: str = "#000000"


class Quality(BaseModel):
    mesh: int = Field(default=10, ge=1, le=100)
    smooth: bool = True


class Bond(BaseModel):
    radius: float = 0.1
    color: str = "atoms"  # or hex variant "#AABBCC"


class SpecialAtoms(BaseModel):
    atomic_radius: dict[int, float] = {-1: 0.15, -2: 0.25}
    atomic_color: dict[int, str] = {-1: "#00FBFF", -2: "#BB9451"}


class Atoms(BaseModel):
    scale_factor: float = 1
    radius: Literal["atomic", "bond"] = "atomic"
    atomic_radius: list[float] = [
        0.1,
        0.15,
        0.17,
        0.20,
        0.22,
        0.24,
        0.26,
        0.28,
        0.30,
        0.32,
        0.34,
        0.30,
        0.32,
        0.34,
        0.36,
        0.38,
        0.40,
        0.42,
        0.44,
        0.40,
        0.41,
        0.42,
        0.43,
        0.44,
        0.45,
        0.46,
        0.47,
        0.48,
        0.49,
        0.50,
        0.51,
        0.52,
        0.53,
        0.54,
        0.55,
        0.56,
        0.57,
        0.50,
        0.51,
        0.52,
        0.53,
        0.54,
        0.55,
        0.56,
        0.57,
        0.58,
        0.59,
        0.60,
        0.61,
        0.62,
        0.63,
        0.64,
        0.65,
        0.66,
        0.67,
        0.60,
        0.61,
        0.62,
        0.62,
        0.62,
        0.62,
        0.62,
        0.62,
        0.62,
        0.62,
        0.62,
        0.62,
        0.62,
        0.62,
        0.62,
        0.62,
        0.62,
        0.63,
        0.64,
        0.65,
        0.66,
        0.67,
        0.68,
        0.69,
        0.70,
        0.71,
        0.72,
        0.73,
        0.74,
        0.75,
        0.76,
        0.77,
        0.70,
        0.71,
        0.72,
        0.72,
        0.72,
        0.72,
        0.72,
        0.72,
        0.72,
        0.72,
        0.72,
        0.72,
        0.72,
        0.72,
        0.72,
        0.72,
        0.72,
        0.73,
        0.74,
        0.75,
        0.76,
        0.77,
        0.78,
        0.79,
        0.80,
        0.81,
        0.82,
        0.83,
        0.84,
        0.85,
        0.86,
        0.87,
    ]
    atomic_color: list[str] = [
        "#00FBFF",
        "#FFFFFF",
        "#D9FFFF",
        "#CC80FF",
        "#C2FF00",
        "#FFB5B5",
        "#909090",
        "#3050F8",
        "#FF0D0D",
        "#90E050",
        "#B3E3F5",
        "#AB5CF2",
        "#8AFF00",
        "#BFA6A6",
        "#F0C8A0",
        "#FF8000",
        "#FFFF30",
        "#1FF01F",
        "#80D1E3",
        "#8F40D4",
        "#3DFF00",
        "#E6E6E6",
        "#BFC2C7",
        "#A6A6AB",
        "#8A99C7",
        "#9C7AC7",
        "#E06633",
        "#F090A0",
        "#50D050",
        "#C88033",
        "#7D80B0",
        "#C28F8F",
        "#668F8F",
        "#BD80E3",
        "#FFA100",
        "#A62929",
        "#5CB8D1",
        "#702EB0",
        "#00FF00",
        "#94FFFF",
        "#94E0E0",
        "#73C2C9",
        "#54B5B5",
        "#3B9E9E",
        "#248F8F",
        "#0A7D8C",
        "#006985",
        "#C0C0C0",
        "#FFD98F",
        "#A67573",
        "#668080",
        "#9E63B5",
        "#D47A00",
        "#940094",
        "#429EB0",
        "#57178F",
        "#00C900",
        "#70D4FF",
        "#FFFFC7",
        "#D9FFC7",
        "#C7FFC7",
        "#A3FFC7",
        "#8FFFC7",
        "#61FFC7",
        "#45FFC7",
        "#30FFC7",
        "#1FFFC7",
        "#00FF9C",
        "#00E675",
        "#00D452",
        "#00BF38",
        "#00AB24",
        "#4DC2FF",
        "#4DA6FF",
        "#2194D6",
        "#267DAB",
        "#266696",
        "#175487",
        "#D0D0E0",
        "#FFD123",
        "#B8B8D0",
        "#A6544D",
        "#575961",
        "#9E4FB5",
        "#AB5C00",
        "#754F45",
        "#428296",
        "#420066",
        "#007D00",
        "#70ABFA",
        "#00BAFF",
        "#00A1FF",
        "#008FFF",
        "#0080FF",
        "#006BFF",
        "#545CF2",
        "#785CE3",
        "#8A4FE3",
        "#A136D4",
        "#B31FD4",
        "#B31FBA",
        "#B30DA6",
        "#BD0D87",
        "#C70066",
        "#CC0059",
        "#D1004F",
        "#D90045",
        "#E00038",
        "#E6002E",
        "#EB0026",
        "#F00024",
        "#F00024",
        "#F00024",
        "#F00024",
        "#F00024",
        "#F00024",
        "#F00024",
        "#F00024",
        "#F00024",
    ]
    special_atoms: SpecialAtoms = SpecialAtoms()


class Style(BaseModel):
    name: str = "Colored Bonds"
    projection: Projection = Projection()
    background: Background = Background()
    quality: Quality = Quality()
    bond: Bond = Bond()
    atoms: Atoms = Atoms()


class StyleConfig(BaseModel):
    current: str = "Colored Bonds"
    default: Style = Style()


class MolecularStructureViewer(BaseModel):
    keymap: Keymap = Keymap()
    geom_bond_tol: float = 0.15
    antialiasing: bool = True
    size: tuple[int, int] = (500, 500)
    min_size: tuple[int, int] = (150, 150)
    style: StyleConfig = StyleConfig()


class Viewers(BaseModel):
    molecular_structure: MolecularStructureViewer = MolecularStructureViewer()


class Widgets(BaseModel):
    toolbars: Toolbars = Toolbars()
    docks: Docks = Docks()
    viewers: Viewers = Viewers()


class Validator(BaseModel):
    type: None | str = None
    language: Literal["system", "en", "ru"] = "system"
    widgets: Widgets = Widgets()


class Config:
    def __init__(
        self, path: None | Path = None, key: str = "", parent: Optional["Config"] = None, read_only: bool = False
    ) -> None:
        self._path = path
        self._data: dict[str, Any] = {}
        self._nested_key = key
        self._defaults: None | "Config" = None
        self._parent = parent
        self._read_only = read_only

        if self._path:
            self._path = self._path.resolve()

        if parent is None:
            self._load()

    def _key(self, key: str) -> list[str]:
        if not isinstance(key, str):
            raise exceptions.ConfigKey(f"Invalid type: {type(key)}")

        if not key:
            raise exceptions.ConfigKey("Empty")

        parts = key.split(".")
        for part in parts:
            if not part:
                raise exceptions.ConfigKey("Empty part")

        return parts

    def _load(self) -> None:
        if self._path is not None and self._path.exists():
            try:
                with self._path.open("r") as f:
                    data = f.read()
            except IsADirectoryError:
                logger.error(f"Trying to load directory: {self._path}")
                return

            if not data:
                return

            try:
                data = yaml.load(data, Loader=yaml.CLoader)
                validator = Validator.model_validate(data, strict=False)
                self._data = validator.model_dump()
            except yaml.YAMLError:
                logger.error(f"Invalid YAML format: {self._path}")
                return

    def set_defaults(self, config: "Config") -> None:
        if self._parent is None:
            self._defaults = config
        else:
            raise exceptions.Config("Can't set defaults for nested config")

    def dump(self) -> None:
        if self._parent is not None:
            self._parent.dump()
        elif self._path is not None and self._read_only is False:
            if not self._path.exists():
                Path(self._path.parts[0]).mkdir(parents=True, exist_ok=True)
            data = yaml.dump(self._data, Dumper=yaml.CDumper, allow_unicode=True)
            with self._path.open("w") as f:
                f.write(data)

    def nested(self, key: str) -> "Config":
        return Config(self._path, key=key, parent=self, read_only=self._read_only)

    def contains(self, key: str) -> bool:
        """Checks whether exist value with that key.

        :param key: a sequence of keys split by dot "." sign. Example: "widgets.toolbars.icon_size"
        :return: returns True if values exists by presented key else returns False
        """
        if self._parent is not None:
            return self._parent.contains(f"{self._nested_key}.{key}")
        else:
            data = self._data
            try:
                for part in self._key(key):
                    data = data[part]
                return True
            except KeyError:
                if self._defaults:
                    return self._defaults.contains(key)
                return False
            except TypeError:
                return False

    def get(self, key: str, default: Any = None) -> Any:
        if self._parent is not None:
            return self._parent.get(f"{self._nested_key}.{key}", default)
        else:
            data = self._data
            try:
                for part in self._key(key):
                    data = data[part]
                return data
            except KeyError:
                if self._defaults:
                    return self._defaults.get(key, default)
                else:
                    return default

    def set(self, key: str, value: Any, write: bool = True) -> None:
        if self._parent is not None:
            self._parent.set(f"{self._nested_key}.{key}", value, write)
        else:
            parts = self._key(key)
            data = self._data

            for i, part in enumerate(parts[:-1]):
                if part not in data:
                    data[part] = {}
                elif not isinstance(data[part], dict):
                    data[part] = {}
                    logger.warning(f"""Replace value for '{".".join(parts[0:i + 1])}' path on object""")
                data = data[part]

            data[parts[-1]] = value

            if write:
                self.dump()

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value, False)

    def __repr__(self) -> str:
        if self._nested_key:
            return f'{self.__class__.__name__}("{self._path}", key="{self._nested_key}", read_only={self._read_only})'
        else:
            return f'{self.__class__.__name__}("{self._path}", read_only={self._read_only})'
