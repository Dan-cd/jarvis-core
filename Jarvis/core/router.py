# Jarvis/core/router.py

from Jarvis.core.intent import IntentType, IntentEngine, Intent
from Jarvis.core.policy import PolicyEngine, PolicyResult
from Jarvis.core.decision import Decision, DecisionOutcome, DecisionPath
from Jarvis.plugins.registry import PluginRegistry


# Padrões linguísticos que indicam sensibilidade temporal/tempo real
TIME_SENSITIVE_PATTERNS = (
    "agora",
    "hoje",
    "neste momento",
    "cotação",
    "preço",
    "notícias",
)


class Router:
    """
    Router principal do Jarvis:
    - Classifica a intenção do usuário
    - Executa políticas prévias
    - Decide o caminho (LLM, plugin, local ou erro)
    """

    def __init__(self, context):
        self.context = context
        self.intent_engine = IntentEngine()
        self.policy_engine = PolicyEngine(context)

    def route(self, user_input: str) -> Decision:
        # Entrada vazia
        if not user_input.strip():
            return Decision.final(
                DecisionOutcome.DENY,
                "Entrada vazia."
            )

        # Analisa intenção
        intent = self.intent_engine.parse(user_input)
        if not intent:
            return Decision.final(
                DecisionOutcome.DENY,
                "Não foi possível identificar a intenção."
            )

        # Aplica política de intenção (antes de decidir rota)
        policy_decision = self.policy_engine.evaluate_intent(intent)
        if policy_decision.result == PolicyResult.DENY:
            # Se a política proíbe a intenção
            return Decision.final(
                DecisionOutcome.DENY,
                policy_decision.reason or "Intenção não permitida pela política."
            )
        if policy_decision.result == PolicyResult.REQUIRE_DEV_MODE:
            # Política exige modo dev
            return Decision.final(
                DecisionOutcome.REQUIRE_DEV_MODE,
                policy_decision.reason or "Requer modo desenvolvedor."
            )

        # Tratamento explícito de DEV MODE
        if intent.type == IntentType.DEV_ENTER:
            return Decision.final(
                DecisionOutcome.REQUIRE_DEV_MODE,
                "Autenticação Dev necessária."
            )
        if intent.type == IntentType.DEV_EXIT:
            self.context.dev_mode = False
            return Decision.final(
                DecisionOutcome.ALLOW,
                "Dev Mode desativado."
            )

        # MEMORY LOCAL
        if intent.type in (IntentType.MEMORY_WRITE, IntentType.MEMORY_READ):
            return Decision.route(
                DecisionPath.LOCAL,
                {"intent": intent}
            )

        # Verifica sensibilidade temporal heurística
        if self._is_time_sensitive(intent):
            temporal_decision = self._route_time_sensitive(intent)
            if temporal_decision:
                return temporal_decision

        # Plugins explícitos (não-web)
        plugins = PluginRegistry.find_by_intent(intent.type)
        if plugins:
            return Decision.route(
                DecisionPath.PLUGIN,
                {"intent": intent, "plugins": plugins}
            )

        # Chat ou Help → LLM (se permitido)
        if intent.type in (IntentType.CHAT, IntentType.HELP, IntentType.UNKNOWN):
            # Se LLM não disponível, negar
            if not self.context.llm_available:
                return Decision.final(
                    DecisionOutcome.OFFLINE,
                    "Modelo de linguagem indisponível."
                )
            # Forçar LLM para UNKNOWN também
            return Decision.route(
                DecisionPath.LLM,
                {"intent": intent}
            )

        # Nenhuma rota encontrada → negar com explicação
        return Decision.final(
            DecisionOutcome.DENY,
            f"Nenhuma rota encontrada para a intenção: {intent.type}"
        )

    def _is_time_sensitive(self, intent: Intent) -> bool:
        """
        Heurística textual que indica que a pergunta pode
        exigir dados em tempo real (web).
        """
        normalized = intent.raw.lower()
        return any(p in normalized for p in TIME_SENSITIVE_PATTERNS)

    def _route_time_sensitive(self, intent: Intent) -> Decision | None:
        """
        Rota explícita para consultas de tempo real (web).
        """
        web_plugins = PluginRegistry.find_by_intent(IntentType.WEB_FETCH)
        if not web_plugins:
            return Decision.final(
                DecisionOutcome.DENY,
                "Consulta em tempo real requer WebPlugin."
            )

        # Redefine a intenção para WEB_FETCH com mesmo raw
        return Decision.route(
            DecisionPath.PLUGIN,
            {
                "intent": Intent(
                    type=IntentType.WEB_FETCH,
                    raw=intent.raw
                ),
                "plugins": web_plugins,
                "temporal": True
            }
        )
