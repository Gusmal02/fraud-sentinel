"""
document_intelligence/ocr_extractor.py
---------------------------------------
Extrae texto de imágenes y PDFs escaneados usando OCR.

Por qué Tesseract:
    Es el motor OCR open-source más maduro y preciso.
    Soporta español de forma nativa, lo cual es crítico
    para documentos de siniestros de una aseguradora mexicana.

Flujo para PDFs escaneados:
    PDF → cada página se convierte en imagen → Tesseract lee la imagen
    → texto plano → Markdown

Por qué convertimos PDF a imagen primero:
    Tesseract no lee PDFs directamente. PyMuPDF renderiza cada
    página como imagen en memoria sin guardar archivos temporales.
"""

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from pathlib import Path


# Configuración de Tesseract para español
TESSERACT_CONFIG = "--oem 3 --psm 6 -l spa"

# Resolución de renderizado — más DPI = mejor OCR, más lento
RENDER_DPI = 300


def extract_image_to_markdown(file_path: str) -> str:
    """
    Extrae texto de una imagen (JPG, PNG, etc.) usando OCR.

    Args:
        file_path: ruta a la imagen

    Returns:
        str: texto extraído en formato Markdown

    Raises:
        FileNotFoundError: si el archivo no existe
        RuntimeError: si OCR falla o no extrae texto útil
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Imagen no encontrada: {file_path}")

    image = Image.open(file_path)
    text = pytesseract.image_to_string(image, config=TESSERACT_CONFIG).strip()

    if not text:
        raise RuntimeError(
            f"OCR no pudo extraer texto de {path.name}. "
            "Verifica que la imagen sea legible."
        )

    return f"## Documento: {path.name}\n\n{text}"


def extract_scanned_pdf_to_markdown(file_path: str) -> str:
    """
    Extrae texto de un PDF escaneado convirtiéndolo página
    por página a imagen y aplicando OCR.

    Args:
        file_path: ruta al PDF escaneado

    Returns:
        str: texto extraído en formato Markdown

    Raises:
        FileNotFoundError: si el archivo no existe
        RuntimeError: si ninguna página produce texto útil
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF no encontrado: {file_path}")

    markdown_pages = []

    with fitz.open(file_path) as doc:
        total_pages = len(doc)

        for page_num, page in enumerate(doc, start=1):
            # Renderizar página como imagen en memoria
            # Matrix(RENDER_DPI/72, RENDER_DPI/72) escala la resolución
            matrix = fitz.Matrix(RENDER_DPI / 72, RENDER_DPI / 72)
            pixmap = page.get_pixmap(matrix=matrix)

            # Convertir pixmap a PIL Image sin guardar en disco
            image_bytes = pixmap.tobytes("png")
            image = Image.open(io.BytesIO(image_bytes))

            # OCR sobre la imagen
            text = pytesseract.image_to_string(
                image, config=TESSERACT_CONFIG
            ).strip()

            if text:
                header = f"## Página {page_num} de {total_pages}\n"
                markdown_pages.append(header + text)

    if not markdown_pages:
        raise RuntimeError(
            "OCR no extrajo texto útil de ninguna página del PDF. "
            "Verifica que el documento sea legible."
        )

    return "\n\n---\n\n".join(markdown_pages)