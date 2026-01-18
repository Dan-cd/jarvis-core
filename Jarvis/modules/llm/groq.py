from groq import Groq

from Jarvis.modules.llm.base import (
    LLMInterface,
    LLMRequest,
    LLMResponse,
)
from Jarvis.core.errors import JarvisError


class GroqLLM(LLMInterface):
    """
    Implementação do provider Groq.
    Responsabilidade única: transformar LLMRequest em texto.
    """

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        api_key = self.config.get("api_key")

        if not api_key:
            raise JarvisError(
                message="Groq API key não configurada.",
                origin="llm",
                module="GroqLLM",
                function="__init__",
                sensitive=True,
            )

        self.client = Groq(api_key=api_key)
        self.model = self.config.get("model", "llama-3.3-70b-versatile")

    def generate(self, request: LLMRequest) -> LLMResponse:
        try:
            messages = []

            if request.system:
                messages.append({
                    "role": "system",
                    "content": request.system
                })

            messages.append({
                "role": "user",
                "content": request.prompt
            })

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=request.temperature,
            )

            text = completion.choices[0].message.content

            return LLMResponse(text=text)

        except Exception as e:
            raise JarvisError(
                message="Falha ao gerar resposta via Groq.",
                origin="llm",
                module="GroqLLM",
                function="generate",
                original_exception=e,
            )
