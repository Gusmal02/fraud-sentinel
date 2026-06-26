Ambas cosas van juntas — el DEMO.md es tu guión de presentación y los comandos de inicialización en orden correcto.
Crea DEMO.md en la raíz:
markdown# 🎬 Guión de Demo — Fraud Sentinel

## Antes de la demo (preparación previa)

```bash
# 1. Asegurarse que Ollama está corriendo
ollama serve

# 2. Verificar modelos disponibles
ollama list

# 3. Levantar el stack completo
docker compose up

# 4. Verificar que todo está sano
curl http://localhost:8000/health
```

---

## Orden de presentación recomendado

### Paso 1 — El problema (30 segundos)
> "Una aseguradora procesa miles de siniestros al mes. 
> Revisarlos manualmente es lento y caro. 
> Fraud Sentinel analiza cada reporte automáticamente 
> y genera un dictamen antes de que llegue al ajustador."

### Paso 2 — La arquitectura (1 minuto)
Mostrar `README.md` en GitHub — señalar el diagrama de flujo:
Documento → Document Intelligence → Agente LangGraph → FastAPI

├── Extractor

├── Scorer (LightGBM)

└── Dictator + RAG

### Paso 3 — Demo en vivo (3 minutos)

**Abrir:** `http://localhost:8000/docs`

**Caso 1 — Siniestro sospechoso (score ALTO esperado):**
```json
{
  "texto": "REPORTE DE SINIESTRO. Poliza AUTO-2026-009981. Asegurado Roberto Fuentes. Vehiculo BMW Serie 3 2019. Robo total reportado a las 03:00 horas en zona despoblada. Monto reclamado 380000 pesos. Sin reporte policial. Sin testigos. Tercer siniestro en 2 anos. Agente externo. Cambio de domicilio hace 3 meses. Poliza con 20 dias de vigencia.",
  "numero_poliza": "AUTO-2026-009981"
}
```

**Caso 2 — Siniestro limpio (score BAJO esperado):**
```json
{
  "texto": "REPORTE DE SINIESTRO. Poliza AUTO-2026-001234. Asegurado Maria Garcia Lopez. Vehiculo Nissan Sentra 2022. Colision menor en estacionamiento el dia 10 de junio a las 14:00 horas. Monto reclamado 8500 pesos. Reporte policial presentado. Dos testigos presentes. Primer siniestro. Sin cambio de domicilio. Agente interno.",
  "numero_poliza": "AUTO-2026-001234"
}
```

**Señalar en la respuesta:**
- `fraud_score` — probabilidad 0 a 1
- `risk_level` — BAJO / MEDIO / ALTO
- `dictamen` — texto auditable en español
- `top_risk_factors` — factores que influyeron

### Paso 4 — Segunda llamada con caché (30 segundos)
Enviar el mismo siniestro del Caso 1 de nuevo.
Mostrar que la respuesta es instantánea — Redis caché funcionando.

### Paso 5 — Observabilidad (1 minuto)
Abrir `http://localhost:3000` — Grafana
- Mostrar métricas de requests
- Señalar latencia p95

Abrir `http://localhost:5000` — MLflow
- Mostrar experimento fraud-sentinel
- Señalar métricas del modelo: AUC 0.8087, Recall 0.69

### Paso 6 — Código (2 minutos)
Abrir VSCode — mostrar estructura de carpetas:
- `agent/graph.py` — el grafo LangGraph
- `classifier/train.py` — entrenamiento con SMOTE
- `llm/client.py` — switch Ollama/Gemini
- `docker-compose.yml` — stack completo

### Paso 7 — GitHub Actions (30 segundos)
Abrir `github.com/Gusmal02/fraud-sentinel` → pestaña Actions
- Mostrar CI verde
- Señalar Bandit + pytest en cada commit

---

## Preguntas frecuentes en demo técnica

**¿Por qué tarda en responder?**
> "Estoy usando Ollama local en CPU. En producción con Gemini API 
> la respuesta baja de 3 minutos a 3-5 segundos. 
> La arquitectura ya está preparada — es una variable de entorno."

**¿Por qué el score salió BAJO si hay señales de alerta?**
> "El texto libre no siempre contiene todos los campos estructurados 
> que el clasificador necesita. El LLM retorna 'unknown' en campos 
> que no encuentra y eso baja el score. En producción complementamos 
> con formularios estructurados."

**¿Cómo escalarías esto?**
> "Terraform ya está documentado para AWS ECS. 
> El contenedor Docker está listo. 
> Solo necesito conectar el CD al pipeline de CI."

**¿Qué mejorarías primero?**
> "Tres cosas: Gemini API para latencia, 
> formularios estructurados para mejor extracción, 
> y reentrenamiento con datos reales del sector."

---

## URLs de referencia rápida

| Servicio | URL |
|----------|-----|
| API docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |
| Métricas | http://localhost:8000/metrics |
| Grafana | http://localhost:3000 |
| MLflow | http://localhost:5000 |
| GitHub | https://github.com/Gusmal02/fraud-sentinel |