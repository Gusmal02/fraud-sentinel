"""
classifier/train.py
--------------------
Entrena el modelo LightGBM para detección de fraude en siniestros.

Por qué LightGBM y no Random Forest o XGBoost:
    - Más rápido en entrenamiento con datasets medianos
    - Maneja variables categóricas nativamente
    - Mejor rendimiento con datasets desbalanceados
    - Produce feature importance interpretable para el negocio

Por qué SMOTE:
    El dataset tiene 94% legítimos y 6% fraude.
    Sin balanceo, el modelo aprende a decir "todo es legítimo"
    y tiene 94% accuracy pero detecta 0% de fraudes — inútil.
    SMOTE genera casos sintéticos de fraude para balancear.

Métrica principal: ROC-AUC y Recall de fraude
    Accuracy es engañosa con datasets desbalanceados.
    Lo que importa es: de todos los fraudes reales,
    ¿cuántos detectamos? Eso es Recall.
"""

import pandas as pd
import numpy as np
import lightgbm as lgb
import mlflow
import mlflow.lightgbm
import pickle
import os
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    roc_auc_score,
    recall_score,
    precision_score,
    f1_score,
    classification_report,
)
from imblearn.over_sampling import SMOTE

# Rutas
DATA_PATH = Path("classifier/data/raw/fraud_oracle.csv")
MODEL_PATH = Path("classifier/model/fraud_model.pkl")
ENCODERS_PATH = Path("classifier/model/encoders.pkl")

# Variables que usaremos para entrenar
# Excluimos PolicyNumber y RepNumber porque son IDs, no features
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

TARGET = "FraudFound_P"

# Variables categóricas — LightGBM las maneja pero necesitan encoding
CATEGORICAL_FEATURES = [
    "Month", "DayOfWeek", "Make", "AccidentArea", "DayOfWeekClaimed",
    "MonthClaimed", "Sex", "MaritalStatus", "Fault", "PolicyType",
    "VehicleCategory", "VehiclePrice", "Days_Policy_Accident",
    "Days_Policy_Claim", "PastNumberOfClaims", "AgeOfVehicle",
    "AgeOfPolicyHolder", "PoliceReportFiled", "WitnessPresent",
    "AgentType", "NumberOfSuppliments", "AddressChange_Claim",
    "NumberOfCars", "BasePolicy"
]


def load_and_preprocess(data_path: Path) -> tuple:
    """
    Carga el dataset y preprocesa variables categóricas.

    Returns:
        tuple: (X, y, encoders) donde encoders se guardan
               para usar en inferencia con los mismos valores
    """
    df = pd.read_csv(data_path, encoding="utf-8-sig")

    # Verificar que existen las columnas necesarias
    missing = [f for f in FEATURES + [TARGET] if f not in df.columns]
    if missing:
        raise ValueError(f"Columnas faltantes en el dataset: {missing}")

    X = df[FEATURES].copy()
    y = df[TARGET].astype(int)

    # Encodear variables categóricas con LabelEncoder
    # Guardamos los encoders para usar exactamente los mismos
    # valores en inferencia — crítico para consistencia
    encoders = {}
    for col in CATEGORICAL_FEATURES:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

    return X, y, encoders


def train():
    """
    Pipeline completo de entrenamiento con tracking en MLflow.
    """
    print("🔍 Cargando y preprocesando datos...")
    X, y, encoders = load_and_preprocess(DATA_PATH)

    print(f"   Dataset: {len(X)} registros, {y.sum()} fraudes ({y.mean()*100:.1f}%)")

    # Split antes de SMOTE — SMOTE solo se aplica al training set
    # Si aplicáramos SMOTE antes, habría data leakage
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"   Train: {len(X_train)} | Test: {len(X_test)}")

    # Balancear con SMOTE solo el training set
    print("⚖️  Aplicando SMOTE para balancear clases...")
    smote = SMOTE(random_state=42)
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
    print(f"   Train balanceado: {len(X_train_balanced)} registros")

    # Configuración del modelo
    params = {
        "objective": "binary",
        "metric": "auc",
        "learning_rate": 0.05,
        "num_leaves": 31,
        "min_child_samples": 20,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "verbose": -1,
        "random_state": 42,
    }

    # Entrenar con MLflow tracking
    mlflow.set_experiment("fraud-sentinel")

    with mlflow.start_run(run_name="lightgbm-smote"):
        print("🚀 Entrenando LightGBM...")

        model = lgb.LGBMClassifier(**params, n_estimators=300)
        model.fit(
            X_train_balanced, y_train_balanced,
            eval_set=[(X_test, y_test)],
            callbacks=[lgb.early_stopping(50, verbose=False)]
        )

        # Evaluar en test set
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        y_pred = (y_pred_proba >= 0.3).astype(int)  # Umbral bajo para maximizar recall

        auc = roc_auc_score(y_test, y_pred_proba)
        recall = recall_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        # Loggear métricas en MLflow
        mlflow.log_params(params)
        mlflow.log_metric("auc", auc)
        mlflow.log_metric("recall_fraude", recall)
        mlflow.log_metric("precision_fraude", precision)
        mlflow.log_metric("f1_fraude", f1)

        print(f"\n📊 Resultados:")
        print(f"   ROC-AUC:   {auc:.4f}")
        print(f"   Recall:    {recall:.4f}")
        print(f"   Precision: {precision:.4f}")
        print(f"   F1:        {f1:.4f}")
        print(f"\n{classification_report(y_test, y_pred, target_names=['Legítimo', 'Fraude'])}")

        # Guardar modelo y encoders
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

        with open(MODEL_PATH, "wb") as f:
            pickle.dump(model, f)

        with open(ENCODERS_PATH, "wb") as f:
            pickle.dump(encoders, f)

        mlflow.lightgbm.log_model(model, "model")

        print(f"✅ Modelo guardado en {MODEL_PATH}")


if __name__ == "__main__":
    train()