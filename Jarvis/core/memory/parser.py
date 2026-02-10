import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class MemoryFact:
    def __init__(self, content: str):
        self.content = content


class MemoryParser:
    """
    Parser determinístico de memória.
    Converte frases explícitas em fatos estruturados.
    """

    NAME_PATTERNS = [
        r"(?:meu nome é|me chamo)\s+(?P<value>[A-Za-zÀ-ÿ]+)",
        r"salve na memória que meu nome é\s+(?P<value>[A-Za-zÀ-ÿ]+)",
    ]

    @classmethod
    def parse(cls, text: str) -> Optional[MemoryFact]:
        text = text.lower().strip()

        # Nome do usuário
        fact = cls._parse_name(text)
        if fact:
            return fact

        return None

    @classmethod
    def _parse_name(cls, text: str) -> Optional[MemoryFact]:
        for pattern in cls.NAME_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group("value").strip().capitalize()
                return MemoryFact(
                    content=text
                    )
        return None