import ollama

from Jarvis.modules.llm.base import (
    LLMInterface,
    LLMRequest,
    LLMResponse,
)
from Jarvis.core.errors import JarvisError


class OllamaLLM(LLMInterface):
    """
    Provider Ollama (fallback / modo offline).
    """

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.model = self.config.get("model", "llama3")

    def generate(self, request: LLMRequest) -> LLMResponse:
        try:
            prompt = request.prompt

            if request.system:
                prompt = f"{request.system}\n\n{request.prompt}"

            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": request.temperature
                }
            )

            return LLMResponse(
                text=response["response"]
            )

        except Exception as e:
            raise JarvisError(
                message="Falha ao gerar resposta via Ollama.",
                origin="llm",
                module="OllamaLLM",
                function="generate",
                original_exception=e,
            )
