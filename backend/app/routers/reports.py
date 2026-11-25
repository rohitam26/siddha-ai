"""
Reports Router
--------------
Historical analysis retrieval, listing, filtering, and deletion.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.config import settings
from app.database import get_db
from app.models import AnalysisRecord
from app.schemas import PredictionResponse

router = APIRouter(prefix="/reports", tags=["Reports & History"])


@router.get("", response_model=List[PredictionResponse])
def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    risk_filter: Optional[str] = Query(None, description="Filter by risk category (Low, Moderate, High)"),
    db: Session = Depends(get_db),
):
    """Retrieves paginated historical analysis reports from persistent SQLite storage."""
    query = db.query(AnalysisRecord)
    if risk_filter:
        query = query.filter(AnalysisRecord.prototype_risk == risk_filter)

    records = query.order_by(desc(AnalysisRecord.created_at)).offset(skip).limit(limit).all()

    results = []
    for r in records:
        d = r.to_dict()
        d["disclaimer"] = settings.DISCLAIMER
        results.append(PredictionResponse(**d))
    return results


@router.get("/{patient_id}", response_model=PredictionResponse)
def get_report_by_id(patient_id: str, db: Session = Depends(get_db)):
    """Fetches a specific structured report by patient/report ID."""
    record = db.query(AnalysisRecord).filter(AnalysisRecord.patient_id == patient_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Report with ID '{patient_id}' not found.")

    d = record.to_dict()
    d["disclaimer"] = settings.DISCLAIMER
    return PredictionResponse(**d)


@router.delete("/{patient_id}")
def delete_report(patient_id: str, db: Session = Depends(get_db)):
    """Deletes an analysis report from the database."""
    record = db.query(AnalysisRecord).filter(AnalysisRecord.patient_id == patient_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Report with ID '{patient_id}' not found.")

    db.delete(record)
    db.commit()
    return {"message": f"Report '{patient_id}' deleted successfully."}
