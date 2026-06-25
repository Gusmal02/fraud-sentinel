"""
classifier/predict.py
----------------------
Inferencia del modelo LightGBM para scoring de fraude.

Por qué un módulo separado de train.py:
    El entrenamiento ocurre una vez. La inferencia ocurre
    miles de veces en producción. Separarlos permite:
    - Cargar el modelo una sola vez en memoria (singleton)
    - Actualizar el modelo sin tocar la lógica de inferencia
    - Testear inferencia de forma independiente
"""

import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from functools import lru_cache

MODEL_PATH = Path("classifier/model/fraud_model.pkl")
ENCODERS_PATH = Path("classifier/model/encoders.pkl")

# Mismo orden que en train.py — crítico para consistencia
FEATURES = [
    "Month", "WeekOfMonth", "DayOfWeek", "Make", "AccidentArea",
    "DayOfWeekClaimed", "MonthClaimed", "WeekOfMonthClaimed",
    "Sex", "MaritalStatus", "Age", "Fault", "PolicyType",
    "VehicleCategory", "VehiclePrice", "Deductible", "DriverRating",
    "Days_Policy_Accident", "Days_Policy_Claim", "PastNumberOfClaims",
    "AgeOfVehicle", "AgeOfPolicyHolder", "PoliceReportFiled",
    "WitnessPresent", "AgentType", "NumberOfSuppliments",
    "AddressChange_Claim", "NumberOfCars", "BasePolicy"
]

CATEGORICAL_FEATURES = [
    "Month", "DayOfWeek", "Make", "AccidentArea", "DayOfWeekClaimed",
    "MonthClaimed", "Sex", "MaritalStatus", "Fault", "PolicyType",
    "VehicleCategory", "VehiclePrice", "Days_Policy_Accident",
    "Days_Policy_Claim", "PastNumberOfClaims", "AgeOfVehicle",
    "AgeOfPolicyHolder", "PoliceReportFiled", "WitnessPresent",
    "AgentType", "NumberOfSuppliments", "AddressChange_Claim",
    "NumberOfCars", "BasePolicy"
]

# Umbral de decisión — mismo que en entrenamiento
FRAUD_THRESHOLD = 0.3


@lru_cache(maxsize=1)
def _load_model():
    """
    Carga el modelo una sola vez y lo mantiene en memoria.
    lru_cache garantiza que aunque se llame mil veces,
    solo lee el archivo una vez.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modelo no encontrado en {MODEL_PATH}. "
            "Ejecuta classifier/train.py primero."
        )
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


@lru_cache(maxsize=1)
def _load_encoders():
    """Carga los encoders una sola vez."""
    with open(ENCODERS_PATH, "rb") as f:
        return pickle.load(f)


def predict_fraud(claim_data: dict) -> dict:
    """
    Genera score de fraude para un siniestro.

    Args:
        claim_data: dict con los campos del siniestro.
                   Campos faltantes se rellenan con valores
                   por defecto para no romper la inferencia.

    Returns:
        dict con:
            - fraud_score: float 0-1 (probabilidad de fraude)
            - is_fraud: bool (True si score >= FRAUD_THRESHOLD)
            - risk_level: str ("BAJO", "MEDIO", "ALTO")
            - top_risk_factors: list de factores que más
                               contribuyeron al score
    """
    model = _load_model()
    encoders = _load_encoders()

    # Construir DataFrame con valores por defecto para campos faltantes
    row = {feat: claim_data.get(feat, "unknown") for feat in FEATURES}
    df = pd.DataFrame([row])

    # Aplicar los mismos encoders usados en entrenamiento
    for col in CATEGORICAL_FEATURES:
        if col in encoders:
            le = encoders[col]
            # Si el valor no fue visto en entrenamiento, usar 0
            df[col] = df[col].apply(
                lambda x: le.transform([str(x)])[0]
                if str(x) in le.classes_
                else 0
            )

    # Asegurar tipos numéricos correctos
    for col in df.columns:
        if col not in CATEGORICAL_FEATURES:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Inferencia
    fraud_score = float(model.predict_proba(df)[0][1])
    is_fraud = fraud_score >= FRAUD_THRESHOLD

    # Nivel de riesgo
    if fraud_score < 0.3:
        risk_level = "BAJO"
    elif fraud_score < 0.6:
        risk_level = "MEDIO"
    else:
        risk_level = "ALTO"

    # Top factores de riesgo usando feature importance del modelo
    importances = model.feature_importances_
    feature_importance = sorted(
        zip(FEATURES, importances),
        key=lambda x: x[1],
        reverse=True
    )
    top_risk_factors = [f for f, _ in feature_importance[:5]]

    return {
        "fraud_score": round(fraud_score, 4),
        "is_fraud": is_fraud,
        "risk_level": risk_level,
        "top_risk_factors": top_risk_factors,
        "threshold_used": FRAUD_THRESHOLD,
    }