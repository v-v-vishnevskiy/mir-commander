from pathlib import Path


def load_lines(path: Path, n: int) -> list[str]:
    lines = []
    with path.open("r") as input_file:
        for i, line in enumerate(input_file):
            lines.append(line)
            if i >= n:
                break
    return lines
