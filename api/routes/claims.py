"""
api/routes/claims.py
---------------------
Endpoint principal — análisis de siniestros.

Por qué POST y no GET:
    GET es para obtener recursos. POST es para enviar datos
    que serán procesados. Aquí enviamos texto para analizar,
    no pedimos un recurso existente.

Por qué HTTPException y no dejar que el error suba solo:
    Si el agente falla sin control, FastAPI retorna un 500
    genérico sin información útil. Con HTTPException podemos
    retornar mensajes claros que el cliente pueda manejar.
"""

from fastapi import APIRouter, HTTPException
from api.schemas import ClaimRequest, ClaimResponse, FraudResult
from agent.graph import analyze_claim
import time

router = APIRouter()


@router.post("/analyze-claim", response_model=ClaimResponse)
def analyze_claim_endpoint(request: ClaimRequest) -> ClaimResponse:
    """
    Analiza un reporte de siniestro y retorna dictamen de fraude.

    Flujo:
        1. Recibe texto del siniestro
        2. Pasa al agente LangGraph
        3. Retorna score, entidades y dictamen

    Args:
        request: ClaimRequest con texto del siniestro

    Returns:
        ClaimResponse con análisis completo

    Raises:
        HTTPException 500: si el agente falla completamente
    """
    start_time = time.time()

    try:
        result = analyze_claim(request.texto)

        # Si hubo error en el agente, retornamos 200 con error en el body
        # No es un 500 porque el servicio funcionó — el documento fue el problema
        if result.get("error"):
            return ClaimResponse(
                numero_poliza=request.numero_poliza,
                fraud_result=None,
                dictamen=result.get("dictamen"),
                entidades=None,
                error=result["error"],
                status="error"
            )

        fraud_result = FraudResult(**result["fraud_result"])

        elapsed = round(time.time() - start_time, 2)
        print(f"✅ Análisis completado en {elapsed}s")

        return ClaimResponse(
            numero_poliza=request.numero_poliza,
            fraud_result=fraud_result,
            dictamen=result["dictamen"],
            entidades=result["entidades"],
            error=None,
            status="success"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado en el agente: {str(e)}"
        )