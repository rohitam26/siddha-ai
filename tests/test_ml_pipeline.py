"""
Unit tests for Machine Learning Pipeline & Inference Service.
"""

import pytest
import numpy as np
import pandas as pd
from app.ml_service import ml_service, SHAP_AVAILABLE


def test_ml_service_is_loaded():
    """Verify that the model bundle is loaded and contains necessary metadata."""
    assert ml_service.is_loaded is True
    assert ml_service.pipeline is not None
    assert ml_service.target_encoder is not None
    assert len(ml_service.all_features) == 23


def test_ml_prediction_format(sample_clinical_payload):
    """Verify predict returns risk label, probability distribution, and confidence."""
    res = ml_service.predict(sample_clinical_payload)
    assert res["prototype_risk"] in ["Low", "Moderate", "High"]
    assert 0.0 <= res["confidence"] <= 1.0
    assert set(res["class_probabilities"].keys()) == {"Low", "Moderate", "High"}
    # Probabilities sum to ~1.0
    prob_sum = sum(res["class_probabilities"].values())
    assert pytest.approx(prob_sum, abs=0.01) == 1.0


def test_ml_prediction_with_unseen_categorical(sample_clinical_payload):
    """Verify ColumnTransformer gracefully handles unseen categorical values."""
    payload = sample_clinical_payload.copy()
    payload["oil_shape"] = "NonExistentShape123"
    payload["urine_color"] = "NeonPurple"
    res = ml_service.predict(payload)
    assert res["prototype_risk"] in ["Low", "Moderate", "High"]
    assert 0.0 <= res["confidence"] <= 1.0


def test_shap_explainability_output(sample_clinical_payload):
    """Verify SHAP attributions are generated when SHAP is available."""
    res = ml_service.predict(sample_clinical_payload)
    if SHAP_AVAILABLE:
        assert res["shap_available"] is True
        assert res["shap_contributions"] is not None
        assert len(res["shap_contributions"]) > 0
        for feat, val in res["shap_contributions"].items():
            assert isinstance(val, float)
