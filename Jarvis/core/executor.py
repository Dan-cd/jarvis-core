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
    Executor principal do Jarvis.

    Ele implementa:
    - Execução de LLM
    - Execução de Plugins (incluindo Web + RAG)
    - Execução Local
    - Garantias de contrato de origem/confiança/content
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
        Executa uma Decision vinda do Router.
        """
        # Sempre limpa a memória de execução (só se existir)
        if self.execution_memory:
            self.execution_memory.clear()

        # DECISÕES FINAIS
        if decision.outcome == DecisionOutcome.DENY:
            return self.answer_pipeline.system_error(decision.reason)

        if decision.outcome == DecisionOutcome.OFFLINE:
            return self.answer_pipeline.system_error(decision.reason)

        # A rota pode ser LLM, PLUGIN ou LOCAL
        if decision.path == DecisionPath.LLM:
            return self._execute_llm(decision, user_input)

        if decision.path == DecisionPath.PLUGIN:
            return self._execute_plugin(decision, user_input)

        if decision.path == DecisionPath.LOCAL:
            return self._execute_local(decision)

        raise InvalidAnswerOrigin(f"Caminho de execução inválido: {decision.path}")

    # ======================
    # EXECUÇÕES POR CAMINHO
    # ======================

    def _execute_llm(self, decision, user_input: str) -> str:
        """
        Executa apenas o LLM com o prompt do usuário.
        """

        # Define origem na memória
        if self.execution_memory:
            self.execution_memory.set("origin", "llm")

        # Gera resposta
        response = self.llm.generate(
            prompt=user_input,
            mode=decision.payload.get("mode", "default")
        )

        # Constrói um ActionResult
        result = ActionResult(
            content=response,
            origin="llm",
            confidence=0.65
        )

        # Valida contrato
        self._validate_action_result(result, expected_origin="llm")

        # Retorna string via AnswerPipeline
        return self.answer_pipeline.build_from_result(result)

    def _execute_plugin(self, decision, user_input: str) -> str:
        """
        Executa um plugin. Se "temporal" estiver marcado,
        aplica RAG (Web + LLM).
        """

        intent = decision.payload.get("intent")
        plugins = decision.payload.get("plugins", [])
        is_temporal = bool(decision.payload.get("temporal"))

        if not plugins:
            raise WebRequiredButUnavailable(
                "Nenhum plugin disponível para a intenção."
            )

        # Pega o primeiro plugin da lista
        plugin_ref = plugins[0]

        # Pode vir como classe ou instância
        plugin = plugin_ref() if isinstance(plugin_ref, type) else plugin_ref

        # Monta ActionRequest
        params = getattr(intent, "payload", None) or {"query": intent.raw}
        action = ActionRequest(
            intent=intent,
            params=params,
            context=self.context
        )

        # Executa o plugin
        raw_result = plugin.execute(action)

        # Garante que seja ActionResult
        if not isinstance(raw_result, ActionResult):
            raise InvalidActionResult(
                f"Plugin {getattr(plugin, 'name', '?')} retornou tipo inválido."
            )

        # Se for consulta temporal e precisamos de RAG:
        if is_temporal:
            return self._synthesize_web_with_llm(user_input, raw_result)

        # Valida contrato de origem se não for temporal
        self._validate_action_result(raw_result, expected_origin="web")

        # Resposta direta (AnswerPipeline)
        return self.answer_pipeline.build_from_result(raw_result)

    def _execute_local(self, decision) -> str:
        """
        Execução local (memória / utilitários).
        """

        # Define origem
        if self.execution_memory:
            self.execution_memory.set("origin", "local")

        # Executa local
        content = self.memory.execute(decision.payload)

        result = ActionResult(
            content=content,
            origin="local",
            confidence=0.9
        )

        self._validate_action_result(result, expected_origin="local")

        return self.answer_pipeline.build_from_result(result)

    # ====================
    # RAG INTEGRADO (Web + LLM)
    # ====================

    def _synthesize_web_with_llm(self, user_query: str, web_result: ActionResult) -> str:
        """
        Sintetiza resposta combinando:
        - o texto da web (web_result.content)
        - as fontes (web_result.data.sources)
        - a pergunta original (user_query)

        Isso transforma um plugin web em um prompt fundamentado para o LLM,
        gerando uma resposta “Jarvis - style”.
        """

        # Monta prompt para RAG
        prompt = (
            "Você é Jarvis, um assistente inteligente com acesso a informações da web.\n"
            f"Pergunta: {user_query}\n"
            f"Resultado da Web:\n{web_result.content}\n\n"
            "Com base nisso, responda de forma clara e precisa:"
        )

        # Chama LLM com modo “rag”
        response = self.llm.generate(
            prompt=prompt,
            mode="rag"
        )

        # Cria ActionResult sintetizado
        result = ActionResult(
            content=response,
            origin="llm",
            confidence=web_result.confidence
        )

        # Valida contrato
        self._validate_action_result(result, expected_origin="llm")

        # Transfere fontes para o resultado
        result.data = {"sources": getattr(web_result.data, "sources", [])}

        # Retorna via AnswerPipeline
        return self.answer_pipeline.build_from_result(result)

    # ====================
    # VALIDAR CONTRATO
    # ====================

    def _validate_action_result(self, result: ActionResult, expected_origin: str):
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
            raise InvalidActionResult("confidence fora do intervalo 0-1.")
