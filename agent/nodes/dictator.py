"""
agent/nodes/dictator.py
------------------------
Nodo 3 del agente: redacta el dictamen final en lenguaje natural.

Por qué este nodo es importante para el negocio:
    El score numérico (0.6572) no le dice nada a un ajustador humano.
    Este nodo convierte el score + entidades + factores de riesgo
    en un dictamen legible que el ajustador puede usar directamente.

Por qué el LLM y no una plantilla fija:
    Una plantilla fija diría lo mismo para todos los casos.
    El LLM adapta el dictamen al contexto específico del siniestro —
    menciona los factores relevantes de ESE caso, no de todos.

Auditoría:
    El dictamen incluye siempre el score numérico y los factores
    de riesgo para que la decisión sea trazable y auditable.
"""

from langchain_core.messages import HumanMessage, SystemMessage
from agent.state import ClaimState
from llm.client import get_llm


SYSTEM_PROMPT = """Eres un analista experto en detección de fraude para una aseguradora mexicana.
Tu tarea es redactar dictámenes claros, profesionales y auditables en español.

El dictamen debe:
1. Iniciar con el nivel de riesgo detectado (BAJO, MEDIO o ALTO)
2. Mencionar el score de fraude como porcentaje
3. Explicar los principales factores de riesgo encontrados
4. Dar una recomendación clara de acción
5. Ser conciso — máximo 200 palabras

Tono: profesional, directo, sin tecnicismos innecesarios.
Audiencia: ajustadores de siniestros, no ingenieros."""


def dictator_node(state: ClaimState) -> ClaimState:
    """
    Redacta el dictamen final basándose en el estado completo del agente.

    Maneja dos casos:
        1. Proceso exitoso: dictamen con score y factores de riesgo
        2. Error previo: dictamen de error explicando qué falló

    Args:
        state: estado completo del agente

    Returns:
        state actualizado con dictamen
    """
    try:
        llm = get_llm()

        # Caso error — redactar dictamen de error
        if state.get("error"):
            dictamen = (
                f"⚠️ DICTAMEN NO DISPONIBLE\n\n"
                f"El sistema no pudo completar el análisis del siniestro.\n"
                f"Motivo: {state['error']}\n\n"
                f"Acción requerida: revisión manual por el equipo de ajuste."
            )
            return {**state, "dictamen": dictamen}

        fraud_result = state["fraud_result"]
        entidades = state["entidades"]

        # Construir prompt con contexto completo
        contexto = f"""
Score de fraude: {fraud_result['fraud_score']} ({fraud_result['fraud_score']*100:.1f}%)
Nivel de riesgo: {fraud_result['risk_level']}
¿Se marca como fraude?: {'Sí' if fraud_result['is_fraud'] else 'No'}
Principales factores de riesgo: {', '.join(fraud_result['top_risk_factors'])}

Datos clave del siniestro:
- Vehículo: {entidades.get('Make', 'N/D')} {entidades.get('VehicleCategory', '')}
- Área del accidente: {entidades.get('AccidentArea', 'N/D')}
- Reporte policial: {entidades.get('PoliceReportFiled', 'N/D')}
- Testigos presentes: {entidades.get('WitnessPresent', 'N/D')}
- Reclamos anteriores: {entidades.get('PastNumberOfClaims', 'N/D')}
- Cambio de domicilio reciente: {entidades.get('AddressChange_Claim', 'N/D')}
- Culpa: {entidades.get('Fault', 'N/D')}
"""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Redacta el dictamen para este siniestro:\n{contexto}")
        ]

        response = llm.invoke(messages)
        dictamen = response.content.strip()

        print(f"✅ Dictador: dictamen generado ({len(dictamen)} caracteres)")

        return {**state, "dictamen": dictamen}

    except Exception as e:
        error_msg = f"Dictador falló: {e}"
        print(f"❌ {error_msg}")
        return {
            **state,
            "dictamen": f"⚠️ Error generando dictamen: {error_msg}"
        }