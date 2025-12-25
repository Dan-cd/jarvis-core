from Jarvis.core.intent import IntentEngine
from Jarvis.core.policy import PolicyEngine, PolicyResult
from Jarvis.core.decision import Decision, DecisionOutcome, DecisionPath


class Router:
    def __init__(self, context, sandbox, memory):
        self.context = context
        self.intent_engine = IntentEngine()
        self.policy_engine = PolicyEngine(context)
        self.sandbox = sandbox
        self.memory = memory

    def route(self, user_input: str) -> Decision:
        if not user_input.strip():
            return Decision.final(
                DecisionOutcome.DENY,
                "Entrada vazia."
            )

        # Estado offline total
        if not self.context.llm_available:
            return Decision.route(
                DecisionPath.FALLBACK,
                payload={"offline": True}
            )

        intent = self.intent_engine.parse(user_input)

        # Intenção não reconhecida → pergunta geral
        if not intent:
            return Decision.route(DecisionPath.LLM)

        decision = self.policy_engine.evaluate(intent)

        if decision.result == PolicyResult.REQUIRE_DEV_MODE:
            return Decision.final(
                DecisionOutcome.REQUIRE_DEV_MODE,
                decision.reason or "Modo desenvolvedor necessário."
            )

        if decision.result == PolicyResult.DENY:
            return Decision.final(
                DecisionOutcome.DENY,
                decision.reason or "Ação não permitida."
            )

        if intent.name.startswith("dev."):
            return Decision.route(
                DecisionPath.SANDBOX,
                payload=intent
                )
        
        if decision.result == PolicyResult.ALLOW:
            pass

        if intent.name == "memory.query":
            return Decision.route(
                DecisionPath.LOCAL,
                payload={"type": "memory.query"}
            )

        # Padrão: LLM
        return Decision.route(DecisionPath.LLM)