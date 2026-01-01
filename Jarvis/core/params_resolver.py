import re
from Jarvis.core.intent import IntentType


class ParamsResolver:
    """
    V5 — Extrai parâmetros estruturados
    a partir do texto bruto.
    """

    def resolve(self, intent_type: IntentType, raw_text: str) -> dict:
        match intent_type:
            case IntentType.FILE_READ:
                return self._resolve_with_path(raw_text)

            case IntentType.FILE_READ_PDF:
                return self._resolve_with_path(raw_text)

            case IntentType.FILE_CREATE:
                return self._resolve_create(raw_text)

            case IntentType.FILE_EDIT:
                return self._resolve_edit(raw_text)

            case IntentType.FILE_DELETE:
                return self._resolve_with_path(raw_text)

            case IntentType.FILE_MOVE:
                return self._resolve_move(raw_text)

        return {}

    # --------------------
    # Helpers
    # --------------------

    def _extract_filename(self, text: str) -> str | None:
        quoted = re.findall(r'"([^"]+)"', text)
        if quoted:
            return quoted[0]

        for part in reversed(text.split()):
            if "." in part:
                return part

        return None

    def _extract_path(self, text: str) -> str | None:
        match = re.search(r"\bem\s+([A-Za-z0-9_/~-]+)", text)
        if match:
            return match.group(1)
        return None

    # --------------------
    # Resolvers
    # --------------------

    def _resolve_with_path(self, text: str) -> dict:
        return {
            "filename": self._extract_filename(text),
            "path": self._extract_path(text)
        }

    def _resolve_create(self, text: str) -> dict:
        filename = self._extract_filename(text)
        path = self._extract_path(text)

        content = ""
        if "com" in text:
            content = text.split("com", 1)[1].strip()

        return {
            "filename": filename,
            "path": path,
            "content": content
        }

    def _resolve_edit(self, text: str) -> dict:
        filename = self._extract_filename(text)
        path = self._extract_path(text)

        content = None
        if "adicionando" in text:
            content = text.split("adicionando", 1)[1].strip()
        elif "com" in text:
            content = text.split("com", 1)[1].strip()

        return {
            "filename": filename,
            "path": path,
            "content": content
        }

    def _resolve_move(self, text: str) -> dict:
        filename = self._extract_filename(text)

        source = None
        target = None

        if "de" in text and "para" in text:
            source = text.split("de", 1)[1].split("para", 1)[0].strip()
            target = text.split("para", 1)[1].strip()

        return {
            "filename": filename,
            "source": source,
            "target": target
        }