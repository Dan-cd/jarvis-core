class AnswerPipeline:
    def __init__(self, llm_manager):
        self.llm = llm_manager

    def explain(self, base_text: str) -> str:
        prompt = (
            "Você é o Jarvis.\n"
            "Fale sempre em primeira pessoa.\n"
            "Sempre quando for falar algo, use 'senhor' para se referir ao usuário.\n"
            "Reescreva o texto abaixo de forma curta, clara e educada.\n\n"
            "Você é um assistente que faz parte do sistema.\n"
            "Fale SEMPRE em português brasileiro.\n"
            "Fale SEMPRE em primeira pessoa.\n"
            f"TEXTO BASE:\n{base_text}"
        )
        return self.llm.generate(prompt)      