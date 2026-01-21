from typing import Optional
import os


class Config:
    """
    Centraliza todas as configurações do Jarvis.
    Carrega valores de ambiente ou usa defaults.
    """

    def __init__(self):
        # MODO
        self.dev_mode: bool = self._get_bool("JARVIS_DEV_MODE", default=False)
        self.offline: bool = self._get_bool("JARVIS_OFFLINE", default=False)

        # LLM MODELS
        self.GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
        self.GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        self.OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

        # Flags gerais
        self.allow_web: bool = self._get_bool("JARVIS_ALLOW_WEB", default=True)
        self.allow_llm: bool = self._get_bool("JARVIS_ALLOW_LLM", default=True)

        # Outros parâmetros podem ser adicionados aqui
        # (tempo de timeout, preferências de fontes, cache TTL, etc)

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
