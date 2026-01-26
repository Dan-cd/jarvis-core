# Jarvis/core/answer_pipeline.py

from typing import Optional, List
from Jarvis.core.errors import (
    InvalidAnswerOrigin,
)

class AnswerPipeline:
    """
    Responsável pela resposta FINAL do sistema.
    Aqui nasce a identidade institucional do Jarvis.
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
        """
        Constrói a resposta final para o usuário.
        """

        self._validate_origin(origin)

        # Normaliza o texto da resposta e cria cabeçalho
        cleaned = response.strip()
        header = self._render_header(origin, confidence)

        # Corpo principal
        body = cleaned

        # Rodapé (fontes, explicações)
        footer = self._render_footer(origin, sources, explainable)

        return "\n".join(filter(None, [header, body, footer]))

    def build_from_result(self, result) -> str:
        """
        Compatibilidade: aceita um ActionResult
        ou objeto similar e converte para a resposta final.
        """
        content = getattr(result, "content", "") or ""
        origin = getattr(result, "origin", "local")
        confidence = getattr(result, "confidence", 0.0) or 0.0
        sources = None

        # Suporta vários formatos de `data` com `sources`
        data = getattr(result, "data", None)
        if isinstance(data, dict):
            sources = data.get("sources")
        elif hasattr(data, "sources"):
            sources = getattr(data, "sources")

        return self.build(
            response=content,
            origin=origin,
            confidence=confidence,
            explainable=True,
            sources=sources,
        )

    # ===========================
    # Erros institucionais
    # ===========================

    def system_error(self, message: str) -> str:
        """
        Erro interno do sistema (negado pela arquitetura).
        """
        return "⚠️ Ocorreu um erro interno no sistema.\n" f"Detalhes: {message}"

    def web_required_error(self, message: str) -> str:
        """
        Chamado quando a rota exige web plugin, mas ele não está disponível.
        """
        return "🌐 Esta pergunta exige acesso à internet.\n" f"{message}"

    # ===========================
    # Validação de origem
    # ===========================

    def _validate_origin(self, origin: str) -> None:
        valid_origins = {"llm", "web", "plugin", "local"}
        if origin not in valid_origins:
            raise InvalidAnswerOrigin(
                message=f"Origem de resposta inválida: {origin}",
                origin="core",
                module="AnswerPipeline",
                function="_validate_origin",
            )

    # ===========================
    # Renderização final
    # ===========================

    def _render_header(self, origin: str, confidence: float) -> str:
        """
        Renderiza o cabeçalho institucional.
        """

        # No modo dev, exibe contexto de origem/confiança
        if self.context.dev_mode:
            return (
                f"[Jarvis • origem={origin} • confiança={confidence:.2f}]"
            )

        # Identidade institucional _sempre_ Jarvis
        return "🤖 Jarvis"

    def _render_footer(
        self,
        origin: str,
        sources: Optional[List[str]],
        explainable: bool
    ) -> Optional[str]:
        """
        Roda rodapé com fontes e explicações extras, quando aplicável.
        """

        lines: List[str] = []

        # Listagem de fontes quando a origem inclui contexto web
        if sources:
            lines.append("🔎 Fontes:")
            for s in sources:
                lines.append(f"- {s}")

        # Se origin == llm e explicável, adiciona nota de transparência
        if origin == "llm" and explainable:
            lines.append("ℹ️ Resposta gerada com base no contexto disponível.")

        return "\n".join(lines) if lines else None
