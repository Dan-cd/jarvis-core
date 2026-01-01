from pathlib import Path

from Jarvis.plugins.base import  Plugin
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult
from Jarvis.plugins_available.filesystem.utils.resolver import resolve_file_humanized
from Jarvis.core.intent import IntentType


class FilesystemReadPlugin(Plugin):
    """
    Plugin responsável por leitura de arquivos locais.
    """

    INTENT = IntentType.FILE_READ

    metadata = {
        "name": "filesystem_read",
        "version": "3.0",
        "description": "Leitura segura de arquivos locais",
        "capabilities": ["filesystem.read"],
        "risk_level": "low",
        "dev_only": False
    }

    def execute(self, action: ActionRequest) -> ActionResult:
        filename = action.params.get("filename")

        if not filename:
            return ActionResult(False, "Arquivo não informado.")

        path = resolve_file_humanized(filename)

        if not path or not path.exists():
            return ActionResult(False, "Arquivo não encontrado.")

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            return ActionResult(False, f"Erro ao ler arquivo: {e}")

        return ActionResult(
            True,
            f"Conteúdo do arquivo '{filename}':\n\n{content}"
        )


PLUGIN_CLASS = FilesystemReadPlugin
