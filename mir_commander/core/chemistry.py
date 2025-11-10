from functools import cache

BOHR2ANGSTROM = 0.529177210903  # 2018 CODATA


_symbols = [
    (-1, "X", 0.0),
    (-2, "Q", 0.0),
    (1, "H", 0.5),
    (2, "He", 0.32),
    (3, "Li", 0.46),
    (4, "Be", 1.33),
    (5, "B", 1.02),
    (6, "C", 0.85),
    (7, "N", 0.75),
    (8, "O", 0.71),
    (9, "F", 0.63),
    (10, "Ne", 0.64),
    (11, "Na", 0.67),
    (12, "Mg", 1.55),
    (13, "Al", 1.39),
    (14, "Si", 1.26),
    (15, "P", 1.16),
    (16, "S", 1.11),
    (17, "Cl", 1.03),
    (18, "Ar", 0.99),
    (19, "K", 0.96),
    (20, "Ca", 1.96),
    (21, "Sc", 1.71),
    (22, "Ti", 1.48),
    (23, "V", 1.36),
    (24, "Cr", 1.34),
    (25, "Mn", 1.22),
    (26, "Fe", 1.19),
    (27, "Co", 1.16),
    (28, "Ni", 1.11),
    (29, "Cu", 1.1),
    (30, "Zn", 1.12),
    (31, "Ga", 1.18),
    (32, "Ge", 1.24),
    (33, "As", 1.21),
    (34, "Se", 1.21),
    (35, "Br", 1.16),
    (36, "Kr", 1.14),
    (37, "Rb", 1.17),
    (38, "Sr", 2.1),
    (39, "Y", 1.85),
    (40, "Zr", 1.63),
    (41, "Nb", 1.54),
    (42, "Mo", 1.47),
    (43, "Tc", 1.38),
    (44, "Ru", 1.28),
    (45, "Rh", 1.25),
    (46, "Pd", 1.25),
    (47, "Ag", 1.2),
    (48, "Cd", 1.28),
    (49, "In", 1.36),
    (50, "Sn", 1.42),
    (51, "Sb", 1.4),
    (52, "Te", 1.4),
    (53, "I", 1.36),
    (54, "Xe", 1.33),
    (55, "Cs", 1.31),
    (56, "Ba", 2.32),
    (57, "La", 1.96),
    (58, "Ce", 1.8),
    (59, "Pr", 1.63),
    (60, "Nd", 1.76),
    (61, "Pm", 1.74),
    (62, "Sm", 1.73),
    (63, "Eu", 1.72),
    (64, "Gd", 1.68),
    (65, "Tb", 1.69),
    (66, "Dy", 1.68),
    (67, "Ho", 1.67),
    (68, "Er", 1.66),
    (69, "Tm", 1.65),
    (70, "Yb", 1.64),
    (71, "Lu", 1.7),
    (72, "Hf", 1.62),
    (73, "Ta", 1.52),
    (74, "W", 1.46),
    (75, "Re", 1.37),
    (76, "Os", 1.31),
    (77, "Ir", 1.29),
    (78, "Pt", 1.22),
    (79, "Au", 1.23),
    (80, "Hg", 1.24),
    (81, "Tl", 1.33),
    (82, "Pb", 1.44),
    (83, "Bi", 1.44),
    (84, "Po", 1.51),
    (85, "At", 1.45),
    (86, "Rn", 1.47),
    (87, "Fr", 1.42),
    (88, "Ra", 2.23),
    (89, "Ac", 2.01),
    (90, "Th", 1.86),
    (91, "Pa", 1.75),
    (92, "U", 1.69),
    (93, "Np", 1.7),
    (94, "Pu", 1.71),
    (95, "Am", 1.72),
    (96, "Cm", 1.66),
    (97, "Bk", 1.66),
    (98, "Cf", 1.68),
    (99, "Es", 1.68),
    (100, "Fm", 1.65),
    (101, "Md", 1.67),
    (102, "No", 1.73),
    (103, "Lr", 1.76),
    (104, "Rf", 1.61),
    (105, "Db", 1.57),
    (106, "Sg", 1.49),
    (107, "Bh", 1.43),
    (108, "Hs", 1.41),
    (109, "Mt", 1.34),
    (110, "Ds", 1.29),
    (111, "Rg", 1.28),
    (112, "Cn", 1.21),
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
def all_symbols() -> list[str]:
    return [symbol for _, symbol, _ in _symbols]
