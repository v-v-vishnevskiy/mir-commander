from typing import Literal

from pydantic import BaseModel, Field
from pydantic_extra_types.color import Color

from mir_commander.ui.utils.opengl.config import ProjectionConfig, TextOverlayConfig


class Background(BaseModel):
    color: Color = Color("#000000")


class Bond(BaseModel):
    radius: float = 0.1
    color: Literal["atoms"] | Color = "atoms"


class SpecialAtoms(BaseModel):
    atomic_radius: dict[int, float] = {-1: 0.15, -2: 0.25}
    atomic_color: dict[int, Color] = {-1: Color("#00FBFF"), -2: Color("#BB9451")}


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
    atomic_color: list[Color] = [
        Color("#00FBFF"),
        Color("#FFFFFF"),
        Color("#D9FFFF"),
        Color("#CC80FF"),
        Color("#C2FF00"),
        Color("#FFB5B5"),
        Color("#909090"),
        Color("#3050F8"),
        Color("#FF0D0D"),
        Color("#90E050"),
        Color("#B3E3F5"),
        Color("#AB5CF2"),
        Color("#8AFF00"),
        Color("#BFA6A6"),
        Color("#F0C8A0"),
        Color("#FF8000"),
        Color("#FFFF30"),
        Color("#1FF01F"),
        Color("#80D1E3"),
        Color("#8F40D4"),
        Color("#3DFF00"),
        Color("#E6E6E6"),
        Color("#BFC2C7"),
        Color("#A6A6AB"),
        Color("#8A99C7"),
        Color("#9C7AC7"),
        Color("#E06633"),
        Color("#F090A0"),
        Color("#50D050"),
        Color("#C88033"),
        Color("#7D80B0"),
        Color("#C28F8F"),
        Color("#668F8F"),
        Color("#BD80E3"),
        Color("#FFA100"),
        Color("#A62929"),
        Color("#5CB8D1"),
        Color("#702EB0"),
        Color("#00FF00"),
        Color("#94FFFF"),
        Color("#94E0E0"),
        Color("#73C2C9"),
        Color("#54B5B5"),
        Color("#3B9E9E"),
        Color("#248F8F"),
        Color("#0A7D8C"),
        Color("#006985"),
        Color("#C0C0C0"),
        Color("#FFD98F"),
        Color("#A67573"),
        Color("#668080"),
        Color("#9E63B5"),
        Color("#D47A00"),
        Color("#940094"),
        Color("#429EB0"),
        Color("#57178F"),
        Color("#00C900"),
        Color("#70D4FF"),
        Color("#FFFFC7"),
        Color("#D9FFC7"),
        Color("#C7FFC7"),
        Color("#A3FFC7"),
        Color("#8FFFC7"),
        Color("#61FFC7"),
        Color("#45FFC7"),
        Color("#30FFC7"),
        Color("#1FFFC7"),
        Color("#00FF9C"),
        Color("#00E675"),
        Color("#00D452"),
        Color("#00BF38"),
        Color("#00AB24"),
        Color("#4DC2FF"),
        Color("#4DA6FF"),
        Color("#2194D6"),
        Color("#267DAB"),
        Color("#266696"),
        Color("#175487"),
        Color("#D0D0E0"),
        Color("#FFD123"),
        Color("#B8B8D0"),
        Color("#A6544D"),
        Color("#575961"),
        Color("#9E4FB5"),
        Color("#AB5C00"),
        Color("#754F45"),
        Color("#428296"),
        Color("#420066"),
        Color("#007D00"),
        Color("#70ABFA"),
        Color("#00BAFF"),
        Color("#00A1FF"),
        Color("#008FFF"),
        Color("#0080FF"),
        Color("#006BFF"),
        Color("#545CF2"),
        Color("#785CE3"),
        Color("#8A4FE3"),
        Color("#A136D4"),
        Color("#B31FD4"),
        Color("#B31FBA"),
        Color("#B30DA6"),
        Color("#BD0D87"),
        Color("#C70066"),
        Color("#CC0059"),
        Color("#D1004F"),
        Color("#D90045"),
        Color("#E00038"),
        Color("#E6002E"),
        Color("#EB0026"),
        Color("#F00024"),
        Color("#F00024"),
        Color("#F00024"),
        Color("#F00024"),
        Color("#F00024"),
        Color("#F00024"),
        Color("#F00024"),
        Color("#F00024"),
        Color("#F00024"),
    ]
    special_atoms: SpecialAtoms = SpecialAtoms()


class Quality(BaseModel):
    mesh: float = Field(default=8, ge=1, le=100)
    smooth: bool = True


class SelectedAtom(BaseModel):
    color: Literal["atom"] | Color = Color("#94FFFF")
    scale_factor: float = Field(default=1.4, ge=1.1, le=3.0)
    opacity: float = Field(default=0.6, ge=0.01, le=0.99)


class Style(BaseModel):
    name: str
    projection: ProjectionConfig = ProjectionConfig()
    background: Background = Background()
    bond: Bond = Bond()
    atoms: Atoms = Atoms()
    quality: Quality = Quality()
    selected_atom: SelectedAtom = SelectedAtom()
    under_cursor_text_overlay: TextOverlayConfig = TextOverlayConfig(
        alignment=["center"],
        background_color=Color("#44444499"),
    )


class MenuKeymap(BaseModel):
    save_image: str = "s"
    toggle_projection: str = "ctrl+p"
    toggle_selected: str = "b"
    select_toggle_all: str = "a"
    calc_auto_parameter: str = "p"
    cloak_toggle_h_atoms: str = "h"
    next_atomic_coordinates: str = "ctrl+right"
    prev_atomic_coordinates: str = "ctrl+left"
    next_style: str = "ctrl+down"
    prev_style: str = "ctrl+up"


class ViewerKeymap(BaseModel):
    rotate_down: list[str] = ["down"]
    rotate_left: list[str] = ["left"]
    rotate_right: list[str] = ["right"]
    rotate_up: list[str] = ["up"]
    zoom_in: list[str] = ["wheel_up", "="]
    zoom_out: list[str] = ["wheel_down", "-"]
    toggle_atom_selection: list[str] = ["mb_1"]


class Keymap(BaseModel):
    menu: MenuKeymap = MenuKeymap()
    viewer: ViewerKeymap = ViewerKeymap()


class MolecularStructureViewerConfig(BaseModel):
    keymap: Keymap = Keymap()
    geom_bond_tolerance: float = 0.15
    size: tuple[int, int] = (500, 500)
    min_size: tuple[int, int] = (150, 150)
    current_style: str = "Colored Bonds"
    styles: list[Style] = Field(
        default=[
            Style(name="Colored Bonds"),
            Style(name="Simple", bond=Bond(color="#888888")),
            Style(
                name="Colored Bonds Only", 
                atoms=Atoms(radius="bond"),
                selected_atom=SelectedAtom(scale_factor=3.0),
            ),
        ],
        min_length=1,
        description="List of available styles for the molecular structure viewer.",
    )
