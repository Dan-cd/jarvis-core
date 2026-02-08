# Jarvis/core/LLMManager.py

from typing import Optional
from Jarvis.core.errors import LLMUnavailable, LLMExecutionError

SYSTEM_PROMPT = (
    "You are Jarvis, an expert and helpful assistant. "
    "Always answer as 'Jarvis' and do not mention being a model, "
    "training, architecture, internal details, or provider. "
    "Provide clear answers, and when sources are included, reference them after the main response."
)

class LLMManager:
    """
    Orquestra provedor(es) de linguagem.
    Insere um prompt de sistema institucional forte,
    aplica fallback quando necessário,
    e retorna apenas texto pronto para a camada superior.
    """

    def __init__(self, primary_llm=None, fallback_llm=None, context=None):
        self.primary_llm = primary_llm
        self.fallback_llm = fallback_llm
        self.context = context

    def available(self) -> bool:
        """
        Indica se algum LLM está configurado.
        """
        return self.primary_llm is not None or self.fallback_llm is not None

    def generate(self, prompt: str, mode: str = "default") -> str:
        """
        Gera resposta usando o LLM primário, com fallback automático.
        O prompt da aplicação já deve incluir instruções contextuais.
        """
        if not self.available():
            raise LLMUnavailable("Nenhum LLM disponível para execução.")

        try:
            return self._generate_with(self.primary_llm, prompt, mode)
        except Exception as e:
            if not self.fallback_llm:
                # Sem fallback → erro definitivo
                raise LLMExecutionError(
                    f"Falha no LLM primário e fallback indisponível: {e}"
                )
            # Tenta fallback
            try:
                return self._generate_with(self.fallback_llm, prompt, mode)
            except Exception as e2:
                raise LLMExecutionError(
                    f"Falha no fallback LLM: {e2}"
                )

    def _generate_with(self, llm, prompt: str, mode: str) -> str:
        """
        Realiza a chamada ao provider real de LLM.
        Adaptamos para dois cenários:
          - providers que usam mensagens (chat)
          - providers que usam string (prompt puro)
        """

        # Monta as instruções completas:
        # Primeiro o system prompt, depois a query do usuário
        final_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

        if not hasattr(llm, "generate"):
            raise LLMExecutionError("LLM não implementa método generate().")

        # Detecta se o provider espera um objeto ou listas de mensagens
        try:
            response = llm.generate(final_prompt, mode=mode)
        except TypeError:
            # Alguns providers (como Groq) usam LLMRequest/LLMResponse
            try:
                from Jarvis.core.llm_contract import LLMRequest, LLMResponse
            except ImportError:
                raise LLMExecutionError("Interface de contrato de LLM não encontrada.")

            # Recria o request com texto e regras
            request = LLMRequest(
                system_rules=SYSTEM_PROMPT,
                prompt=prompt,
                mode=mode
            )
            resp = llm.generate(request)
            # pode retornar LLMResponse ou string
            if isinstance(resp, LLMResponse):
                return resp.text
            if isinstance(resp, str):
                return resp
            raise LLMExecutionError("LLM retornou formato inesperado.")

        # Se chegou aqui, assumimos que a resposta é string
        return response
