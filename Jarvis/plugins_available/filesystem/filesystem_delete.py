from Jarvis.plugins.base import Plugin
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult
from Jarvis.plugins_available.filesystem.utils.resolver import resolve_file_humanized
from Jarvis.core.intent import IntentType


class FilesystemDeletePlugin(Plugin):
    """
    Plugin responsável por exclusão de arquivos.
    """

    INTENT = IntentType.FILE_DELETE

    metadata = {
        "name": "filesystem_delete",
        "version": "3.1",
        "description": "Exclusão segura de arquivos locais",
        "capabilities": ["filesystem.delete"],
        "risk_level": "high",
        "dev_only": False
    }

    def execute(self, action: ActionRequest) -> ActionResult:
        filename = action.params.get("filename")

        if not filename:
            return ActionResult(
                success=False,
                message="Arquivo não informado."
                )

        path = resolve_file_humanized(filename)

        if not path or not path.exists():
            return ActionResult(
                success=False,
                message="Arquivo não encontrado."
                )

        try:
            path.unlink()
        except Exception as e:
            return ActionResult(
                success=False, 
                message=f"Erro ao excluir arquivo: {e}"
                )

        return ActionResult(
            success=True,
            message=f"Arquivo '{path.name}' excluído com sucesso."
        )


PLUGIN_CLASS = FilesystemDeletePlugin