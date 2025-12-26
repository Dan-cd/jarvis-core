import time
import json
from pathlib import Path

STATE_FILE = Path("Jarvis/data/dev_mode_state.json")

class DevModeGuard:
    def __init__(self, password: str):
        self.password = password
        self._load_state()

    def _load_state(self):
        if STATE_FILE.exists():
            self.state = json.loads(STATE_FILE.read_text())
        else:
            self.state = {
                "failures": 0,
                "blocked_until": 0
            }
            self._save_state()

    def _save_state(self):
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(self.state))

    def is_blocked(self) -> bool:
        return time.time() < self.state["blocked_until"]

    def validate(self, attempt: str) -> bool:
        if self.is_blocked():
            return False

        if attempt == self.password:
            self.state["failures"] = 0
            self.state["blocked_until"] = 0
            self._save_state()
            return True

        self.state["failures"] += 1
        self._apply_penalty()
        self._save_state()
        return False

    def _apply_penalty(self):
        failures = self.state["failures"]

        if failures <= 4:
            penalty = 5
        elif failures <= 6:
            penalty = 60
        elif failures <= 8:
            penalty = 3600
        else:
            penalty = 86400

        self.state["blocked_until"] = time.time() + penalty