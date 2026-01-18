from typing import Optional

from Jarvis.core.decision import DecisionOutcome, DecisionPath
from Jarvis.core.errors import (
    WebRequiredButUnavailable,
    InvalidAnswerOrigin,
)
from Jarvis.plugins.registry import PluginRegistry


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
        dev_guard,
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
        # Limpa estado precedente de execução
        self.execution_memory.clear()

        # 1) Negado institucionalmente
        if decision.outcome == DecisionOutcome.DENY:
            return self.answer_pipeline.system_error(decision.message)

        # 2) Requer Web, mas não tem WebPlugin
        if decision.outcome == DecisionOutcome.DENY_WEB_REQUIRED:
            return self.answer_pipeline.web_required_error(decision.message)

        # 3) Caminho de execução
        if decision.path == DecisionPath.LLM:
            return self._execute_llm(decision, user_input)

        if decision.path == DecisionPath.PLUGIN:
            return self._execute_plugin(decision)

        if decision.path == DecisionPath.LOCAL:
            return self._execute_local(decision)

        # Qualquer outra rota é inválida aqui
        raise InvalidAnswerOrigin(f"Caminho inválido: {decision.path}")

    
    # Execuções específicas
    

    def _execute_llm(self, decision, user_input: str) -> str:
        """
        LLM só deve ser invocado quando a intenção for
        sabe/conhecimento estático (não-temporal).
        """
        # Marca origem
        self.execution_memory.set("origin", "llm")
        # Confiança padrão estimada
        self.execution_memory.set("confidence", 0.65)

        return self.answer_pipeline.build(
            response=user_input,
            origin="llm",
            confidence=0.65,
            explainable=False,
        )

    def _execute_plugin(self, decision) -> str:
        """
        Plugins podem incluir WebPlugin. Se for temporal,
        web será chamado.
        """
        intent = decision.payload.get("intent")
        plugins = decision.payload.get("plugins", [])

        if not plugins:
            # Nenhum plugin correspondente → contrato quebrado
            raise WebRequiredButUnavailable(
                "Plugin requerido não encontrado para essa intenção"
            )

        # Pegamos o primeiro plugin disponível
        plugin = plugins[0]
        result = plugin.execute(intent)

        # Decide origem
        # Se plugin representa web e temporalidade foi pedida
        origin = "web" if decision.payload.get("temporal") else "plugin"
        confidence: Optional[float] = getattr(result, "confidence", None)

        return self.answer_pipeline.build(
            response=result.content if hasattr(result, "content") else result.message,
            origin=origin,
            confidence=confidence,
            explainable=True,
            sources=getattr(result, "sources", None),
        )

    def _execute_local(self, decision) -> str:
        """
        Tratamento local (ex.: memória).
        """
        self.execution_memory.set("origin", "local")
        result = self.memory.execute(decision.payload)

        return self.answer_pipeline.build(
            response=result,
            origin="local",
            confidence=0.9,
            explainable=True,
        )
