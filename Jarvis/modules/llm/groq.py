import os
from groq import Groq
from Jarvis.core.llm_contract import (
    LLMInterface,
    LLMRequest,
    LLMResponse,
)

class GroqLLM(LLMInterface):
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def generate(self, request: LLMRequest) -> LLMResponse:
        messages = [
            {"role": "system", "content": request.system_rules},
            {"role": "user", "content": request.prompt},
        ]

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=request.max_tokens,
        )

        text = completion.choices[0].message.content.strip()

        return LLMResponse(
            text=text,
            raw=completion.model_dump(),
        )