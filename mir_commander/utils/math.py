from math import acos, sqrt


def geom_distance_xyz(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float):
    return sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2) + (z1 - z2) * (z1 - z2))


def geom_angle_xyz(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, x3: float, y3: float, z3: float):
    r1 = geom_distance_xyz(x1, y1, z1, x2, y2, z2)
    r2 = geom_distance_xyz(x2, y2, z2, x3, y3, z3)
    r3 = geom_distance_xyz(x1, y1, z1, x3, y3, z3)

    angle = (r1 * r1 + r2 * r2 - r3 * r3) / (2.0 * r1 * r2)
    if angle < -1.0 or angle > 1.0:
        return 0.0
    else:
        return acos(angle)
