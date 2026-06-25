"""
agent/nodes/extractor.py
-------------------------
Nodo 1 del agente: extrae entidades estructuradas del texto del siniestro.

Por qué este nodo existe:
    El clasificador LightGBM necesita datos estructurados (números y
    categorías). Los reportes de siniestro llegan como texto libre.
    Este nodo usa el LLM para convertir texto → estructura.

Por qué JSON y no texto libre:
    El siguiente nodo (scorer) necesita un dict de Python.
    Le pedimos al LLM que responda SOLO en JSON para poder
    parsearlo directamente sin procesamiento adicional.
"""

import json
import re
from langchain_core.messages import HumanMessage, SystemMessage
from agent.state import ClaimState
from llm.client import get_llm


SYSTEM_PROMPT = """Eres un extractor de información de reportes de siniestros de seguros.
Tu única tarea es extraer entidades del texto y devolverlas en JSON válido.
NO agregues explicaciones. NO uses markdown. SOLO JSON puro.

Extrae exactamente estos campos (usa "unknown" si no encuentras el valor):
{
    "Month": "mes del accidente en inglés (Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec)",
    "WeekOfMonth": número de semana del mes (1-5),
    "DayOfWeek": "día en inglés (Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday)",
    "Make": "marca del vehículo en inglés",
    "AccidentArea": "Urban o Rural",
    "DayOfWeekClaimed": "día del reclamo en inglés",
    "MonthClaimed": "mes del reclamo en inglés",
    "WeekOfMonthClaimed": número de semana del reclamo (1-5),
    "Sex": "Male o Female",
    "MaritalStatus": "Single, Married, Widow o Divorced",
    "Age": número entero,
    "Fault": "Policy Holder o Third Party",
    "PolicyType": "tipo de póliza",
    "VehicleCategory": "Sport, Sedan o Utility",
    "VehiclePrice": "rango de precio",
    "Deductible": número entero,
    "DriverRating": número entero 1-4,
    "Days_Policy_Accident": "none, 1 to 7, 8 to 15, 15 to 30, o more than 30",
    "Days_Policy_Claim": "none, 1 to 7, 8 to 15, 15 to 30, o more than 30",
    "PastNumberOfClaims": "none, 1, 2 to 4, o more than 4",
    "AgeOfVehicle": "new, 2 years, 3 years, 4 years, 5 years, 6 years, 7 years, o more than 7",
    "AgeOfPolicyHolder": "16 to 17, 18 to 20, 21 to 25, 26 to 30, 31 to 35, 36 to 40, 41 to 50, 51 to 65, o over 65",
    "PoliceReportFiled": "Yes o No",
    "WitnessPresent": "Yes o No",
    "AgentType": "Internal o External",
    "NumberOfSuppliments": "none, 1 to 2, 3 to 5, o more than 5",
    "AddressChange_Claim": "no change, under 6 months, 1 year, 2 to 3 years, o 4 to 8 years",
    "NumberOfCars": "1 vehicle, 2 vehicles, 3 to 4, o 5 to 8",
    "BasePolicy": "Liability, Collision o All Perils"
}"""


def extractor_node(state: ClaimState) -> ClaimState:
    """
    Lee el texto del siniestro y extrae entidades estructuradas.

    Args:
        state: estado actual con documento_texto

    Returns:
        state actualizado con entidades o error
    """
    try:
        llm = get_llm()

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Extrae las entidades de este reporte:\n\n{state['documento_texto']}")
        ]

        response = llm.invoke(messages)
        raw = response.content.strip()

        # Limpiar posibles backticks si el modelo los agrega
        raw = re.sub(r"```json|```", "", raw).strip()

        entidades = json.loads(raw)

        print(f"✅ Extractor: {len(entidades)} entidades extraídas")

        return {**state, "entidades": entidades}

    except json.JSONDecodeError as e:
        error_msg = f"Extractor no pudo parsear JSON: {e}"
        print(f"❌ {error_msg}")
        return {**state, "error": error_msg}

    except Exception as e:
        error_msg = f"Extractor falló: {e}"
        print(f"❌ {error_msg}")
        return {**state, "error": error_msg}