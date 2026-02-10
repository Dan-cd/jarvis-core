from Jarvis.plugins.base import Plugin
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult
from Jarvis.plugins_available.filesystem.utils.resolver import resolve_file_humanized
from Jarvis.core.intent import IntentType


class FilesystemEditPlugin(Plugin):
    """
    Plugin responsável por edição de arquivos locais.
    """

    intents = {IntentType.CONTENT_MODIFY}

    metadata = {
        "name": "filesystem_edit",
        "version": "3.1",
        "description": "Edição segura de arquivos locais",
        "capabilities": ["filesystem.edit"],
        "risk_level": "medium",
        "dev_only": False
    }

    def execute(self, action: ActionRequest, dry_run: bool = False) -> ActionResult:
        filename = action.params.get("filename")
        content_to_add = action.params.get("content")

        if not filename or not content_to_add:
            return ActionResult(False, "Arquivo ou conteúdo não informado.")

        paths = resolve_file_humanized(filename)

        if not paths:
            return ActionResult(False, "Arquivo não encontrado.")

        if len(paths) > 1:
            return ActionResult(
                False,
                "Encontrei múltiplos arquivos com esse nome:\n"
                + "\n".join(f"- {p}" for p in paths)
                + "\nSeja mais específico."
            )

        path = paths[0]

        if not path.exists() or not path.is_file():
            return ActionResult(False, "Arquivo inválido ou não encontrado.")

        if dry_run:
            return ActionResult(
                True,
                f"--- PREVIEW: Edição ---\n"
                f"Arquivo: {path}\n\n"
                f"+ {content_to_add}\n"
                f"-----------------------"
            )

        try:
            with path.open("a", encoding="utf-8") as f:
                f.write("\n" + content_to_add)
        except Exception as e:
            return ActionResult(False, f"Erro ao editar arquivo: {e}")

        return ActionResult(
            True,
            f"Arquivo '{path.name}' editado com sucesso."
        )


PLUGIN_CLASS = FilesystemEditPlugin