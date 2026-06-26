# 🛡️ Fraud Sentinel

Sistema de detección de fraude en siniestros de seguros construido para aseguradoras

## ¿Qué resuelve?

Las aseguradoras procesan miles de siniestros mensuales. Fraud Sentinel analiza cada reporte
automáticamente y genera un dictamen de riesgo antes de que llegue al ajustador humano,
reduciendo el tiempo de revisión y el costo por fraude no detectado.

## Arquitectura

Documento (PDF/imagen/texto)

↓

Document Intelligence Pipeline (PyMuPDF + Tesseract)

↓

Agente LangGraph

├── Extractor    (LLM → 29 entidades estructuradas)

├── Scorer       (LightGBM → fraud score 0-1)

└── Dictator     (LLM + RAG → dictamen en español)

↑

ChromaDB (patrones históricos de fraude)

↓

FastAPI → respuesta JSON con dictamen auditable

## Stack

| Capa | Tecnología |
|------|-----------|
| Agente | LangGraph |
| LLM | Ollama local / Gemini API (switch por .env) |
| Clasificador | LightGBM (AUC 0.81, Recall 0.69) |
| Documentos | PyMuPDF + Tesseract OCR español |
| RAG | ChromaDB + nomic-embed-text |
| API | FastAPI + Pydantic |
| Observabilidad | Prometheus + Grafana |
| ML Tracking | MLflow |
| Seguridad | Bandit SAST + usuario no-root en Docker |
| Contenedores | Docker Compose |
| CI/CD | GitHub Actions |
| Cloud (documentado) | AWS ECS + Terraform |

## Levantar en local

```bash
git clone https://github.com/Gusmal02/fraud-sentinel
cd fraud-sentinel
cp .env.example .env
docker compose up
```

API disponible en `http://localhost:8000/docs`

## Servicios del stack

| Servicio | URL | Descripción |
|----------|-----|-------------|
| API | http://localhost:8000/docs | Fraud Sentinel API |
| Grafana | http://localhost:3000 | Dashboards (admin/admin) |
| MLflow | http://localhost:5000 | Tracking de experimentos |
| ChromaDB | http://localhost:8001 | Vector store |
| Prometheus | http://localhost:9090 | Métricas |

## Cambiar a Gemini API

```bash
# En .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=tu_api_key
```

## Etapas del proyecto

**Etapa 1 — MVP ✅**
- Document Intelligence Pipeline (PDF digital + OCR)
- Clasificador LightGBM entrenado con SMOTE
- Agente LangGraph con 3 nodos
- FastAPI con documentación automática

**Etapa 2 — Observable ✅**
- RAG con ChromaDB y patrones de fraude históricos
- Prometheus + Grafana para métricas en tiempo real
- MLflow para tracking de experimentos

**Etapa 3 — Cloud ready ✅**
- Terraform documentado para AWS ECS
- GitHub Actions CI/CD automático
- Bandit SAST en cada commit

## Tests

```bash
uv run pytest tests/ -v
```

8 tests passing — API, document intelligence y clasificador.

## Seguridad

- Usuario no-root en Dockerfile
- Bandit SAST en pipeline CI/CD — 0 issues High/Medium
- Variables sensibles en .env (nunca en código)
- pickle.load con nosec B301 documentado — modelos internos únicamente