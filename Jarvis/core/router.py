from Jarvis.core.intent import IntentEngine
from Jarvis.core.policy import PolicyEngine, PolicyResult
from Jarvis.core.decision import Decision, DecisionOutcome, DecisionPath
from Jarvis.core.dev_mode_guard import DevModeGuard


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

        if intent.name == "dev.enter":
            if self.context.dev_mode:
                return Decision.final(
                    DecisionOutcome.DENY,
                    "Modo desenvolvedor já está ativo."
                )

            return Decision.final(
                DecisionOutcome.REQUIRE_DEV_MODE,
                "Senha do modo desenvolvedor necessária."
            )

        if intent.name == "dev.exit":
            if not self.context.dev_mode:
                return Decision.final(
                    DecisionOutcome.DENY,
                    "Modo desenvolvedor não está ativo."
                )

            return Decision.final(
                DecisionOutcome.ALLOW,
                reason="Modo desenvolvedor desativado."
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