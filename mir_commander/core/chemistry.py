from functools import cache

BOHR2ANGSTROM = 0.529177210903  # 2018 CODATA


_symbols = [
    (-1, "X", 0.0),
    (-2, "Q", 0.0),
    (1, "H", 0.32),
    (2, "He", 0.46),
    (3, "Li", 1.33),
    (4, "Be", 1.02),
    (5, "B", 0.85),
    (6, "C", 0.75),
    (7, "N", 0.71),
    (8, "O", 0.63),
    (9, "F", 0.64),
    (10, "Ne", 0.67),
    (11, "Na", 1.55),
    (12, "Mg", 1.39),
    (13, "Al", 1.26),
    (14, "Si", 1.16),
    (15, "P", 1.11),
    (16, "S", 1.03),
    (17, "Cl", 0.99),
    (18, "Ar", 0.96),
    (19, "K", 1.96),
    (20, "Ca", 1.71),
    (21, "Sc", 1.48),
    (22, "Ti", 1.36),
    (23, "V", 1.34),
    (24, "Cr", 1.22),
    (25, "Mn", 1.19),
    (26, "Fe", 1.16),
    (27, "Co", 1.11),
    (28, "Ni", 1.1),
    (29, "Cu", 1.12),
    (30, "Zn", 1.18),
    (31, "Ga", 1.24),
    (32, "Ge", 1.21),
    (33, "As", 1.21),
    (34, "Se", 1.16),
    (35, "Br", 1.14),
    (36, "Kr", 1.17),
    (37, "Rb", 2.1),
    (38, "Sr", 1.85),
    (39, "Y", 1.63),
    (40, "Zr", 1.54),
    (41, "Nb", 1.47),
    (42, "Mo", 1.38),
    (43, "Tc", 1.28),
    (44, "Ru", 1.25),
    (45, "Rh", 1.25),
    (46, "Pd", 1.2),
    (47, "Ag", 1.28),
    (48, "Cd", 1.36),
    (49, "In", 1.42),
    (50, "Sn", 1.4),
    (51, "Sb", 1.4),
    (52, "Te", 1.36),
    (53, "I", 1.33),
    (54, "Xe", 1.31),
    (55, "Cs", 2.32),
    (56, "Ba", 1.96),
    (57, "La", 1.8),
    (58, "Ce", 1.63),
    (59, "Pr", 1.76),
    (60, "Nd", 1.74),
    (61, "Pm", 1.73),
    (62, "Sm", 1.72),
    (63, "Eu", 1.68),
    (64, "Gd", 1.69),
    (65, "Tb", 1.68),
    (66, "Dy", 1.67),
    (67, "Ho", 1.66),
    (68, "Er", 1.65),
    (69, "Tm", 1.64),
    (70, "Yb", 1.7),
    (71, "Lu", 1.62),
    (72, "Hf", 1.52),
    (73, "Ta", 1.46),
    (74, "W", 1.37),
    (75, "Re", 1.31),
    (76, "Os", 1.29),
    (77, "Ir", 1.22),
    (78, "Pt", 1.23),
    (79, "Au", 1.24),
    (80, "Hg", 1.33),
    (81, "Tl", 1.44),
    (82, "Pb", 1.44),
    (83, "Bi", 1.51),
    (84, "Po", 1.45),
    (85, "At", 1.47),
    (86, "Rn", 1.42),
    (87, "Fr", 2.23),
    (88, "Ra", 2.01),
    (89, "Ac", 1.86),
    (90, "Th", 1.75),
    (91, "Pa", 1.69),
    (92, "U", 1.7),
    (93, "Np", 1.71),
    (94, "Pu", 1.72),
    (95, "Am", 1.66),
    (96, "Cm", 1.66),
    (97, "Bk", 1.68),
    (98, "Cf", 1.68),
    (99, "Es", 1.65),
    (100, "Fm", 1.67),
    (101, "Md", 1.73),
    (102, "No", 1.76),
    (103, "Lr", 1.61),
    (104, "Rf", 1.57),
    (105, "Db", 1.49),
    (106, "Sg", 1.43),
    (107, "Bh", 1.41),
    (108, "Hs", 1.34),
    (109, "Mt", 1.29),
    (110, "Ds", 1.28),
    (111, "Rg", 1.21),
    (112, "Cn", 0.0),
    (113, "Nh", 0.0),
    (114, "Fl", 0.0),
    (115, "Mc", 0.0),
    (116, "Lv", 0.0),
    (117, "Ts", 0.0),
    (118, "Og", 0.0),
]

