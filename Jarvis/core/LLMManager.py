from typing import Optional


class LLMResponse:
    def __init__(self, text: str, model: str):
        self.text = text
        self.model = model

class LLMManager:
    def __init__(self, primary_llm):
        self.primary = primary_llm

    def generate(self, prompt: str) -> str:
        try:
            return self.primary.generate(prompt, context=[])
        except Exception:
            return (
                "No momento estou sem acesso ao meu modelo de linguagem. "
                "Posso continuar executando comandos básicos."
            )
        
    def _remember(self, prompt: str, response: str):
        self.memory.remember("user", prompt)
        self.memory.remember("assistant", response)

    def reformulate(self, text: str):
        prompt = (
            "Trate o usuário como o seu senhor, mestre e amigo."
            "Antes de qualquer coisa, diga: Senhor"
            "Você é o Jarvis, um assistente pessoal. "
            "Fale sempre em primeira pessoa, de forma clara e direta.\n\n"
            f"Mensagem base:\n{text}"
        )
        return self.generate(prompt)