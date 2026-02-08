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
    - Executa Decisions vindas do Router.
    - Suporta execução de LLM, Plugins (incluindo RAG) e rotas locais.
    - Valida contratos de ActionResult antes de enviar ao AnswerPipeline.
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
        Executa uma Decision e retorna a resposta formatada pelo AnswerPipeline.
        """

        # Limpamos a memória de execução se ela existir (injeção pelo Context).
        if self.execution_memory:
            try:
                self.execution_memory.clear()
            except Exception:
                # Não deixamos falhas de limpeza interromperem o fluxo principal.
                pass

        # ----- decisões finais / curta-circuito -----
        if decision.path is None:
            # Decision final: usar reason/message como resposta ou erro institucional
            if decision.outcome == DecisionOutcome.DENY:
                return self.answer_pipeline.system_error(getattr(decision, "reason", "") or "")
            if decision.outcome == DecisionOutcome.OFFLINE:
                return self.answer_pipeline.system_error(getattr(decision, "reason", "") or "")
            if decision.outcome == DecisionOutcome.REQUIRE_DEV_MODE:
                return self.answer_pipeline.system_error(getattr(decision, "reason", "") or "")
            # fallback: devolver reason como resposta local
            return self.answer_pipeline.build(
                response=getattr(decision, "reason", "") or "",
                origin="local",
                confidence=1.0
            )

        # ----- roteamento por path -----
        if decision.path == DecisionPath.LLM:
            return self._execute_llm(decision, user_input)

        if decision.path == DecisionPath.PLUGIN:
            return self._execute_plugin(decision, user_input)

        if decision.path == DecisionPath.LOCAL:
            return self._execute_local(decision)

        # Se chegou aqui, caminho inválido
        raise InvalidAnswerOrigin(f"Caminho de execução inválido: {decision.path}")

    # -------------------------
    # Execução LLM (simples)
    # -------------------------
    def _execute_llm(self, decision, user_input: str) -> str:
        """
        Chamada direta ao LLM (chat/help/unknown).
        O LLMManager já injeta o system prompt; aqui passamos o prompt do usuário.
        """

        # Marca origem no ciclo
        if self.execution_memory:
            self.execution_memory.set("origin", "llm")

        # Gerar texto. O LLMManager aplicará o system prompt internamente.
        response_text = self.llm.generate(prompt=user_input, mode=decision.payload.get("mode", "default"))

        result = ActionResult(
            content=response_text,
            origin="llm",
            confidence=0.65
        )

        # Validar contrato (origem, content, confidence)
        self._validate_action_result(result, expected_origin="llm")

        return self.answer_pipeline.build_from_result(result)

    # -------------------------
    # Execução de Plugin (inclui RAG)
    # -------------------------
    def _execute_plugin(self, decision, user_input: str) -> str:
        """
        Executa plugin. Se payload.temporal == True, aplica RAG (Web -> LLM).
        Caso contrário, retorna resultado do plugin diretamente.
        """

        intent = decision.payload.get("intent")
        plugins = decision.payload.get("plugins", []) or []
        is_temporal = bool(decision.payload.get("temporal"))

        if not plugins:
            raise WebRequiredButUnavailable("Nenhum plugin disponível para a intenção.")

        # Instancia plugin se necessário
        plugin_ref = plugins[0]
        plugin = plugin_ref() if isinstance(plugin_ref, type) else plugin_ref

        # Prepara ActionRequest
        params = getattr(intent, "payload", None) or {"query": intent.raw}
        action = ActionRequest(intent=intent, params=params, context=self.context)

        # Executa plugin
        raw_result = plugin.execute(action)

        if not isinstance(raw_result, ActionResult):
            raise InvalidActionResult(f"Plugin {getattr(plugin, 'name', '?')} retornou tipo inválido.")

        # Se consulta temporal: sintetizar com LLM (RAG)
        if is_temporal:
            return self._synthesize_web_with_llm(user_query=user_input, web_result=raw_result)

        # Validate as response from plugin (web/plugin)
        expected_origin = "web" if getattr(raw_result, "origin", None) == "web" else "plugin"
        self._validate_action_result(raw_result, expected_origin=expected_origin)

        return self.answer_pipeline.build_from_result(raw_result)

    # -------------------------
    # Execução local (memória/util)
    # -------------------------
    def _execute_local(self, decision) -> str:
        if self.execution_memory:
            self.execution_memory.set("origin", "local")

        # Espera-se que memory.execute retorne string adequada
        content = self.memory.execute(decision.payload)

        result = ActionResult(content=content, origin="local", confidence=0.9)
        self._validate_action_result(result, expected_origin="local")
        return self.answer_pipeline.build_from_result(result)

    # -------------------------
    # RAG: sintetizar web result com LLM
    # -------------------------
    def _synthesize_web_with_llm(self, user_query: str, web_result: ActionResult) -> str:
        """
        Monta um prompt composto (user_query + web_result + fontes) e chama o LLM.
        A responsabilidade de garantir voz institucional está no LLMManager (system prompt).
        """

        # Assegura que web_result.content é string
        web_content = web_result.content if isinstance(web_result.content, str) else str(web_result.content)

        prompt_parts = [
            f"Pergunta: {user_query}",
            "",
            "Resultado da web (fontes abaixo):",
            web_content,
            ""
        ]

        sources_list = None
        data = getattr(web_result, "data", None)
        if isinstance(data, dict):
            sources_list = data.get("sources")
        elif hasattr(data, "sources"):
            sources_list = getattr(data, "sources")

        if sources_list:
            prompt_parts.append("Fontes:")
            for s in sources_list:
                prompt_parts.append(f"- {s}")
            prompt_parts.append("")

        prompt_parts.append("Com base nisso, resuma e responda de forma clara e prática:")

        rag_prompt = "\n".join(prompt_parts)

        # Marca origem (ciclo)
        if self.execution_memory:
            self.execution_memory.set("origin", "llm")

        # Chama LLM com mode "rag" (LLMManager irá aplicar system prompt)
        response_text = self.llm.generate(prompt=rag_prompt, mode="rag")

        # Monta ActionResult sintetizado
        result = ActionResult(content=response_text, origin="llm", confidence=getattr(web_result, "confidence", 0.6) or 0.6)

        # Anexa fontes para AnswerPipeline exibir
        result.data = {"sources": sources_list or []}

        # Valida e retorna
        self._validate_action_result(result, expected_origin="llm")
        return self.answer_pipeline.build_from_result(result)

    # -------------------------
    # Validação de contrato
    # -------------------------
    def _validate_action_result(self, result: ActionResult, expected_origin: str):
        if not isinstance(result, ActionResult):
            raise InvalidActionResult("Resultado não é ActionResult.")

        if getattr(result, "origin", None) != expected_origin:
            raise InvalidAnswerOrigin(f"Origem inválida: esperado={expected_origin}, recebido={getattr(result, 'origin', None)}")

        if not isinstance(result.content, str):
            raise InvalidActionResult("content precisa ser string.")

        if not isinstance(result.confidence, (int, float)):
            raise InvalidActionResult("confidence inválida.")

        if not 0 <= result.confidence <= 1:
            raise InvalidActionResult("confidence fora do intervalo 0–1.")
