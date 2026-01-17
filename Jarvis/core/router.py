from Jarvis.core.intent import IntentType, IntentEngine, Intent
from Jarvis.core.policy import PolicyEngine
from Jarvis.core.decision import Decision, DecisionOutcome, DecisionPath
from Jarvis.plugins.registry import PluginRegistry


# Intenções que NÃO podem ser respondidas sem Web
TIME_SENSITIVE_INTENTS = {
    IntentType.WEB_FETCH,
    IntentType.NEWS,
    IntentType.REAL_TIME_QUERY,
    IntentType.FINANCIAL_DATA,
}


# Padrões linguísticos que indicam tempo real
TIME_SENSITIVE_PATTERNS = (
    "agora",
    "hoje",
    "atualmente",
    "neste momento",
    "cotação",
    "preço",
    "última",
    "últimas notícias",
)


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

        # MEMORY LOCAL
        if intent.type in (
            IntentType.MEMORY_WRITE,
            IntentType.MEMORY_READ,
        ):
            return Decision.route(
                path=DecisionPath.LOCAL,
                payload={"intent": intent}
            )

        # verificação de sensibilidade temporal
        if self._is_time_sensitive(intent):
            return self._route_time_sensitive(intent)

        # Plugins explícitos não-web
        plugins = PluginRegistry.find_by_intent(intent.type)
        if plugins:
            return Decision.route(
                path=DecisionPath.PLUGIN,
                payload={
                    "intent": intent,
                    "plugins": plugins
                }
            )

        # CHAT / HELP → LLM (somente se seguro)
        if intent.type in (
            IntentType.CHAT,
            IntentType.HELP,
        ):
            if not self.context.llm_available:
                return Decision.final(
                    DecisionOutcome.DENY,
                    "Modelo de linguagem indisponível."
                )

            return Decision.route(
                path=DecisionPath.LLM,
                payload={
                    "intent": intent,
                    "mode": "static_knowledge"
                }
            )

        return Decision.final(
            DecisionOutcome.DENY,
            f"Nenhuma rota disponível para a intenção: {intent.type}"
        )


    # Métodos auxiliares
   

    def _is_time_sensitive(self, intent: Intent) -> bool:
        if intent.type in TIME_SENSITIVE_INTENTS:
            return True

        normalized = intent.raw.lower()
        return any(p in normalized for p in TIME_SENSITIVE_PATTERNS)

    def _route_time_sensitive(self, intent: Intent) -> Decision:
        web_plugins = PluginRegistry.find_by_intent(IntentType.WEB_FETCH)

        if not web_plugins:
            return Decision.final(
                DecisionOutcome.DENY_WEB_REQUIRED,
                "Consulta requer dados em tempo real, mas o WebPlugin não está disponível."
            )

        return Decision.route(
            path=DecisionPath.PLUGIN,
            payload={
                "intent": Intent(
                    type=IntentType.WEB_FETCH,
                    raw=intent.raw
                ),
                "plugins": web_plugins,
                "temporal": True
            }
        )
    def _translate_intent(self, intent: Intent):
        """
        Shim para compatibilidade: antigos lugares podem chamar _translate_intent.
        Chama a nova lógica de roteamento (conteúdo/plugin/etc).
        """
        # Reaproveita a lógica que mapeia intents de conteúdo para plugins
        if intent.type in (
            IntentType.CONTENT_CREATE,
            IntentType.CONTENT_READ,
            IntentType.CONTENT_MODIFY,
            IntentType.CONTENT_DELETE,
            IntentType.CONTENT_MOVE,
            IntentType.WEB_FETCH,
        ):
            plugins = PluginRegistry.find_by_intent(intent.type)
            if intent.type != IntentType.WEB_FETCH and plugins:
                return Decision.route(
                    path=DecisionPath.PLUGIN,
                    payload={"intent": intent, "plugins": plugins}
                )
        decision = self.route(intent.raw)
        return decision if decision.path == DecisionPath.PLUGIN else None