_symbols_map = {symbol.lower(): atomic_number for atomic_number, symbol, _ in _symbols}
_atomic_numbers_map = {atomic_number: (symbol, radius) for atomic_number, symbol, radius in _symbols}


def atomic_number_to_symbol(atomic_number: int) -> str:
    try:
        return _atomic_numbers_map[atomic_number][0]
    except KeyError:
        raise ValueError(f"Invalid atomic number {atomic_number}.")


def symbol_to_atomic_number(symbol: str) -> int:
    try:
        return _symbols_map[symbol.lower()]
    except KeyError:
        raise ValueError(f"Invalid symbol {symbol}.")


def atom_single_bond_covalent_radius(atomic_number: int) -> float:
    try:
        return _atomic_numbers_map[atomic_number][1]
    except KeyError:
        raise ValueError(f"Invalid atomic number {atomic_number}.")


@cache
def atom_single_bond_covalent_radius_list() -> list[float]:
    return [item[2] for item in _symbols[1:]]


@cache
def all_symbols() -> list[str]:
    return [symbol for _, symbol, _ in _symbols]


def build_bonds(
    atomic_num: list[int],
    x: list[float],
    y: list[float],
    z: list[float],
    geom_bond_tolerance: float,
    atom_single_bond_covalent_radius: list[float],
) -> list[tuple[int, int]]:
    """
    Optimized pure Python implementation using Spatial Sorting (Sweep and Prune).
    Complexity: O(N log N) sorting + O(N * k) search, where k is small.
    """
    # 1. Pre-filtering and data preparation
    # Collect a list of tuples for each valid atom.
    # This avoids accessing lists by index inside the hot loop.
    # Structure: (x, y, z, radius, original_index)
    atoms = []

    # Find the global maximum radius for computing limit
    # (iterate through radius table or atoms - atoms are more reliable if table is huge)
    max_radius = 0.0

    # Iterate once for preparation
    # zip works fast with both list and numpy array
    for i, (anum, xi, yi, zi) in enumerate(zip(atomic_num, x, y, z)):
        if anum < 1:
            continue

        r = atom_single_bond_covalent_radius[anum]
        if r > max_radius:
            max_radius = r

        atoms.append((xi, yi, zi, r, i))

    # 2. Sort by X coordinate
    # This is a key step for the Sweep-and-Prune algorithm
    atoms.sort(key=lambda t: t[0])

    # 3. Main bond search loop
    result = []
    tol_factor = 1.0 + geom_bond_tolerance
    n_atoms = len(atoms)

    for i in range(n_atoms):
        xi, yi, zi, ri, orig_i = atoms[i]

        # Search limit along X axis for the current atom.
        # If a neighbor along X is farther than this value, then any other neighbor
        # in the sorted list will be farther.
        limit = (ri + max_radius) * tol_factor

        # Inner loop: only look forward
        for j in range(i + 1, n_atoms):
            xj, yj, zj, rj, orig_j = atoms[j]

            # --- 1. X-axis culling (Sweep Check) ---
            dx = xj - xi

            # Most important line: break the inner loop
            if dx > limit:
                break

            # --- 2. Y and Z axis culling ---
            # In Python abs() is fast enough, but manual comparison may be faster
            # dy = abs(yj - yi)
            dy = yj - yi
            if dy > limit or dy < -limit:
                continue

            dz = zj - zi
            if dz > limit or dz < -limit:
                continue

            # --- 3. Exact check (Squared Distance) ---
            cutoff = (ri + rj) * tol_factor
            dist_sq = dx * dx + dy * dy + dz * dz

            if dist_sq < cutoff * cutoff:
                # Save the result.
                # Usually it's conventional to return (larger_index, smaller_index) or vice versa.
                # Sort the pair for consistency.
                if orig_i > orig_j:
                    result.append((orig_i, orig_j))
                else:
                    result.append((orig_j, orig_i))

    return result
