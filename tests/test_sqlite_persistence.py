"""
Explicit SQLite Persistence Verification Test
----------------------------------------------
Verifies that patient analysis records, observations, and prediction metadata
are persistently stored on disk in SQLite, surviving database disconnection,
engine disposal, and application restarts.
"""

import os
import json
import tempfile
from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import AnalysisRecord


def test_sqlite_persistence_across_engine_disposal_and_restart():
    """
    1. Writes an analysis record to an explicit SQLite disk file.
    2. Completely tears down the database connection and disposes the engine.
    3. Reopens a new connection/session to the exact same file.
    4. Asserts that all data, serialized JSON fields, and metadata persisted intact.
    """
    # Create a temporary SQLite database file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        temp_db_path = tmp.name

    try:
        db_url = f"sqlite:///{temp_db_path}"

        # ── Step 1: Initial Engine & Session ───────────────────────
        engine1 = create_engine(db_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine1)
        Session1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
        session1 = Session1()

        test_patient_id = "RPT-PERSIST-TEST-99"
        obs_list = ["High foam coverage observed", "Turbid sample detected"]
        flags_dict = {"high_foam": True, "turbid_sample": True}
        probs_dict = {"Low": 0.12, "Moderate": 0.28, "High": 0.60}
        inputs_dict = {"age": 52, "gender": "Female", "urine_color": "Dark Amber"}

        record = AnalysisRecord(
            patient_id=test_patient_id,
            created_at=datetime.now(timezone.utc),
            age=52,
            gender="Female",
            predominant_humor="Pitham",
            prototype_risk="High",
            confidence=0.60,
            class_probabilities_json=json.dumps(probs_dict),
            digitized_observations_json=json.dumps(obs_list),
            rule_flags_json=json.dumps(flags_dict),
            top_feature_importances_json=json.dumps({"foam_percentage": 0.35}),
            shap_contributions_json=json.dumps({"foam_percentage": 0.45}),
            input_summary_json=json.dumps(inputs_dict),
            vision_metadata_json=None,
        )

        session1.add(record)
        session1.commit()
        session1.close()

        # ── Step 2: Complete Disconnection / Engine Disposal ───────
        # Simulate full server termination: dispose connection pool & engine
        engine1.dispose()
        del session1
        del engine1

        # ── Step 3: Reconnect with Brand New Engine & Session ───────
        engine2 = create_engine(db_url, connect_args={"check_same_thread": False})
        Session2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)
        session2 = Session2()

        # Query the persisted record
        persisted = session2.query(AnalysisRecord).filter(
            AnalysisRecord.patient_id == test_patient_id
        ).first()

        # ── Step 4: Verification Asserts ───────────────────────────
        assert persisted is not None, "Record was not persisted to disk across engine restart!"
        assert persisted.patient_id == test_patient_id
        assert persisted.age == 52
        assert persisted.gender == "Female"
        assert persisted.predominant_humor == "Pitham"
        assert persisted.prototype_risk == "High"
        assert persisted.confidence == pytest.approx(0.60)

        # Verify JSON deserialization matches exact inputs
        assert json.loads(persisted.digitized_observations_json) == obs_list
        assert json.loads(persisted.rule_flags_json) == flags_dict
        assert json.loads(persisted.class_probabilities_json) == probs_dict
        assert json.loads(persisted.input_summary_json) == inputs_dict

        # Verify to_dict() method on persisted model
        d = persisted.to_dict()
        assert d["patient_id"] == test_patient_id
        assert d["digitized_observations"] == obs_list
        assert d["shap_available"] is True

        session2.close()
        engine2.dispose()

    finally:
        # Clean up temporary database file
        if os.path.exists(temp_db_path):
            try:
                os.remove(temp_db_path)
            except PermissionError:
                pass
