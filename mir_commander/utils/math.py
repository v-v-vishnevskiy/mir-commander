import math


def geom_distance_xyz(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float):
    """
    Calculate and return distance between two points 1-2 defined by Cartesian coordinates xyz1 and xyz2
    """
    return math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2) + (z1 - z2) * (z1 - z2))


def geom_angle_xyz(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, x3: float, y3: float, z3: float):
    """
    Calculate and return angle (in radians) between two lines defined by three points 1-2-3
    with Cartesian coordinates xyz1, xyz2 and xyz3
    """
    r1 = geom_distance_xyz(x1, y1, z1, x2, y2, z2)
    r2 = geom_distance_xyz(x2, y2, z2, x3, y3, z3)
    r3 = geom_distance_xyz(x1, y1, z1, x3, y3, z3)

    angle = (r1 * r1 + r2 * r2 - r3 * r3) / (2.0 * r1 * r2)
    if angle < -1.0 or angle > 1.0:
        return 0.0
    else:
        return math.acos(angle)


def geom_torsion_angle_xyz(
    x1: float,
    y1: float,
    z1: float,
    x2: float,
    y2: float,
    z2: float,
    x3: float,
    y3: float,
    z3: float,
    x4: float,
    y4: float,
    z4: float,
):
    """
    Calculate and return torsion angle (in radians) between two planes defined by four points 1-2-3-4
    (forming planes 1-2-3 and 2-3-4) with Cartesian coordinates xyz1, xyz2, xyz3 and xyz4.
    """
    xba = x2 - x1
    yba = y2 - y1
    zba = z2 - z1

    xcb = x3 - x2
    ycb = y3 - y2
    zcb = z3 - z2

    xdc = x4 - x3
    ydc = y4 - y3
    zdc = z4 - z3

    xt = yba * zcb - ycb * zba
    yt = xcb * zba - xba * zcb
    zt = xba * ycb - xcb * yba

    xu = ycb * zdc - ydc * zcb
    yu = xdc * zcb - xcb * zdc
    zu = xcb * ydc - xdc * ycb

    rt2 = xt * xt + yt * yt + zt * zt
    ru2 = xu * xu + yu * yu + zu * zu
    rtru = math.sqrt(rt2 * ru2)

    if rtru < 1.0e-12:
        return 0.0
    else:
        cosine = (xt * xu + yt * yu + zt * zu) / rtru
        cosine = min(1.0, max(-1.0, cosine))

    geometry = math.acos(cosine)
    xt = xba * xu + yba * yu + zba * zu
    if xt < 0.0:
        geometry = -geometry

    return geometry


def geom_oop_angle_xyz(
    x1: float,
    y1: float,
    z1: float,
    x2: float,
    y2: float,
    z2: float,
    x3: float,
    y3: float,
    z3: float,
    x4: float,
    y4: float,
    z4: float,
):
    """
    Calculate and return out-of-plane angle (in radians) between a plane defined by three points 2-3-4
    and a vector defined by two points 1-3:
          n1 - o.o.p
          |
          n3
         /  \
       n2    n4
    """
    x23 = x2 - x3
    y23 = y2 - y3
    z23 = z2 - z3

    x43 = x4 - x3
    y43 = y4 - y3
    z43 = z4 - z3

    x13 = x1 - x3
    y13 = y1 - y3
    z13 = z1 - z3

    # t - vector of multiplication of vectors 23x43
    xt = y23 * z43 - y43 * z23
    yt = x43 * z23 - x23 * z43
    zt = x23 * y43 - x43 * y23

    rt2 = xt * xt + yt * yt + zt * zt
    ru2 = x13 * x13 + y13 * y13 + z13 * z13
    rtru = math.sqrt(rt2 * ru2)

    if rtru < 1.0e-12:
        return 0.0
    else:
        cosine = (xt * x13 + yt * y13 + zt * z13) / rtru
        cosine = min(1.0, max(-1.0, cosine))
        geometry = math.pi / 2.0 - math.acos(cosine)

    return geometry
