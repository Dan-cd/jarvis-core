class OutputFormatter:
    def __init__(self, context):
        self.context = context

    def format(self, text: str) -> str:
        if not self.context.llm_available:
            return f"[Jarvis-OFFLINE] {text}"

        return f"[Jarvis] {text}"