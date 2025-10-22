from functools import cache

from periodictable import elements


@cache
def atomic_number_to_symbol(atomic_number: int) -> str:
    if atomic_number > 0:
        return elements[atomic_number].symbol
    elif atomic_number == -1:
        return "X"
    elif atomic_number == -2:
        return "Q"
    else:
        raise ValueError(f"Invalid atomic number {atomic_number}.")


@cache
def symbol_to_atomic_number(symbol: str) -> int:
    if symbol == "X":
        return -1
    elif symbol == "Q":
        return -2
    else:
        return elements.symbol(symbol).number


@cache
def all_symbols() -> list[str]:
    return ["X", "Q"] + [element.symbol for element in elements]
