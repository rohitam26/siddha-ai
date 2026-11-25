"""
Integration tests for FastAPI endpoints (v1 routes and legacy compatibility).
"""

import io
import cv2
import numpy as np


def test_root_endpoint(client):
    """GET / should return application name and disclaimer."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "Siddha AI" in data["app_name"]
    assert "disclaimer" in data


def test_health_endpoint(client):
    """GET /api/v1/health should return system status."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["model_loaded"] is True
    assert data["database_connected"] is True


def test_model_metadata_endpoint(client):
    """GET /api/v1/model/metadata should return feature list and metrics."""
    res = client.get("/api/v1/model/metadata")
    assert res.status_code == 200
    data = res.json()
    assert "metadata" in data
    assert "features" in data
    assert len(data["features"]) == 23


def test_predict_and_report_lifecycle(client, sample_clinical_payload):
    """POST /api/v1/analysis/predict -> GET /api/v1/reports/{id} -> GET /api/v1/reports."""
    # 1. Run prediction
    pred_res = client.post("/api/v1/analysis/predict", json=sample_clinical_payload)
    assert pred_res.status_code == 200
    pred_data = pred_res.json()
    patient_id = pred_data["patient_id"]
    assert patient_id.startswith("RPT-")
    assert pred_data["prototype_risk"] in ["Low", "Moderate", "High"]

    # 2. Retrieve persistent report by ID
    rep_res = client.get(f"/api/v1/reports/{patient_id}")
    assert rep_res.status_code == 200
    rep_data = rep_res.json()
    assert rep_data["patient_id"] == patient_id
    assert rep_data["prototype_risk"] == pred_data["prototype_risk"]

    # 3. Verify report appears in reports listing
    list_res = client.get("/api/v1/reports?limit=10")
    assert list_res.status_code == 200
    all_reports = list_res.json()
    assert any(r["patient_id"] == patient_id for r in all_reports)


def test_neerkuri_vision_endpoint(client, synthetic_image_bgr):
    """POST /api/v1/vision/neerkuri accepts image file and returns features."""
    _, buf = cv2.imencode(".jpg", synthetic_image_bgr)
    files = {"file": ("urine_sample.jpg", io.BytesIO(buf.tobytes()), "image/jpeg")}
    res = client.post("/api/v1/vision/neerkuri", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["modality"] == "neerkuri"
    assert "quality" in data
    assert "extracted_features" in data


def test_neikuri_vision_endpoint(client, synthetic_image_bgr):
    """POST /api/v1/vision/neikuri accepts image file and returns drop features."""
    _, buf = cv2.imencode(".jpg", synthetic_image_bgr)
    files = {"file": ("oil_drop.jpg", io.BytesIO(buf.tobytes()), "image/jpeg")}
    res = client.post("/api/v1/vision/neikuri", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["modality"] == "neikuri"
    assert "quality" in data
    assert "extracted_features" in data


def test_legacy_upload_compatibility(client, synthetic_image_bgr):
    """POST /upload should remain backwards compatible with original client."""
    _, buf = cv2.imencode(".jpg", synthetic_image_bgr)
    files = {"file": ("sample.jpg", io.BytesIO(buf.tobytes()), "image/jpeg")}
    res = client.post("/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert "extracted_features" in data
    assert "disclaimer" in data
