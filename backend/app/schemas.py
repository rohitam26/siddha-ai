"""
Pydantic V2 Request & Response Schemas
--------------------------------------
Strict validation schemas for physical measurements, model predictions, and image analysis.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class ClinicalFeatureInput(BaseModel):
    # Demographics & Humor
    age: int = Field(..., ge=1, le=120, description="Patient age in years")
    gender: str = Field(..., description="Patient gender (Male, Female, Other)")
    predominant_humor: str = Field(..., description="Predominant Tridosha humor")

    # Neerkuri (Urine Physical Parameters)
    urine_color: str = Field(..., description="Siddha classified urine color")
    HSV_H: float = Field(..., ge=0.0, le=60.0, description="Hue on yellow-amber scale (0-60)")
    HSV_S: float = Field(..., ge=0.0, le=100.0, description="Saturation percentage (0-100)")
    HSV_V: float = Field(..., ge=0.0, le=100.0, description="Brightness value (0-100)")
    transparency_score: float = Field(..., ge=1.0, le=10.0, description="Clarity score: 1=turbid, 10=crystal clear")
    foam_percentage: float = Field(..., ge=0.0, le=100.0, description="Surface foam coverage percentage")
    foam_bubble_count: int = Field(..., ge=0, le=500, description="Estimated foam bubble count")
    sediment_percentage: float = Field(..., ge=0.0, le=100.0, description="Sediment deposit percentage")
    odor_score: float = Field(..., ge=1.0, le=10.0, description="Odour intensity score: 1=mild, 10=pungent")

    # Neikuri (Oil-Drop Geometric Parameters)
    oil_spread_diameter_mm: float = Field(..., ge=1.0, le=60.0, description="Estimated spread diameter in mm")
    oil_spread_speed: float = Field(..., ge=0.1, le=10.0, description="Spreading expansion velocity proxy")
    oil_shape: str = Field(..., description="Morphological shape category")
    branch_count: int = Field(..., ge=0, le=25, description="Number of radial branches/protrusions")
    circularity: float = Field(..., ge=0.01, le=1.0, description="Circularity metric: 4*pi*area / perimeter^2")
    symmetry_score: float = Field(..., ge=1.0, le=10.0, description="Radial symmetry score (1-10)")
    edge_roughness: float = Field(..., ge=0.0, le=15.0, description="Contour edge roughness index")
    fractal_dimension: float = Field(..., ge=1.0, le=2.0, description="Contour fractal dimension")

    # Tridosha Ratio Scores (sum ~ 100)
    vatham_score: float = Field(..., ge=0.0, le=100.0, description="Vatham humor percentage")
    pitham_score: float = Field(..., ge=0.0, le=100.0, description="Pitham humor percentage")
    kabham_score: float = Field(..., ge=0.0, le=100.0, description="Kabham humor percentage")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        valid = ["Male", "Female", "Other"]
        if v not in valid:
            return "Male"  # Safe default fallback
        return v


class PredictionResponse(BaseModel):
    patient_id: str
    timestamp: str
    predominant_humor_input: str
    digitized_observations: List[str]
    rule_flags: Dict[str, bool]
    prototype_risk: str
    confidence: float
    class_probabilities: Dict[str, float]
    top_feature_importances: Dict[str, float]
    shap_contributions: Optional[Dict[str, float]] = None
    shap_available: bool = False
    input_summary: Dict[str, Any]
    vision_metadata: Optional[Dict[str, Any]] = None
    disclaimer: str


class ImageQualityAssessment(BaseModel):
    quality_score: float
    sharpness_laplacian: float
    mean_brightness: float
    contrast_rms: float
    is_blurry: bool
    is_underexposed: bool
    is_overexposed: bool
    is_acceptable: bool
    warnings: List[str]


class VisionExtractionResponse(BaseModel):
    modality: str
    quality: ImageQualityAssessment
    extracted_features: Dict[str, Any]
    annotated_preview_base64: str
    segmentation_detected: Optional[bool] = True
    disclaimer: str


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    environment: str
    model_loaded: bool
    shap_available: bool
    database_connected: bool
    disclaimer: str
