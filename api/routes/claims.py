"""
api/routes/claims.py
---------------------
Endpoint principal — análisis de siniestros con caché Redis.

Flujo con caché:
    1. Recibe texto del siniestro
    2. Busca en Redis — si existe retorna instantáneo
    3. Si no existe, llama al agente LangGraph
    4. Guarda resultado en Redis con TTL 24h
    5. Retorna resultado

Por qué 200 y no 304 para cache hits:
    El cliente no necesita saber si vino de caché o del agente.
    Lo importante es que el resultado es correcto.
    Transparencia total para el consumidor de la API.
"""

from fastapi import APIRouter, HTTPException
from api.schemas import ClaimRequest, ClaimResponse, FraudResult
from api.cache import get_cached_result, set_cached_result
from agent.graph import analyze_claim
import time

router = APIRouter()


@router.post("/analyze-claim", response_model=ClaimResponse)
def analyze_claim_endpoint(request: ClaimRequest) -> ClaimResponse:
    """
    Analiza un reporte de siniestro y retorna dictamen de fraude.

    Flujo:
        1. Busca en caché Redis
        2. Si hay hit: retorna resultado instantáneo
        3. Si hay miss: llama al agente LangGraph
        4. Guarda en caché y retorna

    Args:
        request: ClaimRequest con texto del siniestro

    Returns:
        ClaimResponse con análisis completo

    Raises:
        HTTPException 500: si el agente falla completamente
    """
    start_time = time.time()

    # Intentar caché primero
    cached = get_cached_result(request.texto)
    if cached:
        elapsed = round(time.time() - start_time, 3)
        print(f"⚡ Respuesta desde caché en {elapsed}s")
        return ClaimResponse(**cached)

    # Cache miss — llamar al agente
    try:
        result = analyze_claim(request.texto)

        if result.get("error"):
            response = ClaimResponse(
                numero_poliza=request.numero_poliza,
                fraud_result=None,
                dictamen=result.get("dictamen"),
                entidades=None,
                error=result["error"],
                status="error"
            )
        else:
            fraud_result = FraudResult(**result["fraud_result"])
            response = ClaimResponse(
                numero_poliza=request.numero_poliza,
                fraud_result=fraud_result,
                dictamen=result["dictamen"],
                entidades=result["entidades"],
                error=None,
                status="success"
            )

        # Guardar en caché solo si fue exitoso
        if response.status == "success":
            set_cached_result(request.texto, response.model_dump())

        elapsed = round(time.time() - start_time, 2)
        print(f"✅ Análisis completado en {elapsed}s")

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado en el agente: {str(e)}"
        )