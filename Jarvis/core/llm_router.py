from Jarvis.core.memory import Memory
from Jarvis.core.IntentClassifier import IntentClassifier
from Jarvis.core.router_result import RouterResult
from Jarvis.core.router import Router

class LLMRouter:

    def __init__(self, llm, policy, limit: int = 20):
        self.memory = Memory()
        self.memory_limit = limit
        self.llm = llm
        self.policy = policy
        self.intent_classifier = IntentClassifier()

    def generate(self, prompt: str) -> str:
        context = self.memory.recall(limit=self.memory_limit)
        response = self.llm.ask(prompt=prompt, context=context)

        self.memory.remember("user", prompt)
        self.memory.remember("assistant", response)

        return response

    def route(self, text: str) -> RouterResult:
        intent = self.intent_classifier.classify(text)

        if intent.name == "command":
            return RouterResult("command", "Comando reconhecido.")

        if intent.name == "dev":
            return RouterResult("command", "Dev mode ativado.")

        if intent.name in ("question", "unknown"):
            if not self.policy.allows(intent):
                return RouterResult("blocked", "Não posso responder a isso.")

            response = self.generate(text)
            return RouterResult("llm", response)

        return RouterResult("blocked", "Entrada não compreendida.")