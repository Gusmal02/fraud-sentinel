"""
document_intelligence/
-----------------------
Pipeline completo de conversión de documentos a texto.

Uso desde otros módulos:
    from document_intelligence import process_document

    texto = process_document("siniestro.pdf")
    # Retorna Markdown limpio sin importar el tipo de archivo
"""

from .detector import detect_document_type, DocumentType
from .pdf_extractor import extract_pdf_to_markdown
from .ocr_extractor import extract_image_to_markdown, extract_scanned_pdf_to_markdown
from .chunker import chunk_document


def process_document(file_path: str) -> str:
    """
    Punto de entrada único del módulo.
    Detecta el tipo de documento y aplica el extractor correcto.

    Args:
        file_path: ruta al documento (PDF, imagen o texto)

    Returns:
        str: contenido completo en Markdown limpio
    """
    doc_type = detect_document_type(file_path)

    if doc_type == DocumentType.TEXT:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    elif doc_type == DocumentType.PDF_DIGITAL:
        return extract_pdf_to_markdown(file_path)

    elif doc_type == DocumentType.PDF_SCANNED:
        return extract_scanned_pdf_to_markdown(file_path)

    elif doc_type == DocumentType.IMAGE:
        return extract_image_to_markdown(file_path)