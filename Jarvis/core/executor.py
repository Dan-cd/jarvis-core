from Jarvis.core.decision import DecisionOutcome, DecisionPath
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.policy import PolicyEngine, PolicyResult
from Jarvis.plugins.registry import PluginRegistry
from Jarvis.core.errors import (
    WebRequiredButUnavailable,
    InvalidAnswerOrigin
)


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

        # Decisões finais
        if decision.outcome == DecisionOutcome.DENY:
            return self.answer_pipeline.system_error(
                decision.message
            )

        if decision.outcome == DecisionOutcome.DENY_WEB_REQUIRED:
            return self.answer_pipeline.web_required_error(
                decision.message
            )

        # Execução por caminho
        if decision.path == DecisionPath.LLM:
            return self._execute_llm(decision, user_input)

        if decision.path == DecisionPath.PLUGIN:
            return self._execute_plugin(decision)

        if decision.path == DecisionPath.LOCAL:
            return self._execute_local(decision)

        raise InvalidAnswerOrigin(
            f"Caminho de execução inválido: {decision.path}"
        )

  
    # Execuções específicas
    #

    def _execute_llm(self, decision, user_input: str) -> str:
        self.execution_memory.set("origin", "llm")
        self.execution_memory.set("confidence", 0.65)

        return self.answer_pipeline.build(
            response=user_input,
            origin="llm",
            confidence=0.65,
            explainable=False
        )


    def _execute_plugin(self, decision) -> str:
        intent = decision.payload["intent"]
        plugins = decision.payload.get("plugins", [])

        if not plugins:
            raise WebRequiredButUnavailable(
                "Nenhum plugin disponível para execução."
            )

        plugin = plugins[0]
        result = plugin.execute(intent)

        origin = "web" if decision.payload.get("temporal") else "plugin"

        return self.answer_pipeline.build(
            response=result.content,
            origin=origin,
            confidence=result.confidence,
            explainable=True,
            sources=getattr(result, "sources", None)
        )

    def _execute_local(self, decision) -> str:
        self.execution_memory.set("origin", "local")
        result = self.memory.execute(decision.payload)

        return self.answer_pipeline.build(
            response=result,
            origin="local",
            confidence=0.9,
            explainable=True
        )
