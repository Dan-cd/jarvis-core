from pathlib import Path

from pdf2image import convert_from_path
import pytesseract


def extract_text_with_ocr(
    pdf_path: Path,
    max_pages: int = 5,
    dpi: int = 200
) -> str:
    """
    Converte páginas do PDF em imagens e aplica OCR.
    Usado como fallback quando PyPDF2 falha.

    - max_pages: limite para evitar PDFs gigantes
    - dpi: equilíbrio entre qualidade e performance
    """

    images = convert_from_path(
        pdf_path,
        dpi=dpi,
        first_page=1,
        last_page=max_pages
    )

    texts = []

    for img in images:
        text = pytesseract.image_to_string(img, lang="por")
        if text:
            texts.append(text.strip())

    return "\n\n".join(texts).strip()