import re
from Jarvis.core.intent import IntentResult

class IntentClassifier:

    def classify(self, text: str) -> IntentResult:
        text_lower = text.lower().strip()

        if text_lower in ("exit", "quit", "sair"):
            return IntentResult("command", 1.0, text)
        
        if text_lower.startswith("entrar no modo dev") or text_lower.startswith("entrar no dev mode"):
            return IntentResult("dev", 0.9, text)
        
        if re.match(r"(o que|porque|por que|como|onde|quando|quem)", text_lower):
            return IntentResult("question", 0.7, text)
        
        return IntentResult("unknown", 0.3, text)