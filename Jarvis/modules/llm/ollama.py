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

    def generate(self, request, mode=None) -> LLMResponse:
        """
        Aceita diferentes formatos de `request`:
        - `str` (prompt direto)
        - `modules.llm.base.LLMRequest` (atributos: prompt, system, temperature)
        - `core.llm_contract.LLMRequest` (atributos: prompt, system_rules, verbosity)
        Também aceita ser chamada como `generate(final_prompt, mode=mode)`.
        """
        try:
            # Caso seja string (prompt completo)
            if isinstance(request, str):
                prompt = request
                system = None
                temperature = 0.7

            else:
                # Obter prompt
                prompt = getattr(request, "prompt", None) or getattr(request, "text", "")

                # Compatibilidade com 'system' (modules.llm.base) e 'system_rules' (core.llm_contract)
                system = getattr(request, "system", None) or getattr(request, "system_rules", None)

                # Temperatura quando disponível
                temperature = getattr(request, "temperature", None) or 0.7

                # Alguns requests expõem 'mode' ou 'verbosity' — podemos ignorar para Ollama
                if hasattr(request, "mode") and request.mode:
                    mode = request.mode

            if system:
                prompt = f"{system}\n\n{prompt}"

            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": temperature
                }
            )

            # Resposta pode ser dict ou string
            if isinstance(response, dict):
                text = response.get("response") or response.get("text") or str(response)
            else:
                text = str(response)

            return LLMResponse(text=text)

        except Exception as e:
            raise JarvisError(
                message="Falha ao gerar resposta via Ollama.",
                origin="llm",
                module="OllamaLLM",
                function="generate",
                original_exception=e,
            )
