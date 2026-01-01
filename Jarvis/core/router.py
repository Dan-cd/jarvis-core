from Jarvis.core.intent import IntentType, IntentEngine
from Jarvis.core.policy import PolicyEngine
from Jarvis.core.decision import Decision, DecisionOutcome, DecisionPath
from Jarvis.plugins.registry import PluginRegistry


class Router:
    def __init__(self, context):
        self.context = context
        self.intent_engine = IntentEngine()
        self.policy_engine = PolicyEngine(context)

    def route(self, user_input: str) -> Decision:

        #  Entrada vazia
        if not user_input.strip():
            return Decision.final(
                DecisionOutcome.DENY,
                "Entrada vazia."
            )

        #  Parse de intenção
        intent = self.intent_engine.parse(user_input)

        #  DEV MODE - prioridade absoluta
        if intent and intent.type == IntentType.DEV_ENTER:
            return Decision.final(
                DecisionOutcome.REQUIRE_DEV_MODE,
                "Autenticação necessária para ativar o Dev Mode."
            )

        if intent and intent.type == IntentType.DEV_EXIT:
            self.context.dev_mode = False
            return Decision.final(
                DecisionOutcome.ALLOW,
                "Dev Mode desativado."
            )
        # Memory - capacidade do core
        if intent and intent.type in (
            IntentType.MEMORY_WRITE,
            IntentType.MEMORY_READ
        ):
            return Decision.route(
                DecisionPath.LOCAL,
                payload={"intent": intent}
            )
        
        if intent.type in (IntentType.MEMORY_READ, IntentType.MEMORY_WRITE):
            return Decision(
                outcome=DecisionOutcome.ALLOW,
                path=DecisionPath.LOCAL,
                payload={"intent": intent}
            )
        
        # PLUGINS - não dependem de LLM
        if intent:
            plugin_cls = PluginRegistry.find_by_intent(intent.type)
            if plugin_cls:
                return Decision.route(
                    DecisionPath.PLUGIN,
                    payload={
                        "intent": intent,
                        "plugin": plugin_cls
                        }
                )

        #  OFFLINE - só bloqueia LLM
        if not self.context.llm_available:
            return Decision.route(
                DecisionPath.FALLBACK,
                payload={"offline": True}
            )

        #  Fallback final - LLM
        return Decision.route(DecisionPath.LLM)