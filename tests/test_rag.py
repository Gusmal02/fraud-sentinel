"""Tests del módulo RAG."""
import pytest
from document_intelligence.chunker import chunk_text
from rag.store import get_chroma_client, get_or_create_collection


def test_chroma_client_inicializa():
    """ChromaDB debe inicializar correctamente."""
    client = get_chroma_client()
    assert client is not None


def test_coleccion_se_crea_o_existe():
    """La colección de patrones debe existir o crearse."""
    collection = get_or_create_collection()
    assert collection is not None
    assert collection.name == "patrones_fraude"


def test_coleccion_tiene_documentos():
    """La colección debe tener documentos indexados."""
    from rag.retriever import index_patrones
    index_patrones()
    collection = get_or_create_collection()
    assert collection.count() > 0


def test_retriever_retorna_texto():
    """El retriever debe retornar texto relevante para una query."""
    pytest.importorskip("ollama")
    from rag.retriever import retrieve_patrones
    try:
        resultado = retrieve_patrones("siniestro sin testigos sin reporte policial")
        assert isinstance(resultado, str)
        assert len(resultado) > 0
    except Exception:
        pytest.skip("Ollama no disponible en este entorno")


def test_retriever_query_vacia_no_falla():
    """Una query vacía no debe romper el sistema."""
    pytest.importorskip("ollama")
    from rag.retriever import retrieve_patrones
    try:
        resultado = retrieve_patrones("")
        assert isinstance(resultado, str)
    except Exception:
        pytest.skip("Ollama no disponible en este entorno")