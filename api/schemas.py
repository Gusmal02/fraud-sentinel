"""
api/schemas.py
--------------
Define los modelos de entrada y salida de la API con Pydantic.

Por qué Pydantic:
    Valida automáticamente que los datos que llegan a la API
    tengan el formato correcto antes de procesarlos.
    Si falta un campo requerido o el tipo es incorrecto,
    FastAPI retorna un error 422 claro antes de tocar el agente.

Por qué esto importa en producción:
    Sin validación, un campo mal formado podría llegar hasta
    el clasificador y causar un error difícil de debuggear.
    Con Pydantic, el error se detecta en la puerta de entrada.
"""

from pydantic import BaseModel, Field
from typing import Optional


class ClaimRequest(BaseModel):
    """
    Entrada de la API — texto del siniestro a analizar.
    Acepta texto plano o Markdown.
    """
    texto: str = Field(
        ...,
        min_length=50,
        description="Texto del reporte de siniestro en español"
    )
    numero_poliza: Optional[str] = Field(
        None,
        description="Número de póliza para referencia (opcional)"
    )


class FraudResult(BaseModel):
    """Score del clasificador LightGBM."""
    fraud_score: float
    is_fraud: bool
    risk_level: str
    top_risk_factors: list
    threshold_used: float


class ClaimResponse(BaseModel):
    """
    Respuesta completa del análisis de siniestro.
    """
    numero_poliza: Optional[str]
    fraud_result: Optional[FraudResult]
    dictamen: Optional[str]
    entidades: Optional[dict]
    error: Optional[str]
    status: str  # "success" o "error"