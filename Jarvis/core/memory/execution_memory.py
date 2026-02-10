
class ExecutionMemory:
    """
    Memória de curtíssimo prazo.
    Vive apenas durante uma execução (1 comando do usuário).
    """

    def __init__(self):
        self._data: dict[str, object] = {}

    def set(self, key: str, value: object) -> None:
        """Salva um dado na memória da execução atual."""
        self._data[key] = value

    def get(self, key: str, default: object = None) -> object:
        """Obtém um dado salvo, ou default se não existir."""
        return self._data.get(key, default)

    def has(self, key: str) -> bool:
        """Verifica se uma chave existe."""
        return key in self._data

    def delete(self, key: str) -> None:
        """Remove um dado específico."""
        if key in self._data:
            del self._data[key]

    def clear(self) -> None:
        """Limpa toda a memória da execução."""
        self._data.clear()

    def dump(self) -> dict:
        """
        Retorna um snapshot da memória.
        Útil para debug ou Dev Mode.
        """
        return dict(self._data)