"""
agent/nodes/dictator.py
------------------------
Nodo 3 del agente: redacta el dictamen final en lenguaje natural.

Actualización Etapa 2 — RAG integrado:
    Antes de redactar el dictamen, el nodo recupera patrones
    de fraude similares de ChromaDB para enriquecer el análisis.
    El LLM ahora tiene tres fuentes de información:
    1. Entidades del siniestro actual
    2. Score del clasificador
    3. Patrones históricos recuperados por RAG
"""

from langchain_core.messages import HumanMessage, SystemMessage
from agent.state import ClaimState
from llm.client import get_llm
from rag.retriever import retrieve_patrones


SYSTEM_PROMPT = """Eres un analista experto en detección de fraude para una aseguradora mexicana.
Tu tarea es redactar dictámenes claros, profesionales y auditables en español.

El dictamen debe:
1. Iniciar con el nivel de riesgo detectado (BAJO, MEDIO o ALTO)
2. Mencionar el score de fraude como porcentaje
3. Explicar los principales factores de riesgo encontrados
4. Comparar con patrones históricos de fraude cuando sean relevantes
5. Dar una recomendación clara de acción
6. Ser conciso — máximo 250 palabras

Tono: profesional, directo, sin tecnicismos innecesarios.
Audiencia: ajustadores de siniestros, no ingenieros."""


def dictator_node(state: ClaimState) -> ClaimState:
    """
    Redacta el dictamen final con contexto RAG.

    Args:
        state: estado completo del agente

    Returns:
        state actualizado con dictamen enriquecido
    """
    try:
        llm = get_llm()

        # Caso error
        if state.get("error"):
            dictamen = (
                f"⚠️ DICTAMEN NO DISPONIBLE\n\n"
                f"El sistema no pudo completar el análisis.\n"
                f"Motivo: {state['error']}\n\n"
                f"Acción requerida: revisión manual por el equipo de ajuste."
            )
            return {**state, "dictamen": dictamen}

        fraud_result = state["fraud_result"]
        entidades = state["entidades"]

        # Construir query para RAG basada en señales del siniestro
        query = f"""
        Siniestro con score de fraude {fraud_result['fraud_score']:.2f}.
        Reporte policial: {entidades.get('PoliceReportFiled', 'unknown')}.
        Testigos: {entidades.get('WitnessPresent', 'unknown')}.
        Reclamos anteriores: {entidades.get('PastNumberOfClaims', 'unknown')}.
        Cambio de domicilio: {entidades.get('AddressChange_Claim', 'unknown')}.
        Agente: {entidades.get('AgentType', 'unknown')}.
        """

        # Recuperar patrones relevantes de ChromaDB
        patrones_contexto = retrieve_patrones(query)

        # Construir prompt con contexto completo + RAG
        contexto = f"""
Score de fraude: {fraud_result['fraud_score']} ({fraud_result['fraud_score']*100:.1f}%)
Nivel de riesgo: {fraud_result['risk_level']}
¿Se marca como fraude?: {'Sí' if fraud_result['is_fraud'] else 'No'}
Principales factores: {', '.join(fraud_result['top_risk_factors'])}

Datos clave del siniestro:
- Vehículo: {entidades.get('Make', 'N/D')} {entidades.get('VehicleCategory', '')}
- Área: {entidades.get('AccidentArea', 'N/D')}
- Reporte policial: {entidades.get('PoliceReportFiled', 'N/D')}
- Testigos: {entidades.get('WitnessPresent', 'N/D')}
- Reclamos anteriores: {entidades.get('PastNumberOfClaims', 'N/D')}
- Cambio de domicilio: {entidades.get('AddressChange_Claim', 'N/D')}
- Agente: {entidades.get('AgentType', 'N/D')}
- Culpa: {entidades.get('Fault', 'N/D')}

Patrones históricos de fraude relevantes:
{patrones_contexto}
"""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Redacta el dictamen para este siniestro:\n{contexto}")
        ]

        response = llm.invoke(messages)
        dictamen = response.content.strip()

        print(f"✅ Dictador: dictamen con RAG generado ({len(dictamen)} caracteres)")

        return {**state, "dictamen": dictamen}

    except Exception as e:
        error_msg = f"Dictador falló: {e}"
        print(f"❌ {error_msg}")
        return {
            **state,
            "dictamen": f"⚠️ Error generando dictamen: {error_msg}"
        }