"""
document_intelligence/detector.py
----------------------------------
Detecta el tipo de documento entrante y decide
qué extractor usar para convertirlo a texto plano.

Tipos soportados:
    - PDF con texto digital  → pdf_extractor
    - PDF escaneado          → ocr_extractor
    - Imagen (jpg, png)      → ocr_extractor
    - Texto plano            → pasa directo

Por qué esta capa existe:
    El agente nunca debe saber qué tipo de archivo recibió.
    Solo recibe Markdown limpio y trabaja sobre eso.
"""

import os
from pathlib import Path
from enum import Enum


class DocumentType(Enum):
    PDF_DIGITAL = "pdf_digital"    # PDF con texto seleccionable
    PDF_SCANNED = "pdf_scanned"    # PDF que es en realidad una imagen escaneada
    IMAGE = "image"                # JPG, PNG, etc.
    TEXT = "text"                  # Texto plano, ya no necesita conversión


def detect_document_type(file_path: str) -> DocumentType:
    """
    Detecta el tipo de documento basándose en extensión y contenido.

    Para PDFs hace una detección inteligente:
    si el PDF no tiene texto extraíble, asume que es escaneado
    y necesita OCR.

    Args:
        file_path: ruta al archivo

    Returns:
        DocumentType: tipo detectado
    
    Raises:
        FileNotFoundError: si el archivo no existe
        ValueError: si el formato no está soportado
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    extension = path.suffix.lower()

    # Texto plano — pasa directo sin conversión
    if extension in [".txt", ".md"]:
        return DocumentType.TEXT

    # Imágenes — siempre OCR
    if extension in [".jpg", ".jpeg", ".png", ".tiff", ".bmp"]:
        return DocumentType.IMAGE

    # PDF — necesita inspección para saber si tiene texto
    if extension == ".pdf":
        return _detect_pdf_type(file_path)

    raise ValueError(
        f"Formato '{extension}' no soportado. "
        "Formatos válidos: pdf, jpg, jpeg, png, tiff, bmp, txt, md"
    )


def _detect_pdf_type(file_path: str) -> DocumentType:
    """
    Inspecciona el PDF para determinar si tiene texto digital
    o si es una imagen escaneada.

    Estrategia: extrae texto de la primera página.
    Si hay menos de 50 caracteres, asumimos que es escaneado.

    Args:
        file_path: ruta al PDF

    Returns:
        DocumentType.PDF_DIGITAL o DocumentType.PDF_SCANNED
    """
    import fitz  # PyMuPDF

    MIN_CHARS_FOR_DIGITAL = 50

    with fitz.open(file_path) as doc:
        first_page = doc[0]
        text = first_page.get_text().strip()

    if len(text) >= MIN_CHARS_FOR_DIGITAL:
        return DocumentType.PDF_DIGITAL
    else:
        return DocumentType.PDF_SCANNED