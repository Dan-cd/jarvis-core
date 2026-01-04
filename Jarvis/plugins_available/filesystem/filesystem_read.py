from pathlib import Path
from Jarvis.plugins_available.filesystem.utils.text_summary import summarize_text
from Jarvis.plugins.base import Plugin
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
        "version": "3.1",
        "description": "Leitura segura de arquivos locais",
        "capabilities": ["filesystem.read"],
        "risk_level": "low",
        "dev_only": False
    }

    def execute(self, action: ActionRequest, dry_run: bool = False) -> ActionResult:
        filename = action.params.get("filename")

        if not filename:
            return ActionResult(False, "Arquivo não informado.")

        paths = resolve_file_humanized(filename)

        if not paths:
            return ActionResult(False, "Nenhum arquivo correspondente encontrado.")

        if len(paths) > 1:
            return ActionResult(
                False,
                "Encontrei múltiplos arquivos com esse nome:\n"
                + "\n".join(f"- {p}" for p in paths)
            )

        path = paths[0]

        if not path.exists() or not path.is_file():
            return ActionResult(False, "Arquivo inválido ou não encontrado.")

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            return ActionResult(False, f"Erro ao ler arquivo: {e}")

        summary = summarize_text(content)

        if not summary:
            return ActionResult(
                False,
                "Não consegui gerar um resumo legível deste arquivo."
            )

        return ActionResult(
            True,
            f"Resumo do arquivo '{path.name}':\n\n{summary}\n\n"
            "(Peça o texto completo se quiser ler tudo.)"
        )

PLUGIN_CLASS = FilesystemReadPlugin
