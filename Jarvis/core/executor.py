from Jarvis.core.decision import DecisionOutcome, DecisionPath
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.params_resolver import ParamsResolver
from Jarvis.core.intent import IntentType
from Jarvis.core.memory.models import MemoryType 
from Jarvis.core.memory.parser import MemoryParser, MemoryFact


class Executor:
    def __init__(
        self,
        llm,
        fallback,
        sandbox,
        memory,
        context,
        answer_pipeline,
        dev_guard
    ):
        self.llm = llm
        self.fallback = fallback
        self.sandbox = sandbox
        self.memory = memory
        self.context = context
        self.answer_pipeline = answer_pipeline
        self.dev_guard = dev_guard

    def execute(self, decision, user_input: str) -> str:

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

        # DECISÃO FINAL SEM PATH (ex: dev.exit)
        if decision.path is None:
            return decision.reason or "OK."

        if decision.path == DecisionPath.LLM:
            return self.answer_pipeline.respond(
                user_input=user_input,
                context=self.context
            )

        if decision.path == DecisionPath.FALLBACK:
            return self.fallback.respond(user_input)

        if decision.path == DecisionPath.LOCAL:
            return self._execute_local(decision)

        if decision.path == DecisionPath.PLUGIN:
            return self._execute_plugin(decision)

        return "Caminho não reconhecido."

    def _execute_plugin(self, decision) -> str:
        
        intent = decision.payload["intent"]

        resolver = ParamsResolver()
        params = resolver.resolve(intent.type, intent.raw)

        action = ActionRequest(
            intent=intent,
            params=params,
            context=self.context
        )

        plugin_cls = decision.payload["plugin"]
        plugin = plugin_cls()

        if plugin.metadata.get("dev_only") and not self.context.dev_mode:
            return "Ação disponível apenas em Dev Mode."


        result = plugin.execute(action)
        return result.message

    def _execute_local(self, decision) -> str:
        intent = decision.payload["intent"]

        # MEMORY WRITE
        if intent.type == IntentType.MEMORY_WRITE:
            success = self.memory.remember(intent.raw)

            if success:
                return "Memória registrada com sucesso."
            else:
                return "Não encontrei nenhuma informação clara para salvar na memória."

        # MEMORY READ
        if intent.type == IntentType.MEMORY_READ:
            memories = self.memory.recall()

            if not memories:
                return "Não há memórias registradas."

            lines = []
            for m in memories:
                lines.append(f"- ({m.type.value}) {m.content}")

            return "Memórias registradas:\n" + "\n".join(lines)

        return "Ação local não reconhecida."