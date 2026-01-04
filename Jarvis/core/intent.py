from enum import Enum, auto
from dataclasses import dataclass, field

MEMORY_VERBS = [
    "salve",
    "guarde",
    "lembre",
    "memorize",
    "grave"
]

MEMORY_KEYWORDS = [
    "memória",
    "memoria"
]
MEMORY_READ_PATTERNS = [
    "qual é meu nome",
    "qual meu nome",
    "como me chamo",
    "quem sou eu",
    "o que você lembra",
    "o que você lembra de mim",
    "voce lembra de mim",
]

class IntentType(Enum):
    MEMORY_WRITE = "memory.write"
    MEMORY_READ = "memory.read"

    DEV_ENTER = auto()
    DEV_EXIT = auto()

    FILE_CREATE = auto()
    FILE_READ = auto()
    FILE_PDF_READ = auto()
    FILE_DELETE = auto()
    FILE_MOVE = auto()
    FILE_EDIT = auto()

    HELP = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class Intent:
    type: IntentType
    raw: str
    payload: dict = field(default_factory=dict)


class IntentEngine:
    """
    V5 — IntentEngine puro.
    Apenas identifica intenção.
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

        # MEMORY — vem ANTES de filesystem
        if any(v in lower for v in MEMORY_VERBS):
            return Intent(IntentType.MEMORY_WRITE, raw)
        

        if any(p in lower for p in MEMORY_READ_PATTERNS):
            return Intent(IntentType.MEMORY_READ, raw)

            
        if any(k in lower for k in (
            "o que você lembra",
            "suas memórias",
            "liste memórias",
            "qual é meu nome",
            "o que você lembra de mim"
        )):
            return Intent(IntentType.MEMORY_READ, raw)

        # FILESYSTEM
        if any(k in lower for k in ("ler", "leia", "abrir", "mostrar", "abra")):
            return Intent(IntentType.FILE_READ, raw)
        if any(k in lower for k in (".pdf", "ler", "pdf", "leia", "resumo pdf", "resumo do pdf")):
            return Intent(IntentType.FILE_PDF_READ, raw)

        if any(k in lower for k in ("criar", "crie", "salvar")):
            return Intent(IntentType.FILE_CREATE, raw)

        if any(k in lower for k in ("editar", "alterar", "adicionar", "modificar", "edite")):
            return Intent(IntentType.FILE_EDIT, raw)

        if any(k in lower for k in ("apagar", "excluir", "deletar", "delete", "exclua", "apague")):
            return Intent(IntentType.FILE_DELETE, raw)

        if any(k in lower for k in ("mover", "transferir", "mova", "transfira")):
            return Intent(IntentType.FILE_MOVE, raw)

        return Intent(IntentType.UNKNOWN, raw)