"""
rag/store.py
-------------
Cliente ChromaDB para almacenar y recuperar embeddings.

Por qué ChromaDB:
    Vector store ligero que corre localmente sin infraestructura
    adicional. Persiste en disco — los embeddings sobreviven
    reinicios del sistema. En producción se migra a pgvector
    en AWS RDS o a Vertex AI Vector Search en GCP.

Por qué una colección separada para patrones de fraude:
    Separar colecciones permite búsquedas más precisas.
    En Etapa 3 podríamos tener colecciones por tipo de siniestro
    (auto, médico, vida) con patrones específicos para cada uno.
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path

# Directorio de persistencia local
CHROMA_PATH = Path("data/chromadb")
COLLECTION_NAME = "patrones_fraude"


def get_chroma_client():
    """
    Retorna cliente ChromaDB con persistencia en disco.
    """
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_PATH))


def get_or_create_collection():
    """
    Obtiene o crea la colección de patrones de fraude.

    Returns:
        chromadb.Collection: colección lista para usar
    """
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # Distancia coseno para texto
    )


def collection_is_empty() -> bool:
    """Verifica si la colección tiene documentos indexados."""
    collection = get_or_create_collection()
    return collection.count() == 0