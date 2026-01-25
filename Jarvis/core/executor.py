# Jarvis/core/executor.py

from typing import Optional
from Jarvis.core.decision import DecisionOutcome, DecisionPath
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult
from Jarvis.core.errors import (
    WebRequiredButUnavailable,
    InvalidAnswerOrigin,
    InvalidActionResult
)


class Executor:
    """
    Executor do Jarvis: responsável por executar a decisão
    tomada pelo Router e produzir resposta final (string).
    """

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
        """
        Ponto de entrada para executar uma Decision e
        produzir uma resposta string pelo AnswerPipeline.
        """

        # ====================
        # LIMPEZA SEMPRE CHAMADA
        # ====================
        # Garantir que sempre exista memória a limpar
        # (execution_memory deve vir do context corretamente).
        if self.execution_memory:
            self.execution_memory.clear()

        # ====================
        # TRATAMENTO RÁPIDO DE DECISÕES FINAIS
        # Se a Decision não especifica `path` é uma decisão final
        # (ex.: mensagens de sistema, requer dev mode, desligar dev, etc.).
        # ====================
        if decision.path is None:
            # Erros/denials
            if decision.outcome == DecisionOutcome.DENY:
                return self.answer_pipeline.system_error(getattr(decision, "reason", "") or "")

            if decision.outcome == DecisionOutcome.DENY_WEB_REQUIRED:
                return self.answer_pipeline.web_required_error(getattr(decision, "reason", "") or "")

            # Caso geral: retornar a `reason` como resposta normal (origem local)
            return self.answer_pipeline.build(
                response=getattr(decision, "reason", "") or "",
                origin="local",
                confidence=1.0,
            )

        # ====================
        # EXECUÇÃO PELO CAMINHO
        # ====================
        if decision.path == DecisionPath.LLM:
            return self._execute_llm(decision, user_input)

        if decision.path == DecisionPath.PLUGIN:
            return self._execute_plugin(decision)

        if decision.path == DecisionPath.LOCAL:
            return self._execute_local(decision)

        # Não deveria chegar aqui
        raise InvalidAnswerOrigin(
            f"Caminho de execução inválido: {decision.path}"
        )

    # ============================
    # MÉTODOS AUXILIARES DE EXECUÇÃO
    # ============================

    def _execute_llm(self, decision, user_input: str) -> str:
        """
        Executa LLM local ou remoto e retorna via AnswerPipeline.
        """
        # Marcar origem
        if self.execution_memory:
            self.execution_memory.set("origin", "llm")

        # Gerar resposta
        response = self.llm.generate(
            prompt=user_input,
            mode=decision.payload.get("mode", "default")
        )

        # Construir ActionResult
        result = ActionResult(
            content=response,
            origin="llm",
            confidence=0.6  # default confianca para LLM
        )

        # Valida contrato
        self._validate_action_result(result, expected_origin="llm")

        # Converter em string final
        return self.answer_pipeline.build_from_result(result)

    def _execute_plugin(self, decision) -> str:
        """
        Executa plugin: pode ser web, scrape, busca, etc.
        """
        intent = decision.payload["intent"]
        plugins = decision.payload.get("plugins", [])

        if not plugins:
            raise WebRequiredButUnavailable(
                "Nenhum plugin disponível para execução."
            )

        # O PluginRegistry retorna lista de classes agora seguro
        plugin_ref = plugins[0]

        # Instancia se for classe
        if isinstance(plugin_ref, type):
            plugin = plugin_ref()
        else:
            plugin = plugin_ref

        # Monta ActionRequest
        params = getattr(intent, "payload", None) or {"query": intent.raw}
        action = ActionRequest(
            intent=intent,
            params=params,
            context=self.context,
        )

        # Executa plugin
        raw_result = plugin.execute(action)

        # Validar tipo
        if not isinstance(raw_result, ActionResult):
            raise InvalidActionResult(
                f"Plugin {plugin.name} retornou tipo inválido."
            )

        # Definir origem esperada
        expected_origin = "web" if decision.payload.get("temporal") else "plugin"

        # Contrato de origem/confiança
        self._validate_action_result(raw_result, expected_origin)

        # Converter resultado em string final
        return self.answer_pipeline.build_from_result(raw_result)

    def _execute_local(self, decision) -> str:
        """
        Executa rota LOCAL (memória, comandos fixos, utilidades).
        """
        if self.execution_memory:
            self.execution_memory.set("origin", "local")

        content = self.memory.execute(decision.payload)

        result = ActionResult(
            content=content,
            origin="local",
            confidence=0.9
        )

        self._validate_action_result(result, expected_origin="local")
        return self.answer_pipeline.build_from_result(result)

    # ============================
    # VALIDAÇÃO DE CONTRATO
    # ============================

    def _validate_action_result(
        self,
        result: ActionResult,
        expected_origin: str
    ):
        """
        Assegura que o ActionResult está de acordo com
        minimal contract (origem, content, confidence).
        """

        # Tipo
        if not isinstance(result, ActionResult):
            raise InvalidActionResult("Resultado não é ActionResult.")

        # Origem
        if result.origin != expected_origin:
            raise InvalidAnswerOrigin(
                f"Origem inválida: esperado={expected_origin}, recebido={result.origin}"
            )

        # Content precisa ser string
        if not isinstance(result.content, str):
            raise InvalidActionResult("content precisa ser string.")

        # Confidence tem que estar entre 0 e 1
        if not isinstance(result.confidence, (int, float)):
            raise InvalidActionResult("confidence inválida.")
        if not 0 <= result.confidence <= 1:
            raise InvalidActionResult("confidence fora do intervalo 0–1.")
