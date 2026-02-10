from pathlib import Path
from typing import List, Optional
import difflib

import datetime

def _human_file_info(path: Path) -> str:
    """Retorna uma linha descritiva curta sobre o arquivo (tamanho, modificação)."""
    try:
        size = path.stat().st_size
        mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime)
        return f"{path} — {size} bytes — mod: {mtime.isoformat(sep=' ', timespec='seconds')}"
    except Exception:
        return f"{path} — (informação indisponível)"


def select_targets_interactive(targets: List[Path]) -> Optional[List[Path]]:
    """
    Mostra uma lista numerada de targets para o usuário e permite:
     - 'all' para selecionar todos
     - 'n' para selecionar só um índice
     - '1,3,4' para selecionar múltiplos
     - Enter para cancelar
    Retorna lista de Path selecionados ou None se cancelado.
    """
    if not targets:
        return None

    print("\nArquivos encontrados:")
    for i, p in enumerate(targets, start=1):
        print(f"  {i}) {_human_file_info(p)}")

    choice = input("\nEscolha (all / números separados por vírgula / Enter = cancelar): ").strip().lower()

    if not choice:
        return None

    if choice == "all":
        return list(targets)

    # parse "1,2-4" basic support (only comma and single indices for simplicidade)
    chosen = []
    parts = [c.strip() for c in choice.split(",") if c.strip()]
    for part in parts:
        if "-" in part:
            # range a-b
            try:
                a, b = part.split("-", 1)
                a_i = int(a)
                b_i = int(b)
                for idx in range(a_i, b_i + 1):
                    if 1 <= idx <= len(targets):
                        chosen.append(targets[idx - 1])
            except Exception:
                continue
        else:
            try:
                idx = int(part)
                if 1 <= idx <= len(targets):
                    chosen.append(targets[idx - 1])
            except Exception:
                continue

    # dedupe and maintain order
    unique = []
    for p in chosen:
        if p not in unique:
            unique.append(p)

    return unique if unique else None


def preview_delete(plan_targets: List[Path]) -> None:
    """Mostra um resumo amigável do que será excluído."""
    print("\n--- PREVIEW: Exclusão ---")
    for p in plan_targets:
        print(f"  - {_human_file_info(p)}")
    print("------------------------\n")


def preview_move(source: Path, dest: Path) -> None:
    """Mostra um resumo amigável do que será movido e para onde."""
    print("\n--- PREVIEW: Movimentação ---")
    print(f"Origem: {_human_file_info(source)}")
    print(f"Destino (final): {dest}")
    print("-----------------------------\n")


def preview_write(target: Path, new_content: str) -> None:
    """
    Mostra um diff entre o conteúdo atual (se existir) e o novo conteúdo.
    Para arquivos grandes, mostra apenas um trecho resumido.
    """
    print("\n--- PREVIEW: Escrita ---")
    if target.exists():
        try:
            current = target.read_text(encoding="utf-8").splitlines(keepends=True)
        except Exception:
            current = ["<não foi possível ler o conteúdo atual>\n"]
    else:
        current = []

    new = new_content.splitlines(keepends=True)

    # usar difflib unified diff com limite
    diff = difflib.unified_diff(current, new, fromfile=str(target), tofile="novo", lineterm="")
    diff_lines = list(diff)

    if not diff_lines:
        print("Nenhuma diferença detectada (conteúdo idêntico).")
    else:
        # limitar a saída para 200 linhas para não poluir
        display = diff_lines[:200]
        print("".join(display))

        if len(diff_lines) > 200:
            print("\n... saída truncada (arquivo muito grande) ...")

    print("------------------------\n")


def confirm_prompt(message: str) -> bool:
    """Prompt simples sim/não com validação repetida curta."""
    while True:
        ans = input(f"{message} (sim/não): ").strip().lower()
        if ans in ("sim", "s", "yes", "y"):
            return True
        if ans in ("não", "nao", "n", "no"):
            return False
        print("Responda 'sim' ou 'não'.")