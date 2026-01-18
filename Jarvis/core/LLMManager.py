from typing import List, Optional

from Jarvis.core.llm_contract import LLMInterface, LLMRequest, LLMResponse
from Jarvis.modules.llm.groq import GroqLLM
from Jarvis.modules.llm.ollama import OllamaLLM
from Jarvis.core.errors import JarvisError


class LLMManager(LLMInterface):
    """
    Gerencia múltiplos provedores LLM e implementa fallback.
    Política escolhida (v6.5): tentar providers na ordem
    configurada (ou default), retornando o primeiro sucesso.
    Falhas são registradas via JarvisError ou propagadas.
    """

    def __init__(self, config: Optional[dict] = None, error_manager=None):
        # configurações e gerenciador de erros (opcional)
        self.config = config or {}
        self.error_manager = error_manager

        # inicializa lista de providers na ordem desejada
        self.providers: List[LLMInterface] = self._init_providers()

    def _init_providers(self) -> List[LLMInterface]:
        """
        Inicializa instâncias de providers a partir da configuração.
        Se não houver configuração, usamos a ordem por padrão:
        GroqLLM -> OllamaLLM
        """
        order = self.config.get("llm_providers", ["groq", "ollama"])
        providers: List[LLMInterface] = []

        for name in order:
            name_lower = name.lower()
            if name_lower == "groq":
                providers.append(GroqLLM(self.config.get("groq", {})))
            elif name_lower == "ollama":
                providers.append(OllamaLLM(self.config.get("ollama", {})))
            else:
                # ignorar providers desconhecidos (log leve)
                continue

        # se por algum motivo a lista ficou vazia, garantimos um provider mínimo
        if not providers:
            providers.append(GroqLLM({}))
        return providers

    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Tenta cada provider na ordem. Se falhar em todos, levanta JarvisError.
        Mantém o fallback dentro do LLMManager (modo B).
        """
        last_exception: Optional[Exception] = None

        for provider in self.providers:
            try:
                # Tenta gerar com o provider atual
                response = provider.generate(request)
                # Se o provider retornar algo que parece um LLMResponse, retorna
                if isinstance(response, LLMResponse):
                    return response
                # Caso contrário, tentamos encapsular se possível
                # (aceita também respostas em formato {text: ...})
                if hasattr(response, "text"):
                    return response
                if isinstance(response, dict) and "text" in response:
                    return LLMResponse(text=response["text"])
                # se nada disso, continuamos para próximo provider
            except Exception as e:
                last_exception = e
                # registra via error_manager quando disponível
                try:
                    if self.error_manager:
                        # encapsula para persistência/registro
                        self.error_manager.handle(
                            JarvisError(
                                message=f"Provider {provider.__class__.__name__} falhou: {e}",
                                origin="llm",
                                module="LLMManager",
                                function="generate",
                                original_exception=e,
                            )
                        )
                    else:
                        # fallback mínimo: print para log
                        print(f"[LLMManager] Provider {provider.__class__.__name__} failed: {e}")
                except Exception:
                    # evitamos que o error handler quebre o fluxo de tentativas
                    pass
                # tenta próximo provider

        # Se chegamos aqui, todos providers falharam
        raise JarvisError(
            message="Todos os provedores LLM falharam.",
            origin="llm",
            module="LLMManager",
            function="generate",
            original_exception=last_exception,
        )
