from Jarvis.core.intent import IntentType, IntentEngine, Intent
from Jarvis.core.policy import PolicyEngine
from Jarvis.core.decision import Decision, DecisionOutcome, DecisionPath
from Jarvis.plugins.registry import PluginRegistry


class Router:
    def __init__(self, context):
        self.context = context
        self.intent_engine = IntentEngine()
        self.policy_engine = PolicyEngine(context)

    def route(self, user_input: str) -> Decision:

        if not user_input.strip():
            return Decision.final(
                DecisionOutcome.DENY,
                "Entrada vazia."
            )

        intent = self.intent_engine.parse(user_input)
        if not intent:
            return Decision.final(
                DecisionOutcome.DENY,
                "Não foi possível identificar a intenção."
            )

        # DEV MODE
        if intent.type == IntentType.DEV_ENTER:
            return Decision.final(
                DecisionOutcome.REQUIRE_DEV_MODE,
                "Autenticação necessária para ativar o Dev Mode."
            )

        if intent.type == IntentType.DEV_EXIT:
            self.context.dev_mode = False
            return Decision.final(
                DecisionOutcome.ALLOW,
                "Dev Mode desativado."
            )

        # MEMORY — LOCAL
        if intent.type in (
            IntentType.MEMORY_WRITE,
            IntentType.MEMORY_READ
        ):
            return Decision.route(
                path=DecisionPath.LOCAL,
                payload={"intent": intent}
            )

        # Tradução semântica
        decision = self._translate_intent(intent)
        if decision:
            return decision

        # Plugins explícitos
        plugins = PluginRegistry.find_by_intent(intent.type)
        if plugins:
            return Decision.route(
                path=DecisionPath.PLUGIN,
                payload={
                    "intent": intent,
                    "plugins": plugins
                }
            )

        # CHAT / HELP explicativo → WEB
        if intent.type in (IntentType.CHAT, IntentType.HELP):
            normalized = intent.raw.lower().replace("?", "").strip()
            patterns = (
                "o que é",
                "oque é",
                "oq é",
                "quem é",
                "defina",
                "explique",
                "significa",
            )

            if any(p in normalized for p in patterns):
                return Decision.route(
                    path=DecisionPath.PLUGIN,
                    payload={
                        "intent": Intent(
                            type=IntentType.WEB_FETCH,
                            raw=intent.raw
                        )
                    }
                )

        # CHAT / HELP → LLM
        if intent.type in (
            IntentType.CHAT,
            IntentType.HELP,
        ):
            if not self.context.llm_available:
                return Decision.final(
                    DecisionOutcome.DENY,
                    "Modelo de linguagem indisponível."
                )

            return Decision.route(DecisionPath.LLM)

        return Decision.final(
            DecisionOutcome.DENY,
            f"Nenhuma rota disponível para a intenção: {intent.type}"
        )

    def _translate_intent(self, intent: Intent):
        if intent.type in (
            IntentType.CONTENT_CREATE,
            IntentType.CONTENT_READ,
            IntentType.CONTENT_MODIFY,
            IntentType.CONTENT_DELETE,
            IntentType.CONTENT_MOVE,
            IntentType.WEB_FETCH,
        ):
            return Decision.route(
                path=DecisionPath.PLUGIN,
                payload={"intent": intent}
            )

        return None
