# Jarvis/core/config.py
from typing import Optional
import os
import sys


class Config:
    """
    Centraliza todas as configurações do Jarvis.
    Carrega valores de ambiente ou usa defaults.
    Esta classe é pensada para ser instanciada e passada para os componentes.
    """

    def __init__(self):
        # MODE
        self.dev_mode: bool = self._get_bool("JARVIS_DEV_MODE", default=False)
        self.offline: bool = self._get_bool("JARVIS_OFFLINE", default=False)

        # LLM MODELS / Keys
        self.GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
        self.GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        self.OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

        # Flags gerais
        self.allow_web: bool = self._get_bool("JARVIS_ALLOW_WEB", default=True)
        self.allow_llm: bool = self._get_bool("JARVIS_ALLOW_LLM", default=True)

        # Outros parâmetros (padrões sensatos)
        self.WEB_TIMEOUT_SECONDS: int = int(os.getenv("JARVIS_WEB_TIMEOUT", "10"))
        self.WEB_CACHE_TTL_SECONDS: int = int(os.getenv("JARVIS_WEB_CACHE_TTL", "3600"))

    def _get_bool(self, name: str, default: bool) -> bool:
        """
        Lê booleano de ambiente (ex: 'true', '1', 'yes', 'on').
        """
        val = os.getenv(name)
        if val is None:
            return default
        return val.strip().lower() in ("1", "true", "yes", "on")

    def get(self, key: str, default=None):
        """
        Acesso dinâmico seguro a um atributo.
        """
        return getattr(self, key, default)

    def validate(self, fatal_on_missing: bool = False) -> bool:
        """
        Validação leve das configurações essenciais.
        - Se fatal_on_missing=True, sai do processo quando uma configuração crítica estiver faltando.
        - Retorna True se a validação passou, False caso contrário.
        """
        ok = True
        missing = []

        # Exemplo: GROQ_API_KEY é opcional (pode usar Ollama), mas logamos se ausente.
        if not self.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")

        # OLLAMA model tem default, então não é crítico
        # Se tanto GROQ quanto OLLAMA não estiverem disponíveis, o sistema fica sem LLM
        if not (self.GROQ_API_KEY or self.OLLAMA_MODEL):
            ok = False
            missing.append("GROQ_API_KEY or OLLAMA_MODEL")

        # Comportamento ao encontrar problemas
        if missing:
            msg = f"Config: chaves/config ausentes ou padrão(s) insuficiente(s): {', '.join(missing)}"
            if fatal_on_missing:
                print(f"[Config.validate] ERRO FATAL: {msg}", file=sys.stderr)
                sys.exit(2)
            else:
                # alerta, mas não encerra
                print(f"[Config.validate] Aviso: {msg}", file=sys.stderr)

        return ok
