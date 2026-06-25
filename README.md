# 🛡️ Fraud Sentinel

Sistema de detección de fraude en siniestros de seguros construido para Inter.mx.

## ¿Qué resuelve?

Inter.mx procesa miles de siniestros mensuales. Fraud Sentinel analiza cada reporte
automáticamente y genera un dictamen de riesgo antes de que llegue al ajustador humano,
reduciendo el tiempo de revisión y el costo por fraude no detectado.

## Arquitectura

Documento (PDF/imagen/texto)

↓

Document Intelligence Pipeline (PyMuPDF + Tesseract)

↓

Agente LangGraph

├── Extractor (LLM → entidades estructuradas)

├── Scorer (LightGBM → fraud score)

└── Dictator (LLM → dictamen en español)

↓

FastAPI → respuesta JSON con dictamen auditable

## Stack

| Capa | Tecnología |
|------|-----------|
| Agente | LangGraph |
| LLM | Ollama / Gemini API |
| Clasificador | LightGBM (AUC 0.81) |
| Documentos | PyMuPDF + Tesseract OCR |
| API | FastAPI |
| Observabilidad | Prometheus + Grafana |
| ML Tracking | MLflow |
| Contenedores | Docker Compose |
| Cloud (documentado) | AWS ECS + Terraform |

## Levantar en local

```bash
git clone https://github.com/Gusmal02/fraud-sentinel
cd fraud-sentinel
cp .env.example .env
docker compose up
```

API disponible en `http://localhost:8000/docs`

## Etapas del proyecto

**Etapa 1 — MVP ✅**
- Document Intelligence Pipeline
- Clasificador LightGBM entrenado
- Agente LangGraph con 3 nodos
- FastAPI con documentación automática

**Etapa 2 — Observable**
- RAG con ChromaDB
- Prometheus + Grafana
- MLflow tracking

**Etapa 3 — Cloud ready**
- Terraform para AWS ECS
- GitHub Actions CI/CD
- Bandit security scanning