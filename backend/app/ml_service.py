"""
Machine Learning Service
------------------------
Manages trained scikit-learn / XGBoost pipeline, SHAP tree explainers,
and local per-sample attribution calculations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import joblib
import numpy as np
import pandas as pd

from app.config import settings

logger = logging.getLogger(__name__)

# Check SHAP availability
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


class MLInferenceService:
    def __init__(self):
        self.bundle: Optional[Dict[str, Any]] = None
        self.pipeline: Any = None
        self.target_encoder: Any = None
        self.metadata: Dict[str, Any] = {}
        self.all_features: list = []
        self.transformed_features: list = []
        self.explainer: Any = None
        self.is_loaded: bool = False
        self._load_model()

    def _load_model(self):
        bundle_path = Path(settings.ML_MODEL_PATH)
        if not bundle_path.exists():
            logger.warning(f"Model bundle not found at {bundle_path}. Inference service running uninitialized.")
            return

        try:
            logger.info(f"Loading ML bundle from {bundle_path}...")
            self.bundle = joblib.load(bundle_path)
            self.pipeline = self.bundle["pipeline"]
            self.target_encoder = self.bundle["target_encoder"]
            self.metadata = self.bundle.get("metadata", {})
            self.all_features = self.bundle["all_features"]
            self.transformed_features = self.bundle["transformed_features"]

            # Initialize SHAP explainer (TreeExplainer for tree models, LinearExplainer for linear)
            if SHAP_AVAILABLE:
                classifier = self.pipeline.named_steps["classifier"]
                if hasattr(classifier, "feature_importances_"):
                    self.explainer = shap.TreeExplainer(classifier)
                    logger.info("SHAP TreeExplainer initialized successfully.")
                elif hasattr(classifier, "coef_"):
                    # For Linear models (LogisticRegression), initialize LinearExplainer with background sample
                    preprocessor = self.pipeline.named_steps["preprocessor"]
                    # Create zero background representation or fit masker
                    self.explainer = shap.LinearExplainer(classifier, masker=shap.maskers.Independent(np.zeros((1, len(self.transformed_features)))))
                    logger.info("SHAP LinearExplainer initialized successfully.")
                else:
                    self.explainer = None

            self.is_loaded = True
            logger.info(f"Model loaded successfully. Version: {self.metadata.get('version', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to load model bundle: {e}", exc_info=True)
            self.is_loaded = False

    def predict(self, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Runs model prediction and generates per-feature local explainability scores."""
        if not self.is_loaded:
            raise RuntimeError("ML model is not loaded. Please ensure train_model.py has been executed.")

        # Construct single-row DataFrame with strict column order
        row = {col: feature_dict.get(col, 0) for col in self.all_features}
        df_row = pd.DataFrame([row])[self.all_features]

        # Pipeline handles ColumnTransformer (scaling numericals + one-hot encoding categoricals)
        pred_idx = int(self.pipeline.predict(df_row)[0])
        probas = self.pipeline.predict_proba(df_row)[0]
        risk_label = str(self.target_encoder.inverse_transform([pred_idx])[0])
        confidence = float(np.max(probas))

        # Class probabilities mapping
        class_probs = {
            str(cls): round(float(p), 4)
            for cls, p in zip(self.target_encoder.classes_, probas)
        }

        # Model Global Feature Importances
        classifier = self.pipeline.named_steps["classifier"]
        if hasattr(classifier, "feature_importances_"):
            importances = classifier.feature_importances_
        elif hasattr(classifier, "coef_"):
            importances = np.mean(np.abs(classifier.coef_), axis=0)
            # Normalize to sum to 1.0 for consistency
            total = np.sum(importances)
            if total > 0:
                importances = importances / total
        else:
            importances = np.ones(len(self.transformed_features)) / len(self.transformed_features)

        imp_series = pd.Series(importances, index=self.transformed_features)
        top_importances = imp_series.sort_values(ascending=False).head(8).round(4).to_dict()

        # Local SHAP contributions for this specific prediction
        shap_contributions = None
        if SHAP_AVAILABLE and self.explainer is not None:
            try:
                preprocessor = self.pipeline.named_steps["preprocessor"]
                x_transformed = preprocessor.transform(df_row)
                shap_vals = self.explainer.shap_values(x_transformed)

                # Format SHAP values: list of arrays (one per class) or 3D array
                if isinstance(shap_vals, list):
                    contrib = shap_vals[pred_idx][0]
                else:
                    sv = np.asarray(shap_vals)
                    if sv.ndim == 3:
                        contrib = sv[0, :, pred_idx]
                    else:
                        contrib = sv[0]

                contrib_series = pd.Series(contrib, index=self.transformed_features)
                shap_contributions = (
                    contrib_series.sort_values(key=lambda s: s.abs(), ascending=False)
                    .head(8)
                    .round(4)
                    .to_dict()
                )
            except Exception as e:
                logger.warning(f"Could not compute local SHAP values: {e}")
                shap_contributions = None

        return {
            "prototype_risk": risk_label,
            "confidence": round(confidence, 4),
            "class_probabilities": class_probs,
            "top_feature_importances": top_importances,
            "shap_contributions": shap_contributions,
            "shap_available": SHAP_AVAILABLE and shap_contributions is not None,
        }


# Singleton service instance
ml_service = MLInferenceService()
