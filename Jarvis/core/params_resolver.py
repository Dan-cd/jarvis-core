import re
from Jarvis.core.intent import IntentType


class ParamsResolver:
    """
    V6 — Extrai parâmetros de forma humanizada e tolerante.

    Responsabilidades:
    - Recebe texto cru do usuário
    - Extrai parâmetros relevantes (filename, content, target)
    - NÃO valida
    - NÃO executa
    - NÃO decide regras ou permissões
    """

    def resolve(self, intent_type: IntentType, raw_text: str) -> dict:
        text = raw_text.strip()

        match intent_type:
            case IntentType.FILE_READ | IntentType.FILE_PDF_READ | IntentType.FILE_DELETE:
                return self._resolve_single_file(text)

            case IntentType.FILE_CREATE:
                return self._resolve_write(text)

            case IntentType.FILE_EDIT:
                return self._resolve_edit(text)

            case IntentType.FILE_MOVE:
                return self._resolve_move(text)

        return {}

   
    # UTILITÁRIOS DE EXTRAÇÃO
    

    def _strip_content_part(self, text: str) -> str:
        """
        Remove partes do texto que indicam conteúdo,
        preservando apenas a parte que contém o nome do arquivo.
        """
        patterns = [
            r"(?:com|conteúdo|texto)\s+.+$",
            r"(?:adicionando|acrescentando|incluindo)\s+.+$",
        ]

        for pattern in patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        return text.strip()

    def _extract_filename(self, text: str) -> str | None:
        """
        Extrai o nome do arquivo do texto.
        Prioridade:
        1. Texto entre aspas
        2. Último token com ponto (.)
        """
        text = self._strip_content_part(text)

        quoted = re.findall(r'"([^"]+)"', text)
        if quoted:
            return quoted[0]

        tokens = re.findall(r"\S+", text)
        for token in reversed(tokens):
            if "." in token:
                return token.strip(",.;:")

        return None

    def _extract_destination(self, text: str) -> str | None:
        """
        Extrai destino para operações de mover.
        """
        patterns = [
            r"\bpara\s+(.+)$",
            r"\bdentro\s+de\s+(.+)$",
            r"\bem\s+(.+)$",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_content_generic(self, text: str, markers: list[str]) -> str:
        """
        Extrai conteúdo textual a ser escrito/editado.
        """
        quoted = re.findall(r'"([^"]+)"', text)
        if quoted:
            return quoted[-1].strip()

        lower = text.lower()
        for marker in markers:
            if marker in lower:
                idx = lower.index(marker) + len(marker)
                return text[idx:].strip()

        patterns = [
            r"(?:com|conteúdo|texto)\s+(.+)",
            r"(?:adicionando|acrescentando|incluindo)\s+(.+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""

    
    # RESOLVERS POR INTENT
   

    def _resolve_single_file(self, text: str) -> dict:
        return {
            "filename": self._extract_filename(text)
        }

    def _resolve_write(self, text: str) -> dict:
        return {
            "filename": self._extract_filename(text),
            "content": self._extract_content_generic(
                text,
                markers=["com", "conteúdo", "texto", "escrevendo"]
            )
        }

    def _resolve_edit(self, text: str) -> dict:
        return {
            "filename": self._extract_filename(text),
            "content": self._extract_content_generic(
                text,
                markers=[
                    "adicionando",
                    "acrescentando",
                    "inserindo",
                    "escrevendo",
                    "colocando"
                ]
            )
        }

    def _resolve_move(self, text: str) -> dict:
        return {
            "filename": self._extract_filename(text),
            "target": self._extract_destination(text)
        }