import time

class TempMemory:
    """
    Memória temporária entre execuções.
    Não é persistida em disco.
    Pode expirar por tempo (TTL).
    """

    def __init__(self):
        self._data: dict[str, tuple[object, float | None]] = {}

    def set(self, key: str, value: object, ttl_seconds: int | None = None) -> None:
        """
        Salva um valor temporário.
        ttl_seconds = tempo de vida em segundos (opcional)
        """
        expires_at = (
            time.time() + ttl_seconds
            if ttl_seconds is not None
            else None
        )
        self._data[key] = (value, expires_at)

    def get(self, key: str, default: object = None) -> object:
        """
        Obtém um valor, respeitando expiração.
        """
        if key not in self._data:
            return default

        value, expires_at = self._data[key]

        if expires_at is not None and time.time() > expires_at:
            del self._data[key]
            return default

        return value

    def has(self, key: str) -> bool:
        """Verifica se existe e não expirou."""
        return self.get(key, None) is not None

    def delete(self, key: str) -> None:
        """Remove um valor manualmente."""
        if key in self._data:
            del self._data[key]

    def clear(self) -> None:
        """Limpa toda a memória temporária."""
        self._data.clear()

    def cleanup(self) -> None:
        """Remove todos os itens expirados."""
        now = time.time()
        expired_keys = [
            key for key, (_, exp) in self._data.items()
            if exp is not None and now > exp
        ]
        for key in expired_keys:
            del self._data[key]

    def dump(self) -> dict:
        """
        Snapshot da memória válida (não expirada).
        """
        self.cleanup()
        return {k: v for k, (v, _) in self._data.items()}