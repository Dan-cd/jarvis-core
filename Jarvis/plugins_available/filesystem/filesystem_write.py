from pathlib import Path
from Jarvis.plugins.base import Plugin
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult
from Jarvis.plugins_available.filesystem.utils.resolver import resolve_file_humanized
from Jarvis.core.intent import IntentType


class FilesystemWritePlugin(Plugin):
    """
    Plugin responsável por criação/escrita de arquivos.
    """

    INTENT = IntentType.FILE_CREATE

    metadata = {
        "name": "filesystem_write",
        "version": "3.1",
        "description": "Criação segura de arquivos locais",
        "capabilities": ["filesystem.write"],
        "risk_level": "medium",
        "dev_only": False
    }

    def execute(self, action: ActionRequest) -> ActionResult:
        filename = action.params.get("filename")
        content = action.params.get("content", "")
        directory = action.params.get("path")

        if not filename:
            return ActionResult(False, "Nome do arquivo não informado.")

        # Resolve diretório humano (Downloads, Desktop, home, etc)
        if directory:
            base_dir = resolve_file_humanized(directory, expect_file=False)
            if not base_dir or not base_dir.exists():
                return ActionResult(False, "Diretório inválido.")
            full_path = base_dir / filename
        else:
            # fallback explícito e consciente
            full_path = Path.cwd() / filename

        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
        except Exception as e:
            return ActionResult(False, f"Erro ao criar arquivo: {e}")

        return ActionResult(
            True,
            f"Arquivo '{full_path}' criado com sucesso."
        )


PLUGIN_CLASS = FilesystemWritePlugin