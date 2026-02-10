from typing import List
import uuid
from datetime import datetime
from Jarvis.core.memory.store import MemoryStore
from Jarvis.core.memory.models import MemoryItem, MemoryType
from Jarvis.core.memory.parser import MemoryParser


class MemoryManager:
    def __init__(self, store: MemoryStore):
        self.store = store

    def remember(self, text: str) -> bool:
        fact = MemoryParser.parse(text)

        if not fact:
            return False

        memory = MemoryItem.create(
            type=MemoryType.FACT,
            content=fact.content,
            source="user"
        )

        self.store.save(memory)
        return True

    def recall(self, type: MemoryType | None = None) -> List[MemoryItem]:
        memories = self.store.load_all()
        if type:
            return [m for m in memories if m.type == type]
        return memories