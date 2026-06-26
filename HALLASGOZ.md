Ahora borra el contenido de HALLAZGOS.md y pega esto:
markdown# Hallazgos y Aprendizajes — Fraud Sentinel

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

---

## Hallazgos del modelo

### Hallazgo 1 — Dataset severamente desbalanceado
El 94% de los casos son legítimos. Un modelo naive que prediga siempre
"legítimo" tendría 94% de accuracy pero 0% de utilidad real.
**Solución aplicada:** SMOTE exclusivamente en el training set.
Aplicar SMOTE antes del split causaría data leakage — los casos sintéticos
del test set habrían sido generados con información del training set.

### Hallazgo 2 — Umbral óptimo en 0.3, no 0.5
Con umbral estándar de 0.5: Recall=0.45  
Con umbral de 0.3: Recall=0.69  
**Decisión:** En detección de fraude el costo de un falso negativo
(dejar pasar un fraude) es mayor que el de un falso positivo
(investigar un caso legítimo). Se prioriza recall sobre precision.

### Hallazgo 3 — Variables más predictivas
Según feature importance de LightGBM:

| Posición | Variable | Interpretación |
|----------|----------|---------------|
| 1 | Make | Marca del vehículo — ciertos modelos tienen mayor incidencia |
| 2 | Age | Edad del asegurado — perfiles de riesgo diferenciados |
| 3 | AgeOfVehicle | Vehículos de cierta antigüedad son más frecuentes en fraude |
| 4 | DayOfWeekClaimed | El día del reclamo tiene correlación estadística con fraude |
| 5 | BasePolicy | El tipo base de póliza influye en el perfil de riesgo |

### Hallazgo 4 — Señales de alerta combinadas
Ninguna señal por sí sola predice fraude con certeza. La combinación de:
- Sin testigos + sin reporte policial
- Cambio de domicilio en últimos 6 meses
- Múltiples reclamos anteriores
- Póliza de menos de 30 días de vigencia
- Agente externo con monto alto

...eleva significativamente el score de fraude.

### Hallazgo 5 — ROC-AUC vs Accuracy
El modelo tiene 74% de accuracy general pero 80.87% de ROC-AUC.
Accuracy es engañosa con datasets desbalanceados.
ROC-AUC mide la capacidad real de discriminación entre clases.

---

## Limitaciones identificadas

### Limitación 1 — Datos incompletos degradan el score
Cuando el texto del siniestro no contiene todos los campos estructurados,
el LLM retorna "unknown" en varios campos y el clasificador pierde precisión.
**Recomendación:** formularios estructurados en el frontend + texto libre como complemento.

### Limitación 2 — Latencia del LLM local
Ollama local en CPU tarda 2-3 minutos por análisis completo.
Dos llamadas secuenciales al LLM (extractor + dictaminador) son el cuello de botella.
**Solución en producción:** Gemini API reduce a 3-5 segundos.
**Optimización adicional:** caché de respuestas en Redis para siniestros repetidos.

### Limitación 3 — Dataset histórico (1994-1996)
Los patrones de fraude han evolucionado significativamente.
El modelo debe reentrenarse con datos actuales del sector para maximizar precisión.
**Ventaja del diseño:** MLflow tracking permite comparar versiones del modelo
y reentrenar sin modificar la arquitectura del agente.

### Limitación 4 — OCR en documentos de baja calidad
Tesseract pierde precisión con documentos escaneados a menos de 200 DPI,
manchas, deterioro físico o letra manuscrita.
**Mitigación actual:** renderizado a 300 DPI antes del OCR.
**Mejora futura:** modelos de visión computacional para documentos degradados.

---

## Decisiones de diseño y su razonamiento

### ¿Por qué texto → Markdown antes del RAG?
El LLM procesa mejor texto con estructura visible. Markdown le indica
jerarquía de información sin instrucciones adicionales en el prompt.
Un encabezado `##` comunica importancia mejor que texto plano.

### ¿Por qué chunks de 500 caracteres con overlap de 50?
- Chunks muy grandes: el embedding representa demasiadas ideas, baja precisión en búsqueda
- Chunks muy pequeños: pierden contexto, una oración sola puede no tener sentido
- Overlap de 50: garantiza que oraciones en el límite entre chunks aparezcan completas en al menos uno

### ¿Por qué K=3 en recuperación RAG?
Suficiente contexto para el dictaminador sin saturar el prompt.
Más chunks = más tokens = más latencia sin mejora proporcional en calidad.

---

## Métricas finales del sistema

| Componente | Métrica | Valor |
|-----------|---------|-------|
| Clasificador | ROC-AUC | 0.8087 |
| Clasificador | Recall fraude | 0.6919 |
| Clasificador | Precision fraude | 0.1445 |
| Clasificador | F1 fraude | 0.2390 |
| API | Tests passing | 8/8 |
| Seguridad | Bandit issues High/Medium | 0 |
| RAG | Chunks indexados | 5 |
| Docker | Servicios en stack | 5 |

---

## Próximas mejoras

### Etapa siguiente
1. **Gemini API** — reducir latencia de 3 min a 5 seg
2. **Formulario estructurado** — complementar texto libre con campos obligatorios
3. **Reentrenamiento** — con datos reales del sector asegurador mexicano