import time
import hashlib
from typing import Optional
from Jarvis.plugins_available.web.models import WebResult


class WebCache:
    def __init__(self):
        self._store: dict[str, tuple[float, WebResult]] = {}

    def _make_key(self, query: str) -> str:
        normalized = query.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()

    def get(self, query: str) -> Optional[WebResult]:
        key = self._make_key(query)
        if key not in self._store:
            return None

        expires_at, result = self._store[key]
        if time.time() > expires_at:
            del self._store[key]
            return None

        return result

    def set(self, query: str, result: WebResult, ttl: int = 300):
        # Não cachear resultados sem conteúdo textual relevante
        try:
            if not getattr(result, "content", None):
                return
        except Exception:
            return

        key = self._make_key(query)
        expires_at = time.time() + ttl
        self._store[key] = (expires_at, result)
