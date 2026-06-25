# Documentación Técnica — Fraud Sentinel

## Arquitectura del sistema

### Flujo completo

Entrada (PDF / imagen / texto)

↓

document_intelligence/

├── detector.py      → detecta tipo de archivo

├── pdf_extractor.py → PDF digital → Markdown

├── ocr_extractor.py → imagen/PDF escaneado → Markdown via Tesseract

└── chunker.py       → divide en chunks para RAG

↓

agent/graph.py (LangGraph)

├── extractor_node   → LLM extrae 29 entidades estructuradas

├── scorer_node      → LightGBM genera fraud score 0-1

└── dictator_node    → LLM redacta dictamen en español

↓

api/main.py (FastAPI)

├── POST /analyze-claim  → análisis completo

├── GET  /health         → estado del sistema

└── GET  /metrics        → métricas Prometheus

## Decisiones técnicas

### ¿Por qué LightGBM y no una red neuronal?
Los siniestros tienen datos tabulares estructurados — edad, marca, área, historial.
LightGBM es superior a redes neuronales para datos tabulares: más rápido de entrenar,
más interpretable y produce feature importance directamente explotable por el agente.

### ¿Por qué SMOTE?
El dataset tiene 94% legítimos vs 6% fraude. Sin balanceo el modelo aprende a decir
"todo es legítimo" con 94% accuracy pero 0% de detección de fraude. SMOTE genera
casos sintéticos de fraude solo en el training set para evitar data leakage.

### ¿Por qué umbral 0.3 y no 0.5?
En detección de fraude el costo de un falso negativo (dejar pasar fraude) es mayor
que el de un falso positivo (investigar un caso legítimo). Bajar el umbral prioriza
recall sobre precision — decisión de negocio, no técnica.

### ¿Por qué LangGraph y no una función secuencial?
LangGraph permite estado compartido tipado entre nodos, fácil extensión con flujos
condicionales y compatibilidad con LangSmith para observabilidad en producción.

### ¿Por qué Ollama con fallback a Gemini?
Privacidad y costo en desarrollo — los documentos de siniestros contienen datos
sensibles. En producción se migra a Gemini API con una variable de entorno.

### ¿Por qué PyMuPDF + Tesseract?
PyMuPDF es la librería más rápida para extracción de texto en PDFs digitales.
Tesseract con idioma español (`-l spa`) maneja documentos mexicanos con acentos
y vocabulario específico de seguros.

## Métricas del modelo

| Métrica | Valor |
|---------|-------|
| ROC-AUC | 0.8087 |
| Recall fraude | 0.6919 |
| Precision fraude | 0.1445 |
| F1 fraude | 0.2390 |
| Dataset | 15,420 siniestros |
| Fraude real | 6.0% |

## Variables más importantes para detección de fraude

Según feature importance del modelo LightGBM:

1. **Make** — marca del vehículo
2. **Age** — edad del asegurado
3. **AgeOfVehicle** — antigüedad del vehículo
4. **DayOfWeekClaimed** — día del reclamo
5. **BasePolicy** — tipo base de póliza

## Estructura de carpetas

fraud-sentinel/

├── agent/              # Agente LangGraph

├── api/                # FastAPI

├── classifier/         # LightGBM

├── document_intelligence/  # PDF/OCR pipeline

├── llm/                # Cliente LLM unificado

├── rag/                # ChromaDB (Etapa 2)

├── infrastructure/     # Terraform AWS

├── observability/      # Prometheus + Grafana

├── tests/              # pytest

└── data/synthetic/     # Siniestros de prueba

## Cómo levantar el sistema

### Local sin Docker
```bash
# Instalar dependencias
uv sync

# Entrenar modelo
uv run python -m classifier.train

# Levantar API
uv run uvicorn api.main:app --reload --port 8000
```

### Con Docker Compose
```bash
cp .env.example .env
docker compose up
```

### Cambiar a Gemini API
```bash
# En .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=tu_api_key
```

## Seguridad

- Usuario no-root en Dockerfile
- Bandit SAST en pipeline CI/CD
- Variables sensibles en .env (nunca en código)
- `.dockerignore` excluye modelos y datos del build
- `pickle.load` suprimido con `# nosec B301` — modelos generados internamente

## Cómo levantar el sistema

### Local sin Docker
```bash
# Instalar dependencias
uv sync

# Entrenar modelo
uv run python -m classifier.train

# Levantar API
uv run uvicorn api.main:app --reload --port 8000
```

### Con Docker Compose
```bash
cp .env.example .env
docker compose up
```

### Cambiar a Gemini API
```bash
# En .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=tu_api_key
```

## Seguridad

- Usuario no-root en Dockerfile
- Bandit SAST en pipeline CI/CD
- Variables sensibles en .env (nunca en código)
- `.dockerignore` excluye modelos y datos del build
- `pickle.load` suprimido con `# nosec B301` — modelos generados internamente

