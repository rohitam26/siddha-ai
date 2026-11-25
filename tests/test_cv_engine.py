"""
Unit tests for Computer Vision Engine (Neerkuri & Neikuri).
"""

import pytest
import cv2
import numpy as np
import cv_engine


def test_image_validation_empty_bytes():
    """Validates that empty byte input raises ValueError."""
    with pytest.raises(ValueError, match="empty"):
        cv_engine.validate_and_decode_image(b"")


def test_image_validation_valid(synthetic_image_bgr):
    """Validates that valid image bytes decode to expected BGR array."""
    _, buf = cv2.imencode(".jpg", synthetic_image_bgr)
    img_bgr, info = cv_engine.validate_and_decode_image(buf.tobytes())
    assert img_bgr.shape == synthetic_image_bgr.shape
    assert info["width"] == 300
    assert info["height"] == 300


def test_image_quality_assessment(synthetic_image_bgr):
    """Verify blurriness, exposure, and contrast evaluation."""
    quality = cv_engine.assess_image_quality(synthetic_image_bgr)
    assert 0.0 <= quality["quality_score"] <= 100.0
    assert "sharpness_laplacian" in quality
    assert "mean_brightness" in quality
    assert "contrast_rms" in quality
    assert isinstance(quality["is_acceptable"], bool)


def test_neerkuri_analysis(synthetic_image_bgr):
    """Verify urine physical parameter extraction from synthetic image."""
    res = cv_engine.analyze_neerkuri_image(synthetic_image_bgr)
    assert res["modality"] == "neerkuri"
    assert "urine_color" in res["extracted_features"]
    assert "HSV_H" in res["extracted_features"]
    assert "foam_percentage" in res["extracted_features"]
    assert res["annotated_preview_base64"].startswith("data:image/jpeg;base64,")


def test_neikuri_analysis(synthetic_image_bgr):
    """Verify oil drop geometric morphology extraction from synthetic image."""
    res = cv_engine.analyze_neikuri_image(synthetic_image_bgr)
    assert res["modality"] == "neikuri"
    feats = res["extracted_features"]
    assert "oil_shape" in feats
    assert 0.0 <= feats["circularity"] <= 1.0
    assert 0.0 <= feats["solidity"] <= 1.0
    assert res["annotated_preview_base64"].startswith("data:image/jpeg;base64,")
