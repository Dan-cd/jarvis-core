import shutil
from pathlib import Path

from Jarvis.plugins.base import Plugin
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult
from Jarvis.plugins_available.filesystem.utils.resolver import resolve_file_humanized
from Jarvis.core.intent import IntentType
import shutil
from pathlib import Path

from Jarvis.plugins.base import Plugin
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult
from Jarvis.plugins_available.filesystem.utils.resolver import resolve_file_humanized
from Jarvis.core.intent import IntentType


class FilesystemMovePlugin(Plugin):
    """
    Plugin responsável por mover arquivos locais.
    Não interpreta linguagem natural.
    Recebe parâmetros já resolvidos.
    """

    INTENT = IntentType.FILE_MOVE

    metadata = {
        "name": "filesystem_move",
        "version": "3.0",
        "description": "Movimentação segura de arquivos locais",
        "capabilities": ["filesystem.move"],
        "risk_level": "medium",
        "dev_only": False
    }

    def execute(self, action: ActionRequest) -> ActionResult:
        filename = action.params.get("filename")
        source = action.params.get("source")
        target = action.params.get("target")

        if not filename or not target:
            return ActionResult(False, "Parâmetros insuficientes para mover o arquivo.")

        source_path = resolve_file_humanized(
            f"{source}/{filename}" if source else filename
        )

        if not source_path or not source_path.exists():
            return ActionResult(False, "Arquivo não encontrado.")

        target_dir = resolve_file_humanized(target, expect_file=False)

        if not target_dir or not target_dir.exists():
            return ActionResult(False, "Diretório de destino inválido.")

        target_path = target_dir / source_path.name

        if target_path.exists():
            return ActionResult(False, "Já existe um arquivo com esse nome no destino.")

        try:
            shutil.move(str(source_path), str(target_path))
        except Exception as e:
            return ActionResult(False, f"Erro ao mover arquivo: {e}")

        return ActionResult(True, f"Arquivo movido para {target_path}")


PLUGIN_CLASS = FilesystemMovePlugin

