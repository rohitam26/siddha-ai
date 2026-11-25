"""
Vision Router (Neerkuri & Neikuri)
----------------------------------
Image upload, quality assessment, and computer vision feature extraction endpoints.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
from app.schemas import VisionExtractionResponse
import cv_engine

router = APIRouter(prefix="/vision", tags=["Computer Vision"])


@router.post("/neerkuri", response_model=VisionExtractionResponse)
async def analyze_neerkuri_upload(file: UploadFile = File(...)):
    """
    Accepts a urine photograph and extracts physical visual features:
    - Color calibration in HSV space & Siddha color categorization
    - Transparency & optical turbidity assessment
    - Foam zone meniscus detection & bubble counts
    - Visual quality validation (blurriness, exposure, contrast)
    """
    contents = await file.read()
    try:
        img_bgr, info = cv_engine.validate_and_decode_image(contents)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image decoding failed: {e}")

    result = cv_engine.analyze_neerkuri_image(img_bgr)
    return VisionExtractionResponse(
        modality="neerkuri",
        quality=result["quality"],
        extracted_features=result["extracted_features"],
        annotated_preview_base64=result["annotated_preview_base64"],
        disclaimer=settings.DISCLAIMER,
    )


@router.post("/neikuri", response_model=VisionExtractionResponse)
async def analyze_neikuri_upload(file: UploadFile = File(...)):
    """
    Accepts an oil-drop photograph on urine surface and extracts morphological geometry:
    - Drop boundary segmentation and contour extraction
    - Circularity, aspect ratio, solidity, and fractal dimension
    - Edge roughness and radial symmetry
    - Branch / protrusion count via convexity defects
    - Siddha oil shape classification (Circular, Ring, Spiral, Lotus, Snake, Branched, Irregular)
    - Annotated contour overlay for visual verification
    """
    contents = await file.read()
    try:
        img_bgr, info = cv_engine.validate_and_decode_image(contents)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image decoding failed: {e}")

    result = cv_engine.analyze_neikuri_image(img_bgr)
    return VisionExtractionResponse(
        modality="neikuri",
        quality=result["quality"],
        extracted_features=result["extracted_features"],
        annotated_preview_base64=result["annotated_preview_base64"],
        segmentation_detected=result.get("segmentation_detected", True),
        disclaimer=settings.DISCLAIMER,
    )
