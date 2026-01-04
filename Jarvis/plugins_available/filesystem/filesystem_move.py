import shutil
from pathlib import Path
from Jarvis.plugins.base import Plugin
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult
from Jarvis.core.action_plan import ActionPlan
from Jarvis.plugins_available.filesystem.utils.resolver import resolve_file_humanized
from Jarvis.core.intent import IntentType


class FilesystemMovePlugin(Plugin):
    """
    Movimentação segura de arquivos.
    Sempre passa por confirmação.
    """

    INTENT = IntentType.FILE_MOVE

    metadata = {
        "name": "filesystem_move",
        "version": "5.0",
        "description": "Movimentação segura e confirmável de arquivos",
        "capabilities": ["filesystem.move"],
        "risk_level": "medium",
        "requires_confirmation": True,
        "supports_dry_run": True,
    }

    def execute(self, action: ActionRequest, dry_run: bool = True):
        filename = action.params.get("filename")
        destination = action.params.get("target") or action.params.get("destination")

        if not filename or not destination:
            return ActionResult(False, "Arquivo ou destino não informado.")

        sources = resolve_file_humanized(filename, must_exist=True)
        dest_candidates = resolve_file_humanized(destination, must_exist=False)

        if not sources:
            return ActionResult(False, "Arquivo de origem não encontrado.")

        dest_base = dest_candidates[0]

        targets = [dest_base / src.name for src in sources]

        if dry_run:
            description = (
                "Mover os seguintes arquivos:\n"
                + "\n".join(f"- {src} → {dest}" for src, dest in zip(sources, targets))
            )
            return ActionPlan(
                action="filesystem.move",
                targets=sources,
                destructive=False,
                description=description,
            )

        # Execução real
        errors = []
        for src, dest in zip(sources, targets):
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dest))
            except Exception as e:
                errors.append(f"{src} → {dest}: {e}")

        if errors:
            return ActionResult(False, "Erros ao mover arquivos:\n" + "\n".join(errors))

        return ActionResult(True, f"{len(sources)} arquivo(s) movido(s) com sucesso.")


PLUGIN_CLASS = FilesystemMovePlugin