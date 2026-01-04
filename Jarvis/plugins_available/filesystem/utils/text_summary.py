import re

MAX_SUMMARY_CHARS = 1200
MIN_TEXT_LENGTH = 80


def _clean_text(text: str) -> str:
    """
    Limpa o texto removendo espaços excessivos e lixo comum.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def summarize_text(text: str) -> str | None:
    """
    Gera um resumo determinístico e seguro de um texto grande.
    NÃO usa LLM.
    """

    if not text:
        return None

    text = _clean_text(text)

    if len(text) < MIN_TEXT_LENGTH:
        return None

    # Texto pequeno → retorna direto
    if len(text) <= MAX_SUMMARY_CHARS:
        return text

    # Texto grande → resumo simples
    head = text[:MAX_SUMMARY_CHARS]

    # tenta cortar em um ponto final para não quebrar frase
    last_dot = head.rfind(".")
    if last_dot > 200:
        head = head[: last_dot + 1]

    return head + "\n\n[...]"