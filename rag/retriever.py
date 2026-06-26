"""
rag/retriever.py
-----------------
Indexa documentos y recupera patrones relevantes de ChromaDB.

Flujo de indexación:
    Documento Markdown → chunks → embeddings → ChromaDB

Flujo de recuperación:
    Query texto → embedding → búsqueda similitud coseno → top K chunks

Por qué K=3:
    Suficiente contexto para el dictaminador sin saturar el prompt.
    Más chunks = más contexto pero también más tokens y más latencia.
"""

from rag.store import get_or_create_collection, collection_is_empty
from rag.embedder import get_embeddings
from document_intelligence.chunker import chunk_text
from pathlib import Path
import uuid


PATRONES_PATH = Path("data/synthetic/patrones_fraude.md")
TOP_K = 3


def index_patrones():
    """
    Indexa el archivo de patrones de fraude en ChromaDB.
    Solo indexa si la colección está vacía — evita duplicados.
    """
    if not collection_is_empty():
        print("✅ RAG: colección ya indexada, saltando")
        return

    print("📚 RAG: indexando patrones de fraude...")

    text = PATRONES_PATH.read_text(encoding="utf-8")
    chunks = chunk_text(text, source="patrones_fraude.md")

    if not chunks:
        raise ValueError("No se generaron chunks del archivo de patrones")

    embeddings_model = get_embeddings()
    collection = get_or_create_collection()

    texts = [c["text"] for c in chunks]
    embeddings = embeddings_model.embed_documents(texts)
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks]

    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )

    print(f"✅ RAG: {len(chunks)} chunks indexados en ChromaDB")


def retrieve_patrones(query: str) -> str:
    """
    Recupera patrones de fraude relevantes para una query.

    Args:
        query: descripción del siniestro o señales de alerta

    Returns:
        str: patrones relevantes concatenados como contexto
    """
    # Asegurar que la colección esté indexada
    index_patrones()

    embeddings_model = get_embeddings()
    query_embedding = embeddings_model.embed_query(query)

    collection = get_or_create_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(TOP_K, collection.count())
    )

    if not results["documents"] or not results["documents"][0]:
        return "No se encontraron patrones relevantes."

    patrones = results["documents"][0]
    return "\n\n---\n\n".join(patrones)