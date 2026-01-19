from Jarvis.core.errors import (
    LLMUnavailable,
    LLMExecutionError
)


class LLMManager:
    """
    Responsável apenas por orquestrar modelos de linguagem.
    NÃO decide origem, NÃO cria ActionResult, NÃO fala com AnswerPipeline.
    """

    def __init__(self, primary_llm=None, fallback_llm=None, context=None):
        self.primary_llm = primary_llm
        self.fallback_llm = fallback_llm
        self.context = context

    def available(self) -> bool:
        return self.primary_llm is not None or self.fallback_llm is not None

    def generate(self, prompt: str, mode: str = "default") -> str:
        """
        Tenta gerar resposta usando o modelo primário.
        Se falhar, tenta fallback.
        Retorna apenas TEXTO.
        """

        if self.primary_llm:
            try:
                return self._generate_with(self.primary_llm, prompt, mode)
            except Exception as e:
                if not self.fallback_llm:
                    raise LLMExecutionError(
                        f"Falha no LLM primário e fallback indisponível: {e}"
                    )

        if self.fallback_llm:
            try:
                return self._generate_with(self.fallback_llm, prompt, mode)
            except Exception as e:
                raise LLMExecutionError(
                    f"Falha no fallback LLM: {e}"
                )

        raise LLMUnavailable("Nenhum LLM disponível para execução.")

    def _generate_with(self, llm, prompt: str, mode: str) -> str:
        """
        Execução isolada de um LLM específico.
        """

        if not hasattr(llm, "generate"):
            raise LLMExecutionError("LLM não implementa método generate().")

        response = llm.generate(
            prompt=prompt,
            mode=mode
        )

        if not isinstance(response, str):
            raise LLMExecutionError(
                "LLM retornou resposta não textual."
            )

        return response
