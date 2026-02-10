import PyPDF2
from pathlib import Path

from Jarvis.plugins_available.filesystem.utils.pdf_summary import summarize_text
from Jarvis.plugins_available.filesystem.utils.pdf_ocr import extract_text_with_ocr
from Jarvis.plugins_available.filesystem.utils.resolver import resolve_file_humanized

from Jarvis.plugins.base import Plugin
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult
from Jarvis.core.intent import IntentType


class FilesystemPDFReadPlugin(Plugin):
    """
    Plugin responsável por leitura segura de PDFs locais,
    com fallback automático para OCR quando necessário.
    """

    intents = {IntentType.CONTENT_READ}

    metadata = {
        "name": "filesystem_pdf_read",
        "version": "3.3",
        "description": "Leitura segura de PDFs locais (com OCR fallback)",
        "capabilities": ["filesystem.read.pdf"],
        "risk_level": "medium",
        "dev_only": False
    }

    def execute(self, action: ActionRequest, dry_run: bool = False) -> ActionResult:
        filename = action.params.get("filename")

        if not filename:
            return ActionResult(False, "Arquivo não informado.")

        paths = resolve_file_humanized(filename)

        if not paths:
            return ActionResult(False, "Arquivo não encontrado.")

        if len(paths) > 1:
            return ActionResult(
                False,
                "Encontrei múltiplos PDFs com esse nome:\n"
                + "\n".join(f"- {p}" for p in paths)
                + "\nSeja mais específico."
            )

        path: Path = paths[0]

        if not path.exists() or not path.is_file():
            return ActionResult(False, "Arquivo inválido ou não encontrado.")

        
        # 1) Tentativa padrão (PyPDF2)
      
        text = ""
        try:
            reader = PyPDF2.PdfReader(str(path))
            text = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            ).strip()
        except Exception:
            text = ""

        
        # 2) Heurística de legibilidade
       
        needs_ocr = (
            not text
            or len(text) < 200
            or sum(c.isalnum() for c in text) / max(len(text), 1) < 0.4
        )

        # 3) OCR fallback
      
        if needs_ocr:
            try:
                text = extract_text_with_ocr(path)
            except Exception as e:
                return ActionResult(
                    False,
                    f"Falha ao aplicar OCR no PDF: {e}"
                )

        if not text or len(text) < 100:
            return ActionResult(
                False,
                "Este PDF não contém texto legível, mesmo após OCR."
            )

        # 4) Resumo
       
        summary = summarize_text(text, llm=action.context.llm if hasattr(action.context, "llm") else None)


        if not summary:
            return ActionResult(
                False,
                "Não consegui gerar um resumo legível deste PDF."
            )

        return ActionResult(
            True,
            f"Resumo do PDF '{path.name}':\n\n{summary}\n\n"
            "(Peça o texto completo se quiser ler tudo.)",
            data={
                "summary": summary,
                "full_text": text,
                "path": str(path),
                "type": "pdf"
            }
        )


PLUGIN_CLASS = FilesystemPDFReadPlugin