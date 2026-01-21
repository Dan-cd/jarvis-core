from enum import Enum, auto
from dataclasses import dataclass, field
import re

# PALAVRAS-CHAVE para detecção
MEMORY_VERBS = (
    "salve", "guarde", "lembre", "memorize", "grave"
)
MEMORY_READ_PATTERNS = (
    "qual é meu nome", "qual meu nome", "como me chamo", "quem sou eu",
    "o que você lembra", "o que você lembra de mim"
)
WEB_VERBS = ("pesquise", "pesquisar", "procure", "buscar", "busca", "pesquisa")
HELP_PATTERN = ("ajuda", "help", "como usar")

class IntentType(Enum):
    MEMORY_WRITE = auto()
    MEMORY_READ = auto()
    DEV_ENTER = auto()
    DEV_EXIT = auto()
    CONTENT_CREATE = auto()
    CONTENT_READ = auto()
    CONTENT_MODIFY = auto()
    CONTENT_DELETE = auto()
    CONTENT_MOVE = auto()
    WEB_FETCH = auto()
    HELP = auto()
    CHAT = auto()
    UNKNOWN = auto()

@dataclass(frozen=True)
class Intent:
    type: IntentType
    raw: str
    payload: dict = field(default_factory=dict)

class IntentEngine:
    """
    Identifica a intenção básica a partir do texto.
    """

    def parse(self, text: str) -> Intent | None:
        raw = text.strip()
        lower = raw.lower()
        if not raw:
            return None

        # DEV MODE
        if "dev entrar" in lower or "dev enter" in lower:
            return Intent(IntentType.DEV_ENTER, raw)
        if "dev sair" in lower or "dev exit" in lower:
            return Intent(IntentType.DEV_EXIT, raw)

        # Memória
        if any(v in lower for v in MEMORY_VERBS):
            return Intent(IntentType.MEMORY_WRITE, raw)
        if any(p in lower for p in MEMORY_READ_PATTERNS):
            return Intent(IntentType.MEMORY_READ, raw)

        # Web
        if any(v in lower for v in WEB_VERBS):
            return Intent(IntentType.WEB_FETCH, raw)

        # Conteúdo abstrato
        if "criar" in lower:
            return Intent(IntentType.CONTENT_CREATE, raw)
        if any(re.search(rf"\b{re.escape(v)}\b", lower) for v in ("ler", "mostrar", "ver")):
            return Intent(IntentType.CONTENT_READ, raw)

        # Help
        if lower.startswith(HELP_PATTERN):
            return Intent(IntentType.HELP, raw)

        # Se “?” ou frase longa → conversa
        if "?" in raw or len(raw.split()) > 3:
            return Intent(IntentType.CHAT, raw)

        # Default fallback
        return Intent(IntentType.UNKNOWN, raw)
