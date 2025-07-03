from enum import Enum


class ClickAndMoveMode(Enum):
    Nothing = 0
    Rotation = 1


class WheelMode(Enum):
    Nothing = 0
    Scale = 1


class ProjectionMode(Enum):
    Orthographic = 1
    Perspective = 2 