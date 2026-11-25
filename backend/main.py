"""
Siddha AI - Digital Neerkuri & Neikuri Analysis Platform
---------------------------------------------------------
FastAPI Application Entrypoint
Provides modular REST APIs, OpenCV vision processing, ML explainability,
and persistent SQLite historical reporting.

DISCLAIMER:
Academic research and engineering prototype.
Trained on synthetic demonstration data. NOT FOR CLINICAL DIAGNOSIS.
"""

import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Add current directory and backend root to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.database import engine, Base, get_db
from app.routers import health, vision, analysis, reports
from app.schemas import ClinicalFeatureInput
import cv_engine

# Structured Logging Setup
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("siddha_ai")


# Ensure database tables exist at import time
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure SQLite database tables are created
    logger.info("Initializing persistent SQLite database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} initialized successfully.")
    yield
    # Shutdown
    logger.info("Application shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-Assisted Digital Neerkuri (Urine) and Neikuri (Oil Drop) Analysis Platform. "
        "Standardizes physical Ayurvedic/Siddha observations into measurable digital features "
        "with transparent deterministic rule engines and explainable machine learning."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "error": str(exc)},
    )


# Mount Modular V1 Routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(vision.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")


# -------------------------------------------------------------------
# Backwards-Compatibility Endpoints (Preserving Legacy Client Support)
# -------------------------------------------------------------------

@app.get("/", tags=["System"])
def root():
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "framing": "Digitizes Neerkuri/Neikuri observation into measurable features; does not diagnose disease.",
        "api_v1_docs": "/docs",
        "disclaimer": settings.DISCLAIMER,
    }


@app.post("/upload", tags=["Legacy Compatibility"])
async def legacy_upload(file: UploadFile = File(...)):
    """Legacy upload endpoint: extracts features and quality from uploaded photo."""
    contents = await file.read()
    try:
        img_bgr, info = cv_engine.validate_and_decode_image(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image processing failed: {e}")

    # Run Neikuri analysis for contour circularity + Neerkuri for color/HSV
    neikuri_res = cv_engine.analyze_neikuri_image(img_bgr)
    neerkuri_res = cv_engine.analyze_neerkuri_image(img_bgr)

    merged = {
        **neerkuri_res["extracted_features"],
        **neikuri_res["extracted_features"],
    }
    return {
        "disclaimer": settings.DISCLAIMER,
        "quality": neikuri_res["quality"],
        "extracted_features": merged,
        "annotated_preview": neikuri_res["annotated_preview_base64"],
    }


@app.post("/predict", tags=["Legacy Compatibility"])
def legacy_predict(payload: ClinicalFeatureInput, db: Session = Depends(get_db)):
    """Legacy predict endpoint routed to the modular analysis router."""
    return analysis.run_prediction(payload, db)


@app.get("/report/{patient_id}", tags=["Legacy Compatibility"])
def legacy_get_report(patient_id: str, db: Session = Depends(get_db)):
    """Legacy report endpoint routed to the modular reports router."""
    return reports.get_report_by_id(patient_id, db)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
