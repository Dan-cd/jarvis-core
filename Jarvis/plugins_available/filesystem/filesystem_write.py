from Jarvis.plugins.base import Plugin
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult
from Jarvis.core.action_plan import ActionPlan
from Jarvis.plugins_available.filesystem.utils.resolver import resolve_file_humanized
from Jarvis.core.intent import IntentType


class FilesystemWritePlugin(Plugin):
    """
    Escrita/criação segura de arquivos.
    Sempre pede confirmação.
    """

    intents = {IntentType.CONTENT_CREATE}

    metadata = {
        "name": "filesystem_write",
        "version": "5.0",
        "description": "Criação e escrita segura de arquivos",
        "capabilities": ["filesystem.write"],
        "risk_level": "medium",
        "requires_confirmation": True,
        "supports_dry_run": True,
    }

    def execute(self, action: ActionRequest, dry_run: bool = True):
        filename = action.params.get("filename")
        content = action.params.get("content", "")

        if not filename:
            return ActionResult(False, "Nome do arquivo não informado.")

        targets = resolve_file_humanized(filename, must_exist=False)

        target = targets[0]

        if dry_run:
            return ActionPlan(
                action="filesystem.write",
                targets=[target],
                destructive=False,
                description=f"Criar ou sobrescrever o arquivo '{target}'.",
            )

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        except Exception as e:
            return ActionResult(False, f"Erro ao escrever arquivo: {e}")

        return ActionResult(True, f"Arquivo '{target}' criado/escrito com sucesso.")


PLUGIN_CLASS = FilesystemWritePlugin