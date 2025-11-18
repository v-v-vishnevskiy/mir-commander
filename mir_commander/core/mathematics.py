import math

from .algebra import Vector3D


def geom_angle_xyz(p1: Vector3D, p2: Vector3D, p3: Vector3D) -> float:
    """
    Calculate and return angle (in radians) between two lines defined by three points 1-2-3
    with Cartesian coordinates p1, p2 and p3
    """
    r1 = p1.distance_to_point(p2)
    r2 = p2.distance_to_point(p3)
    r3 = p1.distance_to_point(p3)

    angle = (r1 * r1 + r2 * r2 - r3 * r3) / (2.0 * r1 * r2)
    if angle < -1.0 or angle > 1.0:
        return 0.0
    else:
        return math.acos(angle)


def geom_torsion_angle_xyz(p1: Vector3D, p2: Vector3D, p3: Vector3D, p4: Vector3D) -> float:
    """
    Calculate and return torsion angle (in radians) between two planes defined by four points 1-2-3-4
    (forming planes 1-2-3 and 2-3-4) with Cartesian coordinates p1, p2, p3 and p4.
    """
    ba = p2 - p1
    cb = p3 - p2
    dc = p4 - p3

    xt = ba.y * cb.z - cb.y * ba.z
    yt = cb.x * ba.z - ba.x * cb.z
    zt = ba.x * cb.y - cb.x * ba.y

    xu = cb.y * dc.z - dc.y * cb.z
    yu = dc.x * cb.z - cb.x * dc.z
    zu = cb.x * dc.y - dc.x * cb.y

    rt2 = xt * xt + yt * yt + zt * zt
    ru2 = xu * xu + yu * yu + zu * zu
    rtru = math.sqrt(rt2 * ru2)

    if rtru < 1.0e-12:
        return 0.0
    else:
        cosine = (xt * xu + yt * yu + zt * zu) / rtru
        cosine = min(1.0, max(-1.0, cosine))

    geometry = math.acos(cosine)
    xt = ba.x * xu + ba.y * yu + ba.z * zu
    if xt < 0.0:
        geometry = -geometry

    return geometry


def geom_oop_angle_xyz(p1: Vector3D, p2: Vector3D, p3: Vector3D, p4: Vector3D) -> float:
    """
    Calculate and return out-of-plane angle (in radians) between a plane defined by three points 2-3-4
    and a vector defined by two points 1-3:
          n1 - o.o.p
          |
          n2
         /  \
       n3    n4
    """
    p32 = p3 - p2
    p42 = p4 - p2
    p12 = p1 - p2

    # t - vector of multiplication of vectors 32x42
    xt = p32.y * p42.z - p42.y * p32.z
    yt = p42.x * p32.z - p32.x * p42.z
    zt = p32.x * p42.y - p42.x * p32.y

    rt2 = xt * xt + yt * yt + zt * zt
    ru2 = p12.x * p12.x + p12.y * p12.y + p12.z * p12.z
    rtru = math.sqrt(rt2 * ru2)

    if rtru < 1.0e-12:
        return 0.0
    else:
        cosine = (xt * p12.x + yt * p12.y + zt * p12.z) / rtru
        cosine = min(1.0, max(-1.0, cosine))
        geometry = math.pi / 2.0 - math.acos(cosine)

    return geometry
