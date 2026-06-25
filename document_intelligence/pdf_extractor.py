"""
document_intelligence/pdf_extractor.py
---------------------------------------
Extrae texto de PDFs digitales y lo convierte a Markdown limpio.

Por qué PyMuPDF (fitz):
    Es la librería más rápida y precisa para extracción de texto
    en PDFs. Preserva estructura de párrafos mejor que pdfplumber
    o PyPDF2, lo que produce Markdown más limpio para el LLM.

Por qué Markdown y no texto plano:
    El LLM procesa mejor documentos con estructura visible.
    Un encabezado en Markdown le dice al modelo "esto es importante"
    sin necesidad de instrucciones adicionales en el prompt.
"""

import fitz  # PyMuPDF
from pathlib import Path


def extract_pdf_to_markdown(file_path: str) -> str:
    """
    Extrae texto de un PDF digital y lo estructura en Markdown.

    Args:
        file_path: ruta al PDF

    Returns:
        str: contenido del PDF en formato Markdown

    Raises:
        FileNotFoundError: si el archivo no existe
        RuntimeError: si el PDF está corrupto o protegido
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF no encontrado: {file_path}")

    try:
        markdown_pages = []

        with fitz.open(file_path) as doc:
            total_pages = len(doc)

            for page_num, page in enumerate(doc, start=1):
                text = page.get_text().strip()

                if not text:
                    continue

                # Encabezado de página en Markdown
                page_header = f"## Página {page_num} de {total_pages}\n"
                markdown_pages.append(page_header + text)

        if not markdown_pages:
            raise RuntimeError(
                "El PDF no contiene texto extraíble. "
                "Considera usar el extractor OCR."
            )

        return "\n\n---\n\n".join(markdown_pages)

    except fitz.FileDataError as e:
        raise RuntimeError(f"PDF corrupto o protegido: {e}")


def get_pdf_metadata(file_path: str) -> dict:
    """
    Extrae metadata del PDF — útil para el agente cuando
    necesita fecha del documento, autor, etc.

    Args:
        file_path: ruta al PDF

    Returns:
        dict: metadata del PDF (título, autor, fecha, páginas)
    """
    with fitz.open(file_path) as doc:
        meta = doc.metadata
        return {
            "titulo": meta.get("title", "Sin título"),
            "autor": meta.get("author", "Desconocido"),
            "fecha": meta.get("creationDate", "Sin fecha"),
            "paginas": len(doc),
            "archivo": Path(file_path).name,
        }