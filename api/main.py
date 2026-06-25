"""
api/main.py
------------
Punto de entrada de la API FastAPI.

Por qué FastAPI y no Flask:
    FastAPI genera documentación automática en /docs,
    valida tipos con Pydantic, soporta async nativamente
    y es significativamente más rápido que Flask.
    Para APIs de ML es el estándar actual.

Por qué Prometheus instrumentator:
    Cada request genera métricas automáticas:
    latencia, requests por segundo, errores por endpoint.
    Grafana las visualiza sin que nosotros escribamos
    ni una línea extra de código de métricas.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from api.routes import health, claims

app = FastAPI(
    title="Fraud Sentinel",
    description="Sistema de detección de fraude en siniestros para Inter.mx",
    version="0.1.0",
)

# CORS — permite que frontends externos consuman la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus — expone métricas en /metrics automáticamente
Instrumentator().instrument(app).expose(app)

# Rutas
app.include_router(health.router, tags=["Sistema"])
app.include_router(claims.router, tags=["Siniestros"])


@app.get("/", tags=["Sistema"])
def root():
    return {
        "sistema": "Fraud Sentinel",
        "version": "0.1.0",
        "descripcion": "Detección de fraude en siniestros — Inter.mx",
        "docs": "/docs",
        "health": "/health",
    }