# Jarvis/core/answer_pipeline.py

from typing import Optional, List
from Jarvis.core.errors import (
    InvalidAnswerOrigin,
)


class AnswerPipeline:
    """
    Responsável pela construção da resposta final exibida ao usuário.
    Garante: identidade institucional (Jarvis), formatação consistente,
    exibição de fontes quando existirem, e pequenas notas de explicabilidade.
    """

    def __init__(self, context):
        self.context = context

    def build(
        self,
        response: str,
        origin: str,
        confidence: float,
        explainable: bool = False,
        sources: Optional[List[str]] = None,
    ) -> str:
        # Valida origem esperada
        self._validate_origin(origin)

        cleaned = (response or "").strip()
        header = self._render_header(origin, confidence)
        body = cleaned
        footer = self._render_footer(origin, sources, explainable)

        return "\n\n".join(part for part in (header, body, footer) if part)

    def build_from_result(self, result) -> str:
        """
        Compat layer para ActionResult/objetos similares.
        Extrai content, origin, confidence e sources (se presentes).
        """
        content = getattr(result, "content", "") or ""
        origin = getattr(result, "origin", getattr(result, "source", "local"))
        confidence = getattr(result, "confidence", 0.0) or 0.0

        # Extrai sources de result.data, que pode ser dict ou objeto
        sources = None
        data = getattr(result, "data", None)
        if isinstance(data, dict):
            sources = data.get("sources")
        elif hasattr(data, "sources"):
            sources = getattr(data, "sources")

        # Por default, explicable=True quando vem de LLM (sintetizado)
        explainable = True if origin == "llm" else False

        return self.build(
            response=content,
            origin=origin,
            confidence=confidence,
            explainable=explainable,
            sources=sources
        )

    # -------------------------
    # Mensagens de erro institucional
    # -------------------------
    def system_error(self, message: str) -> str:
        return "⚠️ Ocorreu um erro interno no sistema.\n" f"Detalhes: {message}"

    def web_required_error(self, message: str) -> str:
        return "🌐 Esta pergunta exige acesso à internet.\n" f"{message}"

    # -------------------------
    # Validações internas
    # -------------------------
    def _validate_origin(self, origin: str) -> None:
        valid_origins = {"llm", "web", "plugin", "local"}
        if origin not in valid_origins:
            raise InvalidAnswerOrigin(
                message=f"Origem de resposta inválida: {origin}",
                origin="core",
                module="AnswerPipeline",
                function="_validate_origin",
            )

    # -------------------------
    # Renderização
    # -------------------------
    def _render_header(self, origin: str, confidence: float) -> str:
        """
        Cabeçalho institucional. No modo dev exibe origem e confiança.
        """
        if getattr(self.context, "dev_mode", False):
            return f"[Jarvis • origem={origin} • confiança={confidence:.2f}]"
        return "🤖 Jarvis"

    def _render_footer(self, origin: str, sources: Optional[List[str]], explainable: bool) -> Optional[str]:
        lines: List[str] = []

        # Exibe fontes se houver
        if sources:
            lines.append("🔎 Fontes:")
            for s in sources:
                lines.append(f"- {s}")

        # Nota de explicabilidade para respostas LLM (sintetizadas)
        if origin == "llm" and explainable:
            lines.append("ℹ️ Resposta gerada com base no contexto disponível.")

        return "\n".join(lines) if lines else None
