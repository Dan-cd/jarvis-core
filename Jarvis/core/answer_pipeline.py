from typing import Optional, List

from Jarvis.core.errors import (
    JarvisError,
    InvalidAnswerOrigin,
    WebRequiredButUnavailable,
)


class AnswerPipeline:
    """
    Responsável pela resposta FINAL do sistema.
    Aqui nasce a identidade institucional do Jarvis.
    """

    def __init__(self, context):
        self.context = context

    # =========================
    # Interface pública
    # =========================

    def build(
        self,
        response: str,
        origin: str,
        confidence: float,
        explainable: bool = False,
        sources: Optional[List[str]] = None,
    ) -> str:
        """
        Constrói a resposta final para o usuário.
        """

        self._validate_origin(origin)

        payload = {
            "text": response.strip(),
            "origin": origin,
            "confidence": confidence,
            "sources": sources or [],
            "explainable": explainable,
        }

        return self._render(payload)

    def build_from_result(self, result) -> str:
        """
        Compat layer: aceita um `ActionResult` (ou objeto similar)
        e converte para a representação final via `build`.
        """
        # Extrai conteúdo textual preferindo `content`, depois `data`, depois `message`
        content = None
        if hasattr(result, "content") and result.content:
            content = result.content
        elif hasattr(result, "data") and isinstance(result.data, str) and result.data:
            content = result.data
        elif getattr(result, "message", None):
            content = result.message

        origin = getattr(result, "origin", getattr(result, "source", "local"))
        confidence = getattr(result, "confidence", 0.0) or 0.0
        sources = None
        # Suporta vários formatos de `data`: dict ou objeto com atributo `sources`
        if hasattr(result, "data"):
            if isinstance(result.data, dict):
                sources = result.data.get("sources")
            elif hasattr(result.data, "sources"):
                sources = getattr(result.data, "sources")

        return self.build(
            response=content or "",
            origin=origin,
            confidence=confidence,
            explainable=False,
            sources=sources,
        )

    # =========================
    # Erros institucionais
    # =========================

    def system_error(self, message: str) -> str:
        return (
            "⚠️ Ocorreu um erro interno no sistema.\n"
            f"Detalhes: {message}"
        )

    def web_required_error(self, message: str) -> str:
        return (
            "🌐 Esta pergunta exige acesso à internet.\n"
            f"{message}"
        )

    # =========================
    # Validações internas
    # =========================

    def _validate_origin(self, origin: str) -> None:
        valid_origins = {"llm", "web", "plugin", "local"}

        if origin not in valid_origins:
            raise InvalidAnswerOrigin(
                message=f"Origem de resposta inválida: {origin}",
                origin="core",
                module="AnswerPipeline",
                function="_validate_origin",
            )

    # =========================
    # Renderização final
    # =========================

    def _render(self, payload: dict) -> str:
        """
        Renderiza a resposta final de forma institucional.
        """

        header = self._render_header(payload)
        body = payload["text"]
        footer = self._render_footer(payload)

        return "\n".join(
            part for part in (header, body, footer) if part
        )

    def _render_header(self, payload: dict) -> str:
        """
        Cabeçalho institucional (opcional).
        """

        if self.context.dev_mode:
            return (
                f"[Jarvis • origem={payload['origin']} • "
                f"confiança={payload['confidence']:.2f}]"
            )

        return "🤖 Jarvis"

    def _render_footer(self, payload: dict) -> Optional[str]:
        """
        Transparência e rastreabilidade.
        """

        lines = []

        if payload["origin"] == "web" and payload["sources"]:
            lines.append("🔎 Fontes:")
            for src in payload["sources"]:
                lines.append(f"- {src}")

        if payload["origin"] == "llm" and payload["explainable"]:
            lines.append(
                "ℹ️ Esta resposta foi gerada com base em conhecimento estático."
            )

        return "\n".join(lines) if lines else None
