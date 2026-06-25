"""Tests del pipeline de documentos."""
import pytest
from document_intelligence.chunker import chunk_text


def test_chunk_text_basic():
    texto = "a" * 1000
    chunks = chunk_text(texto, source="test.pdf")
    assert len(chunks) > 1


def test_chunk_metadata():
    chunks = chunk_text("Texto de prueba para el siniestro " * 20, source="prueba.pdf")
    assert chunks[0]["source"] == "prueba.pdf"
    assert chunks[0]["chunk_index"] == 0
    assert chunks[0]["total_chunks"] == len(chunks)


def test_empty_text_returns_empty_list():
    chunks = chunk_text("")
    assert chunks == []


def test_chunk_size_respected():
    texto = "x " * 500
    chunks = chunk_text(texto)
    for chunk in chunks:
        assert len(chunk["text"]) <= 550  # tamaño + margen