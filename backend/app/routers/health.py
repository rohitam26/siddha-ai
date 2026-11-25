"""
Health & Metadata Router
------------------------
Health probes, environment status, and model metadata.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.database import get_db
from app.schemas import HealthResponse
from app.ml_service import ml_service, SHAP_AVAILABLE

router = APIRouter(tags=["Health & System"])


@router.get("/health", response_model=HealthResponse)
def get_health_status(db: Session = Depends(get_db)):
    """System health check and dependency connectivity probe."""
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return HealthResponse(
        status="healthy" if (db_ok and ml_service.is_loaded) else "degraded",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        model_loaded=ml_service.is_loaded,
        shap_available=SHAP_AVAILABLE,
        database_connected=db_ok,
        disclaimer=settings.DISCLAIMER,
    )


@router.get("/model/metadata")
def get_model_metadata():
    """Returns training parameters, cross-validation benchmarks, and feature schemas."""
    return {
        "metadata": ml_service.metadata,
        "is_loaded": ml_service.is_loaded,
        "features": ml_service.all_features,
        "disclaimer": settings.DISCLAIMER,
    }
