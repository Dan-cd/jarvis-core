from Jarvis.core.intent import IntentType, IntentEngine, Intent
from Jarvis.core.policy import PolicyEngine
from Jarvis.core.decision import Decision, DecisionOutcome, DecisionPath
from Jarvis.plugins.registry import PluginRegistry

# Intenções que NÃO podem ser respondidas sem Web
TIME_SENSITIVE_INTENTS = {
    IntentType.WEB_FETCH,
}

TIME_SENSITIVE_PATTERNS = (
    "agora",
    "hoje",
    "neste momento",
    "cotação",
    "preço",
    "notícias",
)

class Router:
    def __init__(self, context):
        self.context = context
        self.intent_engine = IntentEngine()
        self.policy_engine = PolicyEngine(context)

    def route(self, user_input: str) -> Decision:
        if not user_input.strip():
            return Decision.final(DecisionOutcome.DENY, "Entrada vazia.")

        intent = self.intent_engine.parse(user_input)
        if not intent:
            return Decision.final(DecisionOutcome.DENY, "Intenção não identificada.")

        # Dev Mode
        if intent.type == IntentType.DEV_ENTER:
            return Decision.final(DecisionOutcome.REQUIRE_DEV_MODE, "Autenticação Dev necessária.")
        if intent.type == IntentType.DEV_EXIT:
            self.context.dev_mode = False
            return Decision.final(DecisionOutcome.ALLOW, "Dev Mode desativado.")

        # Memory
        if intent.type in (IntentType.MEMORY_WRITE, IntentType.MEMORY_READ):
            return Decision.route(DecisionPath.LOCAL, {"intent": intent})

        # Identifica tempo real
        if self._is_time_sensitive(intent):
            return self._route_time_sensitive(intent)

        # Plugins explícitos
        plugins = PluginRegistry.find_by_intent(intent.type)
        if plugins:
            return Decision.route(DecisionPath.PLUGIN, {"intent": intent, "plugins": plugins})

        # Chat/Help → LLM
        if intent.type in (IntentType.CHAT, IntentType.HELP):
            if not self.context.llm_available:
                return Decision.final(DecisionOutcome.DENY, "LLM indisponível.")
            return Decision.route(DecisionPath.LLM, {"intent": intent})

        return Decision.final(DecisionOutcome.DENY, f"Sem rota para: {intent.type}")

    def _is_time_sensitive(self, intent: Intent) -> bool:
        if intent.type in TIME_SENSITIVE_INTENTS:
            return True
        normalized = intent.raw.lower()
        return any(p in normalized for p in TIME_SENSITIVE_PATTERNS)

    def _route_time_sensitive(self, intent: Intent) -> Decision:
        web_plugins = PluginRegistry.find_by_intent(IntentType.WEB_FETCH)
        if not web_plugins:
            return Decision.final(DecisionOutcome.DENY_WEB_REQUIRED, "WebPlugin indisponível.")
        return Decision.route(DecisionPath.PLUGIN, {
            "intent": Intent(IntentType.WEB_FETCH, intent.raw),
            "plugins": web_plugins,
            "temporal": True
        })
