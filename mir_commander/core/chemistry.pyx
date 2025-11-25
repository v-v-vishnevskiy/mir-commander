# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: initializedcheck=False

import numpy as np
cimport numpy as cnp
from libcpp.vector cimport vector
from cpython.exc cimport PyErr_SetString

# --- Constants ---
# Исправление: просто присваиваем значение.
# Cython сделает это доступным как float атрибут модуля.
BOHR2ANGSTROM = 0.529177210903  # 2018 CODATA

# --- Data Definitions ---

# Исходные данные
cdef list _raw_symbols = [
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

# --- Internal Storage Strategy ---
cdef int MIN_ATOMIC_NUM = -2
cdef int MAX_ATOMIC_NUM = 118
cdef int OFFSET = 2
cdef int ARRAY_SIZE = MAX_ATOMIC_NUM + OFFSET + 1

# Статический C-массив для радиусов (очень быстро)
cdef double[125] _radii_array

# Словарь для обратного поиска (str -> int)
cdef dict _symbol_to_number_map = {}

# Список символов по индексу (смещенному)
cdef list _symbol_by_index = [None] * ARRAY_SIZE

# Списки для кэшированных значений
cdef list _cached_radii_list_val = []
cdef list _cached_all_symbols_val = []


# --- Initialization Logic ---
def _initialize():
    global _cached_radii_list_val, _cached_all_symbols_val

    cdef int atomic_num
    cdef str symbol
    cdef double radius
    cdef int idx

    # Инициализация массива значениями по умолчанию (на всякий случай)
    for i in range(ARRAY_SIZE):
        _radii_array[i] = 0.0

    # 1. Заполняем структуры
    for atomic_num, symbol, radius in _raw_symbols:
        idx = atomic_num + OFFSET
        if 0 <= idx < ARRAY_SIZE:
            _radii_array[idx] = radius
            _symbol_by_index[idx] = symbol
            _symbol_to_number_map[symbol.lower()] = atomic_num

    # 2. Создаем готовые списки (аналог @cache)
    # Оригинал: [item[2] for item in _symbols[1:]] (пропускает первый элемент, который -1 'X')
    _cached_radii_list_val = [item[2] for item in _raw_symbols[1:]]
    _cached_all_symbols_val = [item[1] for item in _raw_symbols]

# Запускаем инициализацию при импорте
_initialize()


# --- Public API Functions ---

cpdef str atomic_number_to_symbol(int atomic_number):
    cdef int idx = atomic_number + OFFSET

    if idx < 0 or idx >= ARRAY_SIZE or _symbol_by_index[idx] is None:
        raise ValueError(f"Invalid atomic number {atomic_number}.")

    return _symbol_by_index[idx]


cpdef int symbol_to_atomic_number(str symbol):
    try:
        return _symbol_to_number_map[symbol.lower()]
    except KeyError:
        raise ValueError(f"Invalid symbol {symbol}.")


cpdef double atom_single_bond_covalent_radius(int atomic_number):
    cdef int idx = atomic_number + OFFSET

    # Проверка валидности.
    # Если символ None, значит атомный номер не был инициализирован.
    if idx < 0 or idx >= ARRAY_SIZE or _symbol_by_index[idx] is None:
        raise ValueError(f"Invalid atomic number {atomic_number}.")

    return _radii_array[idx]


cpdef list atom_single_bond_covalent_radius_list():
    return _cached_radii_list_val


cpdef list all_symbols():
    return _cached_all_symbols_val


cnp.import_array()

def build_bonds(
    object atomic_num,
    object x,
    object y,
    object z,
    double geom_bond_tolerance,
    object atom_single_bond_covalent_radius,
):
    # --- 1. Подготовка данных ---
    # Нам нужны Numpy массивы для сортировки
    cdef cnp.ndarray[cnp.int32_t, ndim=1] raw_atomic = np.asarray(atomic_num, dtype=np.int32)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] raw_x = np.asarray(x, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] raw_y = np.asarray(y, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] raw_z = np.asarray(z, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] raw_radii = np.asarray(atom_single_bond_covalent_radius, dtype=np.float64)

    cdef int n_atoms = raw_atomic.shape[0]

    # --- 2. Сортировка по координате X (Spatial Sorting) ---
    # Это ключевой момент. Сортировка позволяет прерывать внутренний цикл рано.
    # argsort возвращает индексы: order[0] - индекс самого левого атома
    cdef cnp.ndarray[cnp.int64_t, ndim=1] order = np.argsort(raw_x).astype(np.int64)

    # Создаем отсортированные временные массивы (C-contiguous)
    # Прямой доступ к памяти (sequential access) быстрее, чем прыжки по индексам
    cdef cnp.ndarray[cnp.int32_t, ndim=1, mode="c"] s_atomic = raw_atomic[order]
    cdef cnp.ndarray[cnp.float64_t, ndim=1, mode="c"] s_x = raw_x[order]
    cdef cnp.ndarray[cnp.float64_t, ndim=1, mode="c"] s_y = raw_y[order]
    cdef cnp.ndarray[cnp.float64_t, ndim=1, mode="c"] s_z = raw_z[order]

    # Для радиусов нам нужно отображение, так как atomic_num - это индексы в таблице радиусов,
    # но нам удобнее сразу иметь массив радиусов для каждого атома
    cdef cnp.ndarray[cnp.float64_t, ndim=1, mode="c"] atom_radii_per_atom = \
        np.take(raw_radii, s_atomic).astype(np.float64)

    # Указатели на отсортированные данные
    cdef int* atomic_ptr = <int*> s_atomic.data
    cdef double* x_ptr = <double*> s_x.data
    cdef double* y_ptr = <double*> s_y.data
    cdef double* z_ptr = <double*> s_z.data
    cdef double* r_ptr = <double*> atom_radii_per_atom.data

    # Указатель на массив индексов для восстановления оригинальных номеров
    cdef cnp.int64_t* order_ptr = <cnp.int64_t*> order.data

    # --- 3. Поиск глобального максимума радиуса ---
    cdef double global_max_radius = 0.0
    cdef int k
    # Ищем максимум в таблице радиусов (она маленькая)
    cdef double* raw_r_table_ptr = <double*> raw_radii.data
    for k in range(raw_radii.shape[0]):
        if raw_r_table_ptr[k] > global_max_radius:
            global_max_radius = raw_r_table_ptr[k]

    # Константы
    cdef double tol = 1.0 + geom_bond_tolerance
    cdef vector[int] bonds
    bonds.reserve(n_atoms * 6)

    # Переменные цикла
    cdef int i, j
    cdef double xi, yi, zi, ri
    cdef double limit_x, dx, dy, dz, dist_sq, max_dist_sq

    # Оригинальные индексы
    cdef int orig_i, orig_j

    # --- 4. Быстрый цикл (Sweep and Prune) ---
    with nogil:
        for i in range(n_atoms):
            if atomic_ptr[i] < 1: continue

            xi = x_ptr[i]
            yi = y_ptr[i]
            zi = z_ptr[i]
            ri = r_ptr[i]

            # Предел поиска по X:
            # (Радиус текущего + Максимально возможный радиус соседа) * допуск
            limit_x = (ri + global_max_radius) * tol

            # Ищем только "вперед" по списку.
            # Так как список отсортирован по X, x[j] >= x[i].
            for j in range(i + 1, n_atoms):

                # 1. ПРОВЕРКА ПО X (САМАЯ ВАЖНАЯ)
                dx = x_ptr[j] - xi

                # Если разница по X уже слишком велика, то все последующие атомы (j+1, j+2...)
                # ТЕМ БОЛЕЕ будут слишком далеко, так как они отсортированы.
                # МЫ ПРЕРЫВАЕМ ВНУТРЕННИЙ ЦИКЛ.
                if dx > limit_x:
                    break

                if atomic_ptr[j] < 1: continue

                # 2. Проверка Y (обычное отсечение)
                dy = y_ptr[j] - yi
                if dy > limit_x or dy < -limit_x: continue

                # 3. Проверка Z
                dz = z_ptr[j] - zi
                if dz > limit_x or dz < -limit_x: continue

                # 4. Точная дистанция
                dist_sq = dx*dx + dy*dy + dz*dz

                max_dist_sq = (ri + r_ptr[j]) * tol
                max_dist_sq = max_dist_sq * max_dist_sq

                if dist_sq < max_dist_sq:
                    # Нашли связь! Но i и j - это индексы в ОТСОРТИРОВАННОМ массиве.
                    # Нам нужно сохранить ОРИГИНАЛЬНЫЕ индексы.
                    orig_i = order_ptr[i]
                    orig_j = order_ptr[j]

                    # Сохраняем всегда пару, чтобы соблюсти порядок вызова
                    # В оригинале (i, j) где j < i, но мы перебираем j > i.
                    # Чтобы не путать пользователя, вернем как нашли, или отсортируем.
                    # Оригинальный код возвращает (max, min) так как j in range(i).
                    # Мы добавим просто пару, порядок в tuple не критичен для большинства,
                    # но если критичен:
                    if orig_i > orig_j:
                        bonds.push_back(orig_i)
                        bonds.push_back(orig_j)
                    else:
                        bonds.push_back(orig_j)
                        bonds.push_back(orig_i)

    # --- 5. Вывод ---
    cdef list result = []
    cdef int n_bonds = bonds.size() // 2
    for k in range(0, bonds.size(), 2):
        result.append((bonds[k], bonds[k+1]))

    return result
