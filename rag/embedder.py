"""
rag/embedder.py
----------------
Genera embeddings usando Ollama para indexar documentos en ChromaDB.

Por qué embeddings y no búsqueda por palabras clave:
    La búsqueda por palabras clave encuentra "robo" si el documento
    dice exactamente "robo". Los embeddings encuentran conceptos
    similares — "sustracción de vehículo" también aparece aunque
    no diga "robo". Para documentos de siniestros con lenguaje
    variable, la búsqueda semántica es superior.

Por qué Ollama para embeddings:
    Mismo proveedor que el LLM — sin dependencias adicionales.
    El modelo nomic-embed-text es ligero y preciso para español.
"""

from langchain_ollama import OllamaEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()


def get_embeddings():
    """
    Retorna el modelo de embeddings configurado.
    Usa nomic-embed-text — modelo especializado en embeddings,
    más eficiente que usar el LLM completo para esta tarea.
    """
    return OllamaEmbeddings(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model="nomic-embed-text"
    )