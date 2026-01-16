from Jarvis.core.decision import DecisionOutcome, DecisionPath
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.params_resolver import ParamsResolver
from Jarvis.core.intent import IntentType
from Jarvis.core.policy import PolicyEngine, PolicyResult
from Jarvis.plugins.registry import PluginRegistry
from Jarvis.plugins_available.web.models import WebResult


class Executor:
    def __init__(
        self,
        llm,
        fallback,
        sandbox,
        memory,
        execution_memory,
        temp_memory,
        context,
        answer_pipeline,
        dev_guard
    ):
        self.llm = llm
        self.fallback = fallback
        self.sandbox = sandbox
        self.memory = memory
        self.execution_memory = execution_memory
        self.temp_memory = temp_memory
        self.context = context
        self.answer_pipeline = answer_pipeline
        self.dev_guard = dev_guard

    def execute(self, decision, user_input: str) -> str:
        self.execution_memory.clear()
        self.execution_memory.set("last_source", "llm")

        # 🔹 DEV MODE GUARD
        if decision.outcome == DecisionOutcome.REQUIRE_DEV_MODE:
            if self.dev_guard.is_blocked():
                return "Dev Mode temporariamente bloqueado."

            attempt = input("Senha do Dev Mode: ")
            if self.dev_guard.validate(attempt):
                self.context.dev_mode = True
                return "Modo desenvolvedor ativado."

            return "Senha incorreta."

        if decision.outcome == DecisionOutcome.DENY:
            return decision.reason or "Operação negada."

        if decision.path is None:
            return decision.reason or "OK."

        # 🔹 LLM
        if decision.path == DecisionPath.LLM:
            if not self.context.llm_available:
                return "Modelo de linguagem indisponível no momento."

            try:
                self.execution_memory.set("last_source", "llm")
                return self.answer_pipeline.respond(user_input, self.context)
            except Exception as e:
                self.context.llm_available = False
                return "Modelo de linguagem indisponível."

        # 🔹 FALLBACK
        if decision.path == DecisionPath.FALLBACK:
            self.execution_memory.set("last_source", "fallback")
            return self.fallback.respond(user_input)

        # 🔹 LOCAL
        if decision.path == DecisionPath.LOCAL:
            return self._execute_local(decision)

        # 🔹 PLUGIN (NUNCA depende de internet)
        if decision.path == DecisionPath.PLUGIN:
            return self._execute_plugin(decision, user_input)

        return "Caminho não reconhecido."

    def _execute_plugin(self, decision, user_input: str) -> str:
        intent = decision.payload.get("intent")
        plugin_cls = PluginRegistry.find_by_intent(intent.type)
        if not plugin_cls:
            return "Nenhum plugin disponível para essa ação."
        plugin = plugin_cls()

        resolver = ParamsResolver()
        params = resolver.resolve(intent.type, intent.raw)

        action = ActionRequest(
            intent=intent,
            params=params,
            context=self.context
        )

        metadata = plugin.metadata or {}
        action.action = metadata.get("name")
        action.risk = metadata.get("risk_level", "low")

        policy = PolicyEngine(self.context)
        policy_decision = policy.evaluate_action(action, self.context.dev_mode)

        if policy_decision.result != PolicyResult.ALLOW:
            return policy_decision.reason or "Ação bloqueada."

        result = plugin.execute(action)

        if hasattr(result, "source"):
            self.execution_memory.set("last_source", result.source)
        else:
            self.execution_memory.set("last_source", "plugin")

        if isinstance(result.data, WebResult):
            self.execution_memory.set("last_source", "web")
            self.execution_memory.set("last_confidence", result.data.confidence)
            return self.answer_pipeline.respond_with_web(
                user_input=user_input,
                web_data=result.data,
                context=self.context
            )

        return result.message

    def _execute_local(self, decision) -> str:
        intent = decision.payload["intent"]

        if intent.type == IntentType.MEMORY_WRITE:
            self.execution_memory.set("last_source", "memory")
            return (
                "Memória registrada com sucesso."
                if self.memory.remember(intent.raw)
                else "Não encontrei nenhuma informação clara para salvar."
            )

        if intent.type == IntentType.MEMORY_READ:
            self.execution_memory.set("last_source", "memory")
            memories = self.memory.recall()
            if not memories:
                return "Não há memórias registradas."
            return "Memórias:\n" + "\n".join(
                f"- ({m.type.value}) {m.content}" for m in memories
            )

        return "Ação local não reconhecida."
