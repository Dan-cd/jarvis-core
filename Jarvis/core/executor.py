from Jarvis.core.decision import DecisionOutcome, DecisionPath

class Executor:
    def __init__(self, llm, fallback, sandbox, memory, context, answer_pipeline):
        self.llm = llm
        self.fallback = fallback
        self.sandbox = sandbox
        self.memory = memory
        self.context = context
        self.answer_pipeline = answer_pipeline

    def execute(self, decision, user_input: str) -> str:
        if decision.outcome != DecisionOutcome.ALLOW:
            return decision.reason or "Operação interrompida."

        if decision.path == DecisionPath.LLM:
            return self.answer_pipeline.respond(user_input, context={})

        if decision.path == DecisionPath.FALLBACK:
            return self.fallback.respond(user_input)

        if decision.path == DecisionPath.SANDBOX:
            return self.sandbox.handle(decision, self.context)

        if decision.path == DecisionPath.LOCAL:
            if decision.payload and decision.payload.get("type") == "memory.query":
                return self.memory.describe()

        return "Caminho não reconhecido."