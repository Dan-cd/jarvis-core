from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import uuid4


class MemoryType(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    PROJECT = "project"
    TASK = "task"


@dataclass
class MemoryItem:
    id: str
    type: MemoryType
    content: str
    source: str
    created_at: datetime
    confidence: float = 1.0

    @staticmethod
    def create(
        type: MemoryType,
        content: str,
        source: str = "user",
        confidence: float = 1.0
    ) -> "MemoryItem":
        return MemoryItem(
            id=str(uuid4()),
            type=type,
            content=content,
            source=source,
            created_at=datetime.now(), 
            confidence=confidence
        )