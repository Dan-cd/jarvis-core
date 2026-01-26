# Jarvis/core/intent.py
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
import re


class IntentType(Enum):
    # operações de memória / dev
    MEMORY_WRITE = auto()
    MEMORY_READ = auto()
    DEV_ENTER = auto()
    DEV_EXIT = auto()

    # conteúdo (CRUD genérico)
    CONTENT_CREATE = auto()
    CONTENT_READ = auto()
    CONTENT_MODIFY = auto()
    CONTENT_DELETE = auto()
    CONTENT_MOVE = auto()

    # buscas / web / tempo real
    WEB_FETCH = auto()

    # ajuda / bate-papo
    HELP = auto()
    CHAT = auto()

    # fallback
    UNKNOWN = auto()


@dataclass(frozen=True)
class Intent:
    type: IntentType
    raw: str
    payload: dict = field(default_factory=dict)


class IntentEngine:
    """
    Motor simples de intenção.
    Regras:
      - Comandos de DEV (entrar/sair) são detectados por frases curtas específicas.
      - Comandos de memória por verbos (salvar, lembrar, guarde...).
      - Web fetch por verbos (pesquise, buscar) ou por padrão temporal (hoje, agora, cotação).
      - Conteúdo (criar/ler/modificar) por verbos CRUD simples.
      - Help por 'ajuda' e seus sinônimos.
      - Chat se a frase tem '?' ou é longa o bastante.
      - Fallback -> UNKNOWN
    """

    # palavras/expressões chave
    _DEV_ENTER = re.compile(r"\b(dev entrar|dev enter|dev enter:|@dev)\b", re.IGNORECASE)
    _DEV_EXIT = re.compile(r"\b(dev sair|dev exit|/devexit|exit dev)\b", re.IGNORECASE)

    _MEMORY_WRITE_WORDS = ("salve", "guarde", "memorize", "lembre", "gravar", "anote")
    _MEMORY_READ_PATTERNS = (
        r"o que você lembra",
        r"me lembre",
        r"mostre minha memória",
        r"lembre-me",
        r"o que eu pedi",
    )

    _WEB_VERBS = ("pesquise", "pesquisar", "procure", "buscar", "busca", "pesquisa", "search")
    _HELP_WORDS = ("ajuda", "help", "como faço", "o que é", "como usar")
    _CONTENT_CREATE_WORDS = ("criar", "novo", "gerar")
    _CONTENT_READ_WORDS = ("ler", "mostrar", "abrir", "exibir", "ver")
    _CONTENT_MODIFY_WORDS = ("editar", "modificar", "alterar", "atualizar")
    _CONTENT_DELETE_WORDS = ("deletar", "remover", "apagar", "excluir")

    # padrões simples de sensibilidade temporal (usado também pelo router)
    _TIME_PATTERNS = ("agora", "hoje", "neste momento", "cotação", "preço", "últimas notícias", "última notícia", "atualmente")

    def parse(self, text: str) -> Optional[Intent]:
        raw = (text or "").strip()
        if not raw:
            return None

        lowered = raw.lower()

        # Dev mode explicit
        if self._DEV_ENTER.search(raw):
            return Intent(IntentType.DEV_ENTER, raw)
        if self._DEV_EXIT.search(raw):
            return Intent(IntentType.DEV_EXIT, raw)

        # Memory write detection
        if any(word in lowered for word in self._MEMORY_WRITE_WORDS):
            return Intent(IntentType.MEMORY_WRITE, raw)

        # Memory read detection (phrases)
        if any(re.search(pat, lowered) for pat in self._MEMORY_READ_PATTERNS):
            return Intent(IntentType.MEMORY_READ, raw)

        # Web explicit verbs
        if any(v in lowered for v in self._WEB_VERBS):
            return Intent(IntentType.WEB_FETCH, raw)

        # Help detection (start phrases or single word)
        if any(h in lowered for h in self._HELP_WORDS) or lowered.strip() in ("ajuda", "help"):
            return Intent(IntentType.HELP, raw)

        # Content operations (CRUD-ish)
        if any(w in lowered for w in self._CONTENT_CREATE_WORDS):
            return Intent(IntentType.CONTENT_CREATE, raw)
        if any(w in lowered for w in self._CONTENT_MODIFY_WORDS):
            return Intent(IntentType.CONTENT_MODIFY, raw)
        if any(w in lowered for w in self._CONTENT_DELETE_WORDS):
            return Intent(IntentType.CONTENT_DELETE, raw)
        if any(w in lowered for w in self._CONTENT_READ_WORDS):
            return Intent(IntentType.CONTENT_READ, raw)

        # Time-sensitive heuristics that should be handled by Router as well.
        if any(p in lowered for p in self._TIME_PATTERNS):
            # sinaliza como WEB_FETCH para garantir roteamento coerente com policy/router
            return Intent(IntentType.WEB_FETCH, raw)

        # Heurística para chat: interrogação ou frase de mais de 3 palavras
        if "?" in raw or len(raw.split()) > 3:
            return Intent(IntentType.CHAT, raw)

        # Fallback: se nenhuma regra bate, devolve UNKNOWN (Router decidirá)
        return Intent(IntentType.UNKNOWN, raw)
