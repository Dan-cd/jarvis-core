from enum import Enum, auto
from dataclasses import dataclass, field
import re


# PALAVRAS-CHAVE


MEMORY_VERBS = (
    "salve", "guarde", "lembre", "memorize", "grave"
)

MEMORY_READ_PATTERNS = (
    "qual é meu nome",
    "qual meu nome",
    "como me chamo",
    "quem sou eu",
    "o que você lembra",
    "o que você lembra de mim",
    "você lembra de mim",
    "liste memórias",
    "suas memórias",
)

CREATE_VERBS = (
    "criar", "crie", "salvar", "gerar", "produzir"
)

READ_VERBS = (
    "ler", "leia", "abrir", "abra", "mostrar", "ver"
)

MODIFY_VERBS = (
    "editar", "alterar", "modificar", "adicionar", "atualizar"
)

DELETE_VERBS = (
    "apagar", "excluir", "deletar", "delete", "exclua", "apague"
)

MOVE_VERBS = (
    "mover", "transferir", "mova", "transfira"
)

WEB_VERBS = (
    "pesquise", "pesquisar", "procure", "buscar",
    "busca", "pesquisa", "google", "bing"
)


# TIPOS DE INTENÇÃO (V6)


class IntentType(Enum):
    # Memória
    MEMORY_WRITE = "memory.write"
    MEMORY_READ = "memory.read"

    # Dev Mode
    DEV_ENTER = auto()
    DEV_EXIT = auto()

    # Conteúdo (abstrato)
    CONTENT_CREATE = auto()
    CONTENT_READ = auto()
    CONTENT_MODIFY = auto()
    CONTENT_DELETE = auto()
    CONTENT_MOVE = auto()

    # Web
    WEB_FETCH = auto()

    # Conversa
    HELP = auto()
    CHAT = auto()
    UNKNOWN = auto()


# MODELO DE INTENT


@dataclass(frozen=True)
class Intent:
    type: IntentType
    raw: str
    payload: dict = field(default_factory=dict)


# INTENT ENGINE V6


class IntentEngine:
    """
    V6 — IntentEngine HUMANO
    Identifica apenas o que o usuário quer fazer.
    Não conhece plugins, arquivos, web ou execução.
    """

    def parse(self, text: str) -> Intent | None:
        raw = text.strip()
        lower = raw.lower()

        if not raw:
            return None

        # DEV MODE
        if "dev" in lower and any(k in lower for k in ("entrar", "enter")):
            return Intent(IntentType.DEV_ENTER, raw)

        if "dev" in lower and any(k in lower for k in ("sair", "exit")):
            return Intent(IntentType.DEV_EXIT, raw)

        # MEMÓRIA
        if any(v in lower for v in MEMORY_VERBS):
            return Intent(IntentType.MEMORY_WRITE, raw)

        if any(p in lower for p in MEMORY_READ_PATTERNS):
            return Intent(IntentType.MEMORY_READ, raw)

        #  WEB — prioridade sobre conteúdo
        if any(v in lower for v in WEB_VERBS):
            return Intent(IntentType.WEB_FETCH, raw)

        # CONTEÚDO (abstrato)
        if any(v in lower for v in CREATE_VERBS):
            return Intent(IntentType.CONTENT_CREATE, raw)

        # cuidado com "ver" → palavra isolada
        if any(
            re.search(rf"\b{re.escape(v)}\b", lower)
            for v in READ_VERBS
        ):
            return Intent(IntentType.CONTENT_READ, raw)

        if any(v in lower for v in MODIFY_VERBS):
            return Intent(IntentType.CONTENT_MODIFY, raw)

        if any(v in lower for v in DELETE_VERBS):
            return Intent(IntentType.CONTENT_DELETE, raw)

        if any(v in lower for v in MOVE_VERBS):
            return Intent(IntentType.CONTENT_MOVE, raw)

        # HELP / CHAT
        if lower.startswith(("ajuda", "help", "como usar")):
            return Intent(IntentType.HELP, raw)

        # Se não é ação → conversa
        if "?" in raw or len(raw.split()) > 3:
            return Intent(IntentType.CHAT, raw)

        return Intent(IntentType.UNKNOWN, raw)
