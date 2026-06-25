"""
api/routes/health.py
---------------------
Endpoint de salud del sistema.

Por qué un endpoint de salud:
    En producción, los sistemas de monitoreo (AWS ECS, Kubernetes)
    necesitan saber si el servicio está vivo y funcionando.
    Si /health no responde, el orquestador reinicia el contenedor.

Por qué verificamos Ollama y el modelo:
    El servicio puede estar arriba pero el LLM caído.
    Un health check real verifica todas las dependencias críticas,
    no solo que FastAPI esté corriendo.
"""

from fastapi import APIRouter
from llm.client import get_provider_name
from classifier.predict import _load_model
from pathlib import Path

router = APIRouter()


@router.get("/health")
def health_check():
    """
    Verifica el estado de todos los componentes del sistema.

    Returns:
        dict con status de cada componente
    """
    checks = {}

    # Verificar modelo LightGBM
    try:
        _load_model()
        checks["classifier"] = "ok"
    except Exception as e:
        checks["classifier"] = f"error: {e}"

    # Verificar que existen los archivos críticos
    checks["model_file"] = "ok" if Path("classifier/model/fraud_model.pkl").exists() else "missing"
    checks["encoders_file"] = "ok" if Path("classifier/model/encoders.pkl").exists() else "missing"

    # Proveedor LLM activo
    checks["llm_provider"] = get_provider_name()

    # Status general
    all_ok = all(v == "ok" for k, v in checks.items() if k != "llm_provider")
    status = "healthy" if all_ok else "degraded"

    return {
        "status": status,
        "checks": checks,
        "version": "0.1.0"
    }
    