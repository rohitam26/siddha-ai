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


def test_delete_report_endpoint(client, sample_clinical_payload):
    """DELETE /api/v1/reports/{id} removes record from SQLite."""
    # Create report
    create_res = client.post("/api/v1/analysis/predict", json=sample_clinical_payload)
    pid = create_res.json()["patient_id"]

    # Delete report
    del_res = client.delete(f"/api/v1/reports/{pid}")
    assert del_res.status_code == 200
    assert "deleted" in del_res.json()["message"]

    # Verify 404 on subsequent get
    get_res = client.get(f"/api/v1/reports/{pid}")
    assert get_res.status_code == 404


def test_report_not_found_404(client):
    """GET /api/v1/reports/NONEXISTENT should return 404."""
    res = client.get("/api/v1/reports/NONEXISTENT-999")
    assert res.status_code == 404


def test_invalid_payload_rejected_with_422(client):
    """POST /api/v1/analysis/predict with invalid age should return 422 Unprocessable Entity."""
    bad_payload = {"age": 999, "gender": "Male"}  # age > 120 and missing required features
    res = client.post("/api/v1/analysis/predict", json=bad_payload)
    assert res.status_code == 422


def test_corrupt_image_upload_rejected(client):
    """POST /api/v1/vision/neerkuri with invalid bytes should return 400 Bad Request."""
    corrupt_bytes = b"NOT_A_VALID_IMAGE_HEADER_12345"
    files = {"file": ("corrupt.jpg", io.BytesIO(corrupt_bytes), "image/jpeg")}
    res = client.post("/api/v1/vision/neerkuri", files=files)
    assert res.status_code == 400

