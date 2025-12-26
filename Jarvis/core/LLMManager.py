from Jarvis.core.llm_contract import (
    LLMInterface,
    LLMRequest,
    LLMResponse,
)
from Jarvis.modules.llm.groq import GroqLLM


class LLMManager(LLMInterface):
    def __init__(self):
        self.provider: LLMInterface = GroqLLM()

    def generate(self, request: LLMRequest) -> LLMResponse:
        return self.provider.generate(request)