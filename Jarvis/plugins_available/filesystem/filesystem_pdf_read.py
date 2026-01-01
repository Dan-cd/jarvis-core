import PyPDF2

from Jarvis.plugins.base import Plugin
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult
from Jarvis.plugins_available.filesystem.utils.resolver import resolve_file_humanized
from Jarvis.core.intent import IntentType


class FilesystemPDFReadPlugin(Plugin):
    """
    Plugin responsável por leitura de PDFs.
    """

    INTENT = IntentType.FILE_READ_PDF

    metadata = {
        "name": "filesystem_pdf_read",
        "version": "3.0",
        "description": "Leitura segura de PDFs locais",
        "capabilities": ["filesystem.read.pdf"],
        "risk_level": "medium",
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
            reader = PyPDF2.PdfReader(str(path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            return ActionResult(False, f"Erro ao ler PDF: {e}")

        return ActionResult(
            True,
            f"Conteúdo do PDF '{filename}':\n\n{text}"
        )


PLUGIN_CLASS = FilesystemPDFReadPlugin