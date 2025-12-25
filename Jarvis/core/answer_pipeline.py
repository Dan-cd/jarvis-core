class AnswerPipeline:
    def __init__(self, llm_manager):
        self.llm = llm_manager


    def respond(self, user_input: str, context: dict) -> str:
        prompt = self._build_prompt(user_input, context)
        response = self.llm.generate(prompt)
        return response

    def explain(self, base_text: str) -> str:
        prompt = (
            "Você é o Jarvis.\n"
            "Fale sempre em primeira pessoa.\n"
            "Use 'senhor' para se referir ao usuário.\n"
            "Reescreva o texto abaixo de forma curta, clara e educada.\n\n"
            "Você é um assistente que faz parte do sistema.\n"
            "Fale SEMPRE em português brasileiro.\n"
            "Fale SEMPRE em primeira pessoa.\n"
            f"TEXTO BASE:\n{base_text}"
        )
        return self.llm.generate(prompt)   
       
    def _build_prompt(self, user_input: str, context: dict) -> str:
        return f"""
Você é Jarvis, um assistente em desenvolvimento.

Estado atual do sistema:
- Memória persistente: NÃO
- Voz: NÃO
- Hotword: NÃO

Pergunta do usuário:
{user_input}

Responda de forma direta e honesta.
"""