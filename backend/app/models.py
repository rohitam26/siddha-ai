"""
SQLAlchemy Database Models
--------------------------
Persistent storage for patient analysis records and reports.
"""

from datetime import datetime, timezone
import json
from sqlalchemy import Column, String, Integer, Float, Text, DateTime
from app.database import Base


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(String(64), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Patient Demographic & Humor
    age = Column(Integer, nullable=False)
    gender = Column(String(16), nullable=False)
    predominant_humor = Column(String(32), nullable=False)

    # ML Prediction Outcome
    prototype_risk = Column(String(32), nullable=False)
    confidence = Column(Float, nullable=False)

    # Serialized JSON fields
    class_probabilities_json = Column(Text, nullable=False)
    digitized_observations_json = Column(Text, nullable=False)
    rule_flags_json = Column(Text, nullable=False)
    top_feature_importances_json = Column(Text, nullable=False)
    shap_contributions_json = Column(Text, nullable=True)
    input_summary_json = Column(Text, nullable=False)
    vision_metadata_json = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "timestamp": self.created_at.isoformat() if self.created_at else None,
            "predominant_humor_input": self.predominant_humor,
            "digitized_observations": json.loads(self.digitized_observations_json),
            "rule_flags": json.loads(self.rule_flags_json),
            "prototype_risk": self.prototype_risk,
            "confidence": self.confidence,
            "class_probabilities": json.loads(self.class_probabilities_json),
            "top_feature_importances": json.loads(self.top_feature_importances_json),
            "shap_contributions": json.loads(self.shap_contributions_json) if self.shap_contributions_json else None,
            "shap_available": self.shap_contributions_json is not None,
            "input_summary": json.loads(self.input_summary_json),
            "vision_metadata": json.loads(self.vision_metadata_json) if self.vision_metadata_json else None,
        }
