# Hallazgos y Aprendizajes — Fraud Sentinel

## Dataset — fraud_oracle.csv

**Fuente:** Kaggle - Vehicle Claim Fraud Detection  
**Registros:** 15,420 siniestros de seguros de auto  
**Variables:** 33 columnas  
**Periodo:** 1994-1996

### Distribución de fraude
| Clase | Registros | Porcentaje |
|-------|-----------|------------|
| Legítimo | 14,497 | 94.0% |
| Fraude | 923 | 6.0% |

### Hallazgo 1 — Dataset severamente desbalanceado
El 94% de los casos son legítimos. Un modelo naive que prediga siempre
"legítimo" tendría 94% de accuracy pero 0% de utilidad real.
**Solución aplicada:** SMOTE en el training set exclusivamente.

### Hallazgo 2 — Variables más predictivas de fraude
Según feature importance de LightGBM:
- Marca del vehículo (Make)
- Edad del asegurado (Age)
- Antigüedad del vehículo (AgeOfVehicle)
- Día del reclamo (DayOfWeekClaimed)
- Tipo base de póliza (BasePolicy)

### Hallazgo 3 — Señales de alerta combinadas
Ninguna señal por sí sola predice fraude. La combinación de:
- Sin testigos + sin reporte policial
- Cambio de domicilio reciente
- Múltiples reclamos anteriores
- Póliza muy reciente
...eleva significativamente el score.

### Hallazgo 4 — Umbral óptimo
Con umbral estándar de 0.5: Recall=0.45, Precision=0.28  
Con umbral de 0.3: Recall=0.69, Precision=0.14  
**Decisión:** priorizar recall — cada fraude no detectado cuesta
más que investigar un caso legítimo.

## Limitaciones identificadas

### Limitación 1 — Datos incompletos degradan el score
Cuando el texto del siniestro no contiene todos los campos estructurados,
el LLM retorna "unknown" en varios campos y el clasificador pierde precisión.
**Recomendación:** formularios estructurados en el frontend + texto libre como complemento.

### Limitación 2 — Latencia del LLM local
Ollama local en CPU tarda 2-3 minutos por análisis completo.
**Solución en producción:** Gemini API reduce a 3-5 segundos.

### Limitación 3 — Dataset histórico (1994-1996)
Los patrones de fraude han evolucionado. El modelo debe reentrenarse
con datos actuales de Inter.mx para maximizar precisión.

### Limitación 4 — OCR en documentos de baja calidad
Tesseract pierde precisión con documentos escaneados a menos de 200 DPI
o con manchas y deterioro físico.

## Próximas mejoras (Etapa 2)

1. **RAG con ChromaDB** — base de conocimiento de patrones de fraude históricos
2. **Gemini API** — reducir latencia de 3 min a 5 seg
3. **Prometheus + Grafana** — observabilidad en tiempo real
4. **MLflow UI** — comparación de experimentos de entrenamiento