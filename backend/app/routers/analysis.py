"""
Analysis Router
---------------
Handles feature-based model inference, rule engine observations,
and persistent SQLite report creation.
"""

import uuid
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import AnalysisRecord
from app.schemas import ClinicalFeatureInput, PredictionResponse
from app.ml_service import ml_service
from app.rule_engine import generate_observations, rule_based_flags

router = APIRouter(prefix="/analysis", tags=["Predictive Analysis & Rule Engine"])


@router.post("/predict", response_model=PredictionResponse)
def run_prediction(payload: ClinicalFeatureInput, db: Session = Depends(get_db)):
    """
    Accepts digitized Siddha physical and clinical parameters, executes:
    1. Deterministic Rule Engine observation synthesis
    2. ML model inference (Random Forest classifier)
    3. Per-patient local SHAP attribution
    4. Persistent storage in SQLite database
    """
    data = payload.model_dump()

    # 1. Deterministic Rule Engine Observations
    observations = generate_observations(data)
    flags = rule_based_flags(data)

    # 2. ML Inference with SHAP
    try:
        ml_result = ml_service.predict(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {e}")

    # Generate Unique Patient / Report ID
    patient_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
    timestamp_str = datetime.now(timezone.utc).isoformat()

    response_data = {
        "patient_id": patient_id,
        "timestamp": timestamp_str,
        "predominant_humor_input": data["predominant_humor"],
        "digitized_observations": observations,
        "rule_flags": flags,
        "prototype_risk": ml_result["prototype_risk"],
        "confidence": ml_result["confidence"],
        "class_probabilities": ml_result["class_probabilities"],
        "top_feature_importances": ml_result["top_feature_importances"],
        "shap_contributions": ml_result["shap_contributions"],
        "shap_available": ml_result["shap_available"],
        "input_summary": data,
        "vision_metadata": None,
        "disclaimer": settings.DISCLAIMER,
    }

    # 3. Persistent Storage in SQLite Database
    try:
        record = AnalysisRecord(
            patient_id=patient_id,
            age=data["age"],
            gender=data["gender"],
            predominant_humor=data["predominant_humor"],
            prototype_risk=ml_result["prototype_risk"],
            confidence=ml_result["confidence"],
            class_probabilities_json=json.dumps(ml_result["class_probabilities"]),
            digitized_observations_json=json.dumps(observations),
            rule_flags_json=json.dumps(flags),
            top_feature_importances_json=json.dumps(ml_result["top_feature_importances"]),
            shap_contributions_json=json.dumps(ml_result["shap_contributions"]) if ml_result["shap_contributions"] else None,
            input_summary_json=json.dumps(data),
            vision_metadata_json=None,
        )
        db.add(record)
        db.commit()
    except Exception as e:
        db.rollback()
        # Continue and return the response even if persistent logging fails
        pass

    return PredictionResponse(**response_data)
