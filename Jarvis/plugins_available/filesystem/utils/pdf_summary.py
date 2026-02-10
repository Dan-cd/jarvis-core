import re
from Jarvis.core.llm_contract import LLMRequest

def _deterministic_summary(text: str, max_lines: int = 6) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    summary = sentences[:max_lines]
    return "\n".join(f"- {s}" for s in summary if len(s) > 20)


def summarize_text(
    text: str,
    llm=None,
    max_lines: int = 6
) -> str:
    """
    Resumo híbrido:
    - Com LLM: resumo semântico
    - Sem LLM: fallback determinístico
    """

    # Proteção básica
    if not text or len(text) < 100:
        return ""

    # === CAMINHO LLM ===
    if llm:
        try:
            prompt = (
                "Resuma o texto abaixo de forma clara e objetiva, "
                "em até 6 tópicos curtos:\n\n"
                f"{text[:8000]}"  # proteção de contexto
            )

            request = LLMRequest(
                system="Você é um assistente que resume documentos.",
                user=prompt
            )

            response = llm.generate(request)
            if response and response.text:
                return response.text.strip()

        except Exception:
            pass  # cai pro fallback

    # === FALLBACK DETERMINÍSTICO ===
    return _deterministic_summary(text, max_lines)