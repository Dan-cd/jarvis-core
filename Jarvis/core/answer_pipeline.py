# Jarvis/core/answer_pipeline.py
from typing import Optional, Any, Dict

from Jarvis.core.llm_contract import LLMRequest, LLMVerbosity
from Jarvis.core.context import ExecutionContext
from Jarvis.plugins_available.web.models import WebResult


class AnswerPipeline:
    """
    Pipeline responsável por:
    - Unificar e validar metadados de origem/confiança;
    - Construir system prompt / system rules que correspondam
      ao contrato de identidade do Jarvis;
    - Enviar pedidos ao LLM (formatação final) quando apropriado;
    - Fornecer métodos utilitários compatíveis com o Executor.
    """

    def __init__(self, llm, execution_memory):
        self.llm = llm
        self.execution_memory = execution_memory

    # -------------------------
    # Compatibilidade / helpers
    # -------------------------
    def _get_origin(self) -> str:
        # Tentamos as chaves recentes; fallback para chaves antigas (compatibilidade)
        return self.execution_memory.get("origin", self.execution_memory.get("last_source", "local"))

    def _get_confidence(self) -> Optional[float]:
        return self.execution_memory.get("confidence", self.execution_memory.get("last_confidence", None))

    # -------------------------
    # API pública usada pelo Executor
    # -------------------------
    def build(self, response: str, origin: str, confidence: Optional[float], explainable: bool, sources: Optional[Any] = None) -> str:
        """
        Constrói a resposta final (formata com o LLM) usando metadados.
        - response: texto bruto (p.ex. result.content de um plugin ou texto do LLM)
        - origin: 'web' | 'plugin' | 'llm' | 'local'
        - confidence: float [0..1] ou None
        - explainable: se True, incluirá instruções para anexar fontes/explicação
        - sources: opcional, estrutura com fontes (lista/dict) vinda do plugin web
        """
        # Atualiza execução para futuras consultas (consistência)
        self.execution_memory.set("last_source", origin)
        self.execution_memory.set("origin", origin)
        if confidence is not None:
            self.execution_memory.set("last_confidence", confidence)
            self.execution_memory.set("confidence", confidence)

        # Construção das system rules / identidade Jarvis
        system_rules = [
            "Você é o Jarvis, um sistema executor com contrato institucional.",
            "Você usa metadados de origem para justificar respostas.",
            "Nunca afirme ter acesso direto à internet; sempre referencie a origem real (web/plugin/memory/llm).",
            "Quando a origem for 'web', forneça fontes se disponíveis.",
            "Quando a origem for 'llm' (raciocínio interno), deixe claro que é estimativa e informe a confiança se existir."
        ]

        if origin == "web":
            system_rules.append("Esta resposta foi construída a partir de dados buscados na web via WebPlugin.")
        elif origin == "local":
            system_rules.append("Esta resposta foi obtida da memória local / cache do Jarvis.")
        elif origin == "plugin":
            system_rules.append("Esta resposta foi produzida por um plugin local.")
        elif origin == "llm":
            system_rules.append("Esta resposta é resultado de raciocínio interno (modelo).")

        # Se pediram explicação, instruímos o modelo a anexar fontes e confiança
        explanation_block = ""
        if explainable:
            explanation_block = "\n\nInclua uma breve seção 'Origem e Confiança' listando a origem e a(s) fonte(s) quando disponíveis."

        # Contexto adicional para o LLM (se houver web_result/sources)
        context_data: Dict[str, Any] = {}
        if sources is not None:
            context_data["sources"] = sources
        # Monta prompt final a ser enviado ao LLM (formatado)
        prompt = (
            "\n".join(system_rules)
            + "\n\n---\n"
            + "Conteúdo a ser entregue ao usuário (já formatado):\n"
            + response.strip()
            + explanation_block
        )

        request = LLMRequest(
            prompt=prompt,
            system_rules="\n".join(system_rules),
            verbosity=LLMVerbosity.SHORT,
            max_tokens=800 if origin == "web" else 400,
            context_data=context_data
        )

        llm_response = self.llm.generate(request)
        return llm_response.text.strip()

    def system_error(self, message: str) -> str:
        """
        Resposta padronizada quando o Executor decide negar (erro institucional).
        Mantemos um formato simples (não chamar o LLM para mensagens de erro simples).
        """
        # Atualiza execução para rastreabilidade
        self.execution_memory.set("last_source", "system")
        self.execution_memory.set("origin", "system")
        return f"Erro do Jarvis: {message}"

    def web_required_error(self, message: str) -> str:
        """
        Mensagem específica quando uma consulta sensível no tempo precisava de Web.
        """
        self.execution_memory.set("last_source", "system")
        self.execution_memory.set("origin", "system")
        return (
            f"A consulta requer dados em tempo real e o WebPlugin não está disponível.\n"
            f"Motivo: {message}\n"
            "Tente novamente quando o WebPlugin estiver ativo ou solicite uma resposta offline (confiança reduzida)."
        )

    # -------------------------
    # Métodos legacy (compatibilidade)
    # -------------------------
    def respond(self, user_input: str, context: ExecutionContext) -> str:
        """
        Método legacy — mantém compatibilidade com chamadas antigas.
        Interpreta o execution_memory para decidir o comportamento.
        """
        origin = self._get_origin()
        confidence = self._get_confidence()
        # Se a origem for web e houver web payload em memory, incluímos no context_data
        web_ctx = context and getattr(context, "last_web_result", None)
        return self.build(
            response=user_input,
            origin=origin,
            confidence=confidence,
            explainable=(origin in ("web", "plugin", "local")),
            sources=getattr(web_ctx, "__dict__", None)
        )

    def respond_with_web(self, user_input: str, web_data: WebResult, context: ExecutionContext) -> str:
        """
        Outro método legacy — recebe explicitamente o resultado web e formata.
        """
        return self.build(
            response=web_data.content if hasattr(web_data, "content") else str(web_data),
            origin="web",
            confidence=getattr(web_data, "confidence", None),
            explainable=True,
            sources=getattr(web_data, "sources", None)
        )
