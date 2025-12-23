class AnswerPipeline:

    def __init__(self, llm_manager):
        self.llm = llm_manager

    def explain(self, raw_text: str) -> str:
        prompt = (
            "Explique a seguinte informação de forma clara, curta e amigável:\n\n"
            f"{raw_text}"
        )
        response = self.llm.generate(prompt)
        return response.text
    