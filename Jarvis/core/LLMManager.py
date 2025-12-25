from typing import Optional


class LLMResponse:
    def __init__(self, text: str, model: str):
        self.text = text
        self.model = model


class LLMManager:
    def __init__(self, primary_llm=None, fallback_llm=None):
        if primary_llm is not None:
            self.primary = primary_llm
        else:
            self.primary = self._init_primary()

        if fallback_llm is not None:
            self.fallback = fallback_llm
        else:
            self.fallback = self._init_fallback()
    

    def _init_primary(self):
        from Jarvis.core.config import Config
        from groq import Groq
        return Groq(api_key=Config.GROQ_API_KEY)


    def _init_fallback(self):
        return None
    

    def generate(self, prompt: str, context: list | None = None) -> str:
        context = context or []
        try:
            if hasattr(self.primary, 'generate'):
                return self.primary.generate(prompt, context=context)
            else:
                raise AttributeError("primary LLM does not have 'generate' method")
        except Exception as e:
            return (
                "No momento estou sem acesso ao meu modelo de linguagem. "
                "Posso continuar executando comandos básicos."
            )
        
    def _remember(self, prompt: str, response: str):
        if hasattr(self, 'memory') and self.memory:
            self.memory.remember("user", prompt)
            self.memory.remember("assistant", response)