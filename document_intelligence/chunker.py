"""
document_intelligence/chunker.py
----------------------------------
Divide el texto extraído en chunks para indexar en ChromaDB.

Por qué chunking y no indexar el documento completo:
    Un LLM tiene límite de contexto. Si metes 50 páginas de un
    siniestro en un solo prompt, el modelo se pierde o falla.
    El chunking divide el documento en fragmentos manejables
    y el RAG solo recupera los fragmentos relevantes para
    la pregunta específica.

Estrategia de chunking:
    Chunk size: 500 caracteres
    Overlap: 50 caracteres

    El overlap es crítico — si una oración importante cae
    exactamente en el límite entre dos chunks, el overlap
    garantiza que aparezca completa en al menos uno de ellos.
"""

from typing import List


# Tamaño de cada chunk en caracteres
CHUNK_SIZE = 500

# Cuántos caracteres se repiten entre chunks consecutivos
CHUNK_OVERLAP = 50


def chunk_text(text: str, source: str = "documento") -> List[dict]:
    """
    Divide texto en chunks con overlap y metadata.

    Args:
        text: texto completo extraído del documento
        source: nombre del documento origen — se guarda en metadata
                para que el RAG pueda citar de dónde vino la info

    Returns:
        List[dict]: lista de chunks con esta estructura:
            {
                "text": str,        # contenido del chunk
                "source": str,      # nombre del documento
                "chunk_index": int, # posición del chunk en el documento
                "total_chunks": int # total de chunks del documento
            }
    """
    if not text or not text.strip():
        return []

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = start + CHUNK_SIZE

        # Si no es el último chunk, busca un punto de corte natural
        # (espacio o salto de línea) para no cortar palabras a la mitad
        if end < len(text):
            # Busca el último espacio antes del límite
            natural_break = text.rfind(" ", start, end)
            if natural_break > start:
                end = natural_break

        chunk_text_content = text[start:end].strip()

        if chunk_text_content:
            chunks.append({
                "text": chunk_text_content,
                "source": source,
                "chunk_index": chunk_index,
                "total_chunks": 0,  # Se actualiza al final
            })
            chunk_index += 1

        # Avanza con overlap — retrocede CHUNK_OVERLAP caracteres
        start = end - CHUNK_OVERLAP

    # Actualizar total_chunks ahora que sabemos cuántos hay
    total = len(chunks)
    for chunk in chunks:
        chunk["total_chunks"] = total

    return chunks


def chunk_document(file_path: str, extracted_text: str) -> List[dict]:
    """
    Wrapper conveniente que recibe la ruta del archivo y el texto
    ya extraído, y retorna chunks listos para indexar en ChromaDB.

    Args:
        file_path: ruta original del documento (para metadata)
        extracted_text: texto ya extraído por pdf_extractor u ocr_extractor

    Returns:
        List[dict]: chunks listos para ChromaDB
    """
    from pathlib import Path
    source = Path(file_path).name
    return chunk_text(extracted_text, source=source)