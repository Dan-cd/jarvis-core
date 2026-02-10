# Jarvis/core/LLMManager.py

from typing import Optional
from Jarvis.core.errors import LLMUnavailable, LLMExecutionError
from Jarvis.core.llm_contract import LLMVerbosity

SYSTEM_PROMPT = (
    "Você é o JARVIS, um sistema de assistência arquitetural avançado. "
    "Sua identidade: "
    "1. Você NÃO é uma IA generativa comum; você é parte de um sistema maior. "
    "2. Você utiliza ferramentas (LLMs, plugins, execução de código) para resolver tarefas. "
    "3. Você é objetivo, profissional e levemente formal. "
    "4. Idioma obrigatório: Português (Brasil). "
    "Limites: "
    "1. NÃO invente que tem acesso externo se não tiver. "
    "2. NÃO invente memórias passadas. "
    "3. Se não souber, diga 'Não tenho essa informação no meu contexto atual'. "
    "Responda à pergunta do usuário agindo conforme essa identidade."
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
            # Log ou print opcional aqui
            # print(f"[LLMManager] Primário falhou: {e}")
            
            if not self.fallback_llm:
                # Sem fallback → erro definitivo
                raise LLMExecutionError(
                    f"Falha no LLM primário e fallback indisponível: {e}"
                )
            # Tenta fallback
            try:
                # Fallback pode ser Ollama ou outro local
                return self._generate_with(self.fallback_llm, prompt, mode)
            except Exception as e2:
                raise LLMExecutionError(
                    f"Falha no fallback LLM: {e2}. Erro original: {e}"
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

            # Mapear 'mode' para 'verbosity' do contrato quando possível
            verbosity = LLMVerbosity.NORMAL
            try:
                if isinstance(mode, str):
                    mode_l = mode.lower()
                    if mode_l in LLMVerbosity._value2member_map_:
                        verbosity = LLMVerbosity(mode_l)
            except Exception:
                verbosity = LLMVerbosity.NORMAL

            # Recria o request com texto e regras (sem passar 'mode' inválido)
            request = LLMRequest(
                system_rules=SYSTEM_PROMPT,
                prompt=prompt,
                verbosity=verbosity
            )
            resp = llm.generate(request)
            # pode retornar LLMResponse ou string
            if isinstance(resp, LLMResponse):
                return resp.text
            if isinstance(resp, str):
                return resp
            raise LLMExecutionError("LLM retornou formato inesperado.")

        # Se chegou aqui, response pode ser string ou LLMResponse (dependendo se caiu no except TypeError ou não)
        # Duck typing: se tem atributo .text e não é string, assumimos que é um wrapper de resposta
        if hasattr(response, "text") and not isinstance(response, str):
            val = response.text
            # Se .text for callable, chama (im improvável, mas defensivo)
            if callable(val):
                return str(val())
            return str(val)

        return response
