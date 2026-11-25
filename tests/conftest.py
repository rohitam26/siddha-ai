"""
pytest configuration and fixtures for Siddha AI test suite.
"""

import sys
from pathlib import Path
import pytest
import numpy as np

# Add backend and project root to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from main import app


@pytest.fixture(scope="session")
def client():
    """FastAPI test client fixture."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_clinical_payload():
    """Valid standard physical observation payload."""
    return {
        "age": 45,
        "gender": "Male",
        "predominant_humor": "Pitham",
        "urine_color": "Yellow",
        "HSV_H": 45.0,
        "HSV_S": 50.0,
        "HSV_V": 70.0,
        "transparency_score": 6.5,
        "foam_percentage": 20.0,
        "foam_bubble_count": 55,
        "sediment_percentage": 12.0,
        "odor_score": 3.5,
        "oil_spread_diameter_mm": 18.0,
        "oil_spread_speed": 5.2,
        "oil_shape": "Ring",
        "branch_count": 2,
        "circularity": 0.72,
        "symmetry_score": 6.8,
        "edge_roughness": 2.8,
        "fractal_dimension": 1.18,
        "vatham_score": 33.0,
        "pitham_score": 34.0,
        "kabham_score": 33.0,
    }


@pytest.fixture
def synthetic_image_bgr():
    """Generates a synthetic 300x300 BGR test image containing a circular disk."""
    import cv2
    img = np.full((300, 300, 3), 180, dtype=np.uint8)  # Light gray background
    cv2.circle(img, (150, 150), 60, (50, 80, 120), -1)  # Darker circular blob
    return img
