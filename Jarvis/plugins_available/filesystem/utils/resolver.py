from pathlib import Path
from typing import Iterable


SEARCH_BASES = [
    Path.home() / "Downloads",
    Path.home() / "Desktop",
    Path.home() / "Documents",
    Path.home() / "Pictures",
    Path.home() / "Videos",
    Path.home() / "Music",
    Path.home() / "Public",
    Path.home() / "Templates",
    Path.home() / ".jarvis" / "files",
    Path.home(),
]

MAX_DEPTH = 4


def resolve_file_humanized(filename: str, expect_file: bool = True) -> Path | None:
    if not filename:
        return None
    if not expect_file and filename.endswith("/"):
        filename = filename[:-1]

    filename = filename.strip().strip('"').strip("'")

    #  Caminho absoluto
    direct = Path(filename)
    if direct.is_absolute() and direct.exists():
        return direct

    #  Busca direta nos locais prioritários
    for base in SEARCH_BASES:
        candidate = base / filename
        if candidate.exists():
            return candidate

    #  Busca controlada por nome (sem rglob solto)
    for base in SEARCH_BASES:
        found = _search_by_name(base, filename, MAX_DEPTH)
        if found:
            return found

    return None


def _search_by_name(base: Path, filename: str, max_depth: int) -> Path | None:
    try:
        for path in _walk(base, max_depth):
            if path.name.lower() == filename.lower():
                return path
    except PermissionError:
        return None

    return None


def _walk(base: Path, max_depth: int) -> Iterable[Path]:
    stack = [(base, 0)]

    while stack:
        current, depth = stack.pop()

        if depth > max_depth:
            continue

        if current.is_file():
            yield current
            continue

        if current.is_dir():
            try:
                for child in current.iterdir():
                    stack.append((child, depth + 1))
            except PermissionError:
                continue