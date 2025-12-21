import json
from pathlib import Path
from datetime import datetime

class Memory:
    def __init__(self, path: str = "data/memory/short_term_memory.json", limit: int = 20):
        self.path = Path(path)
        self.limit = limit
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save([])

    def _load(self) -> list:
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: list):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def remember(self, role: str, content: str):
        memory = self._load()
        memory.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._save(memory)

    def recall(self) -> list:
        return self._load()

    def clear(self):
        self._save([])

    # Backwards-compatible API used by LLMRouter
    def get_context(self) -> list:
        data = self._load()
        return data[-self.limit:]

    def add(self, user_text: str, assistant_text: str):
        self.remember("user", user_text)
        self.remember("assistant", assistant_text)