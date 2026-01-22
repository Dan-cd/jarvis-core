from Jarvis.core.decision import DecisionOutcome, DecisionPath
from Jarvis.core.action_result import ActionResult
from Jarvis.core.errors import (
    WebRequiredButUnavailable,
    InvalidAnswerOrigin,
    InvalidActionResult
)
from Jarvis.core.action_request import ActionRequest


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

        # Decisões finais (curto-circuito)
        if decision.outcome == DecisionOutcome.DENY:
            return self.answer_pipeline.system_error(decision.message)

        if decision.outcome == DecisionOutcome.DENY_WEB_REQUIRED:
            return self.answer_pipeline.web_required_error(decision.message)

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

    # =========================
    # Execuções específicas
    # =========================

    def _execute_llm(self, decision, user_input: str) -> str:
        self.execution_memory.set("origin", "llm")

        response = self.llm.generate(
            prompt=user_input,
            mode=decision.payload.get("mode", "default")
        )

        result = ActionResult(
            content=response,
            origin="llm",
            confidence=0.6
        )

        self._validate_action_result(result, expected_origin="llm")

        return self.answer_pipeline.build_from_result(result)

    def _execute_plugin(self, decision) -> str:
        intent = decision.payload["intent"]
        plugins = decision.payload.get("plugins", [])

        if not plugins:
            raise WebRequiredButUnavailable(
                "Nenhum plugin disponível para execução."
            )

        # plugins pode conter classes (registradas) ou instâncias
        plugin_ref = plugins[0]
        if isinstance(plugin_ref, type):
            plugin = plugin_ref()
        else:
            plugin = plugin_ref

        # Constrói ActionRequest esperado pelos plugins
        params = getattr(intent, "payload", None) or {"query": intent.raw}
        action = ActionRequest(
            intent=intent,
            params=params,
            context=self.context,
        )

        raw_result = plugin.execute(action)

        if not isinstance(raw_result, ActionResult):
            raise InvalidActionResult(
                f"Plugin {plugin.name} retornou tipo inválido."
            )

        expected_origin = "web" if decision.payload.get("temporal") else "plugin"

        self._validate_action_result(
            raw_result,
            expected_origin=expected_origin
        )

        return self.answer_pipeline.build_from_result(raw_result)

    def _execute_local(self, decision) -> str:
        self.execution_memory.set("origin", "local")

        content = self.memory.execute(decision.payload)

        result = ActionResult(
            content=content,
            origin="local",
            confidence=0.9
        )

        self._validate_action_result(result, expected_origin="local")

        return self.answer_pipeline.build_from_result(result)

    # =========================
    # Validação de contrato
    # =========================

    def _validate_action_result(
        self,
        result: ActionResult,
        expected_origin: str
    ):
        if not isinstance(result, ActionResult):
            raise InvalidActionResult("Resultado não é ActionResult.")

        if result.origin != expected_origin:
            raise InvalidAnswerOrigin(
                f"Origem inválida: esperado={expected_origin}, recebido={result.origin}"
            )

        if not isinstance(result.content, str):
            raise InvalidActionResult("content precisa ser string.")

        if not isinstance(result.confidence, (int, float)):
            raise InvalidActionResult("confidence inválida.")

        if not 0 <= result.confidence <= 1:
            raise InvalidActionResult("confidence fora do intervalo 0–1.")
