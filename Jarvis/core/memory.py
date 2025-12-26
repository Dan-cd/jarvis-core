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
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data: list):
        self.path.write_text(
            json.dumps(data[-self.limit:], indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def remember(self, role: str, content: str):
        memory = self._load()
        memory.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save(memory[-self.limit:])

    def recall(self) -> list:
        return self._load()
    

    def context(self) -> list:
        data = self._load()
        return [
        {"role": m["role"], "content": m["content"]}
        for m in data
        ]
    
    def log_action(self, description: str):
        data = self._load()
        data.append({
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
        self._save(data)

    def get_recent_actions(self) -> list[str]:
        return [item["description"] for item in self._load()]