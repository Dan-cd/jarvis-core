from Jarvis.plugins.base import Plugin
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult
from Jarvis.core.action_plan import ActionPlan
from Jarvis.plugins_available.filesystem.utils.resolver import resolve_file_humanized
from Jarvis.core.intent import IntentType


class FilesystemDeletePlugin(Plugin):
    """
    Plugin responsável por exclusão segura de arquivos.
    Nunca executa diretamente sem confirmação.
    """

    INTENT = IntentType.FILE_DELETE

    metadata = {
        "name": "filesystem_delete",
        "version": "4.0",
        "description": "Exclusão segura de arquivos locais",
        "capabilities": ["filesystem.delete"],
        "risk_level": "high",
        "dev_only": False,
        "supports_dry_run": True,
        "requires_confirmation": True,
    }

    def execute(self, action: ActionRequest, dry_run: bool = True):
        filename = action.params.get("filename")

        if not filename:
            return ActionResult(False, "Arquivo não informado.")

        paths = resolve_file_humanized(filename, must_exist=True)

        if not paths:
            return ActionResult(False, "Nenhum arquivo correspondente encontrado.")

        # DRY-RUN → gera plano
        if dry_run:
            return ActionPlan(
                action="filesystem.delete",
                targets=paths,
                destructive=True,
                description=self._describe(paths),
            )

        # EXECUÇÃO REAL (confirmada)
        deleted = []
        errors = []

        for path in paths:
            try:
                path.unlink()
                deleted.append(path)
            except Exception as e:
                errors.append(f"{path}: {e}")

        if errors:
            return ActionResult(
                success=False,
                message="Alguns arquivos não puderam ser excluídos:\n" + "\n".join(errors),
            )

        return ActionResult(
            success=True,
            message=f"{len(deleted)} arquivo(s) excluído(s) com sucesso.",
        )

    def _describe(self, paths):
        if len(paths) == 1:
            return f"Excluir o arquivo '{paths[0]}'."
        return (
            "Excluir os seguintes arquivos:\n"
            + "\n".join(f"- {p}" for p in paths)
        )


PLUGIN_CLASS = FilesystemDeletePlugin