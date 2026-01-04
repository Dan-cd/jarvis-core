from pathlib import Path
from typing import Iterable, List


SEARCH_BASES = [
    Path.home() / "Downloads",
    Path.home() / "Desktop",
    Path.home() / "Documents",
    Path.home() / "Pictures",
    Path.home() / "Videos",
    Path.home() / "Music",
    Path.home() / "Public",
    Path.home() / "Templates",
    Path.home(),
]

MAX_DEPTH = 4


def resolve_file_humanized(
    name: str,
    *,
    must_exist: bool = True
) -> List[Path]:
    results: List[Path] = []

    if not name:
        return results

    name = name.strip().strip('"').strip("'")

    direct = Path(name)

    # Caminho absoluto
    if direct.is_absolute():
        if direct.exists():
            return [direct]
        return [] if must_exist else [direct]

    # Busca direta nos locais conhecidos
    for base in SEARCH_BASES:
        candidate = base / name
        if candidate.exists():
            results.append(candidate)

    if results:
        return results

    # Busca controlada (fuzzy simples)
    for base in SEARCH_BASES:
        found = _search_by_name(base, name, MAX_DEPTH)
        if found and found not in results:
            results.append(found)

    if results:
        return results

    # Se não precisa existir, sugerimos local padrão
    if not must_exist:
        return [Path.cwd() / name]

    return []


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