from Jarvis.plugins.base import Plugin
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult
from Jarvis.plugins_available.filesystem.utils.resolver import resolve_file_humanized
from Jarvis.core.intent import IntentType


class FilesystemEditPlugin(Plugin):
    """
    Plugin responsável por edição (append) de arquivos.
    """

    INTENT = IntentType.FILE_EDIT

    metadata = {
        "name": "filesystem_edit",
        "version": "3.0",
        "description": "Edição segura de arquivos locais",
        "capabilities": ["filesystem.edit"],
        "risk_level": "medium",
        "dev_only": False
    }

    def execute(self, action: ActionRequest) -> ActionResult:
        filename = action.params.get("filename")
        content = action.params.get("content")

        if not filename or not content:
            return ActionResult(False, "Parâmetros insuficientes para edição.")

        path = resolve_file_humanized(filename)

        if not path or not path.exists():
            return ActionResult(False, "Arquivo não encontrado.")

        try:
            with path.open("a", encoding="utf-8") as f:
                f.write("\n" + content)
        except Exception as e:
            return ActionResult(False, f"Erro ao editar arquivo: {e}")

        return ActionResult(
            True,
            f"Arquivo '{filename}' editado com sucesso."
        )


PLUGIN_CLASS = FilesystemEditPlugin