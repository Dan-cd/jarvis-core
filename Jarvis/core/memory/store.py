import json
from pathlib import Path
from typing import List
from datetime import datetime
from Jarvis.core.memory.models import MemoryItem, MemoryType


class MemoryStore:
    def __init__(self, path: str = "Jarvis/data/memory.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self._write([])

    def _read(self) -> List[dict]:
        try:
            text = self.path.read_text(encoding="utf-8").strip()
            if not text:
                return []
            return json.loads(text)
        except json.JSONDecodeError:
            return []

    def _write(self, data: List[dict]):
        self.path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def save(self, memory: MemoryItem):
        data = self._read()
        data.append({
            "id": memory.id,
            "type": memory.type.value,
            "content": memory.content,
            "source": memory.source,
            "created_at": memory.created_at.isoformat(), 
            "confidence": memory.confidence
        })
        self._write(data)

    def load_all(self) -> List[MemoryItem]:
        items = []
        for raw in self._read():
            items.append(
                MemoryItem(
                    id=raw["id"],
                    type=MemoryType(raw["type"]),
                    content=raw["content"],
                    source=raw["source"],
                    created_at=datetime.fromisoformat(raw["created_at"]),  
                    confidence=raw.get("confidence", 1.0)
                )
            )
        return items