"""
Siddha AI - Machine Learning Pipeline
------------------------------------
Trains and benchmarks multiple classifiers (Random Forest, XGBoost, Logistic Regression)
on the Siddha physical examination dataset (synthetic prototype data).

Features:
- Rigorous preprocessing via scikit-learn ColumnTransformer (leakage-free)
- Stratified Train-Test Split (80/20) + 5-Fold Stratified Cross-Validation
- Multi-model evaluation: Accuracy, Balanced Accuracy, Macro F1, Precision, Recall, ROC-AUC
- Hyperparameter tuning via GridSearchCV
- SHAP-based local and global model explainability
- Model serialization with full metadata, schema validation, and versioning

DISCLAIMER:
This pipeline is an academic engineering demonstration trained on synthetic data.
It does NOT provide clinical diagnostic claims or validate real-world efficacy.
"""

import os
import sys
import json
import hashlib
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple

import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
import xgboost as xgb
import shap

# Feature Definitions
NUMERICAL_FEATURES = [
    "age",
    "HSV_H",
    "HSV_S",
    "HSV_V",
    "transparency_score",
    "foam_percentage",
    "foam_bubble_count",
    "sediment_percentage",
    "odor_score",
    "oil_spread_diameter_mm",
    "oil_spread_speed",
    "branch_count",
    "circularity",
    "symmetry_score",
    "edge_roughness",
    "fractal_dimension",
    "vatham_score",
    "pitham_score",
    "kabham_score",
]

CATEGORICAL_FEATURES = [
    "gender",
    "urine_color",
    "oil_shape",
    "predominant_humor",
]

ALL_FEATURE_COLUMNS = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
TARGET_COLUMN = "prototype_risk"
DISCLAIMER_TEXT = (
    "This ML model is trained on synthetic Siddha diagnostic parameter data for academic "
    "and prototype demonstration. It is NOT validated for clinical diagnosis or treatment."
)


def compute_file_hash(filepath: Path) -> str:
    """Compute SHA256 hash of the dataset for provenance tracking."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()[:16]


def create_preprocessor() -> ColumnTransformer:
    """Build a leakage-free ColumnTransformer pipeline."""
    num_transformer = Pipeline(steps=[
        ("scaler", StandardScaler()),
    ])
    cat_transformer = Pipeline(steps=[
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, NUMERICAL_FEATURES),
            ("cat", cat_transformer, CATEGORICAL_FEATURES),
        ]
    )
    return preprocessor


def evaluate_model_cv(
    pipeline: Pipeline, X_train: pd.DataFrame, y_train: np.ndarray, cv_folds: int = 5
) -> Dict[str, float]:
    """Run Stratified K-Fold cross validation and record metrics."""
    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
    scores = {"accuracy": [], "balanced_accuracy": [], "f1_macro": []}

    for fold, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train)):
        X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train[train_idx], y_train[val_idx]

        pipeline.fit(X_tr, y_tr)
        preds = pipeline.predict(X_val)

        scores["accuracy"].append(accuracy_score(y_val, preds))
        scores["balanced_accuracy"].append(balanced_accuracy_score(y_val, preds))
        scores["f1_macro"].append(f1_score(y_val, preds, average="macro"))

    return {
        "cv_accuracy_mean": float(np.mean(scores["accuracy"])),
        "cv_accuracy_std": float(np.std(scores["accuracy"])),
        "cv_balanced_acc_mean": float(np.mean(scores["balanced_accuracy"])),
        "cv_f1_macro_mean": float(np.mean(scores["f1_macro"])),
        "cv_f1_macro_std": float(np.std(scores["f1_macro"])),
    }


def train_and_benchmark(
    data_path: Path, output_dir: Path, tune: bool = True, model_choice: str = "auto"
) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = output_dir / "plots"
    plots_dir.mkdir(exist_ok=True)

    print(f"[*] Loading dataset from {data_path}...")
    df = pd.read_csv(data_path)
    data_hash = compute_file_hash(data_path)
    print(f"[*] Dataset shape: {df.shape}, SHA256: {data_hash}")

    # Validate required columns
    missing_cols = set(ALL_FEATURE_COLUMNS + [TARGET_COLUMN]) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns in dataset: {missing_cols}")

    X = df[ALL_FEATURE_COLUMNS]
    y_raw = df[TARGET_COLUMN]

    # Target Encoding
    target_encoder = LabelEncoder()
    # Ensure ordered classes: Low, Moderate, High if present
    target_classes_order = ["Low", "Moderate", "High"]
    target_encoder.fit(target_classes_order)
    y = target_encoder.transform(y_raw)
    classes = target_encoder.classes_.tolist()

    # Stratified Train-Test Split (80 / 20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"[*] Train set: {X_train.shape[0]} samples, Test set: {X_test.shape[0]} samples")

    # Candidate Models definition
    candidate_pipelines = {
        "LogisticRegression": Pipeline([
            ("preprocessor", create_preprocessor()),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
        ]),
        "RandomForest": Pipeline([
            ("preprocessor", create_preprocessor()),
            ("classifier", RandomForestClassifier(n_estimators=300, max_depth=8, class_weight="balanced", random_state=42)),
        ]),
        "XGBoost": Pipeline([
            ("preprocessor", create_preprocessor()),
            ("classifier", xgb.XGBClassifier(
                n_estimators=200,
                max_depth=4,
                learning_rate=0.05,
                eval_metric="mlogloss",
                random_state=42,
            )),
        ]),
    }

    print("\n" + "=" * 60)
    print("[*] STEP 1: Cross-Validation Benchmarking on Training Set")
    print("=" * 60)

    comparison_results = {}
    for name, pipe in candidate_pipelines.items():
        print(f"  -> Evaluating {name} via 5-Fold Stratified CV...")
        cv_metrics = evaluate_model_cv(pipe, X_train, y_train, cv_folds=5)
        comparison_results[name] = cv_metrics
        print(
            f"     CV Accuracy: {cv_metrics['cv_accuracy_mean']:.3f} +/- {cv_metrics['cv_accuracy_std']:.3f} | "
            f"CV Macro F1: {cv_metrics['cv_f1_macro_mean']:.3f}"
        )

    # Model Selection Strategy
    if model_choice == "auto":
        # Select best model based on cross-validation macro F1
        best_model_name = max(comparison_results, key=lambda k: comparison_results[k]["cv_f1_macro_mean"])
        selection_rationale = (
            f"Automatically selected '{best_model_name}' because it achieved the highest 5-fold CV Macro F1 "
            f"({comparison_results[best_model_name]['cv_f1_macro_mean']:.3f}). In synthetic benchmarking, "
            f"the underlying data generation formula is predominantly an additive linear risk function, "
            f"enabling regularized linear models to generalize with high precision."
        )
    else:
        best_model_name = model_choice
        selection_rationale = f"Manually pinned model choice: '{best_model_name}'."

    print(f"\n[*] Model Selection: {best_model_name}")
    print(f"[*] Rationale: {selection_rationale}")

    final_pipeline = candidate_pipelines[best_model_name]
    tuned_params = {}

    if tune and best_model_name == "RandomForest":
        print("\n" + "=" * 60)
        print(f"[*] STEP 2: Hyperparameter Optimization for {best_model_name}")
        print("=" * 60)
        param_grid = {
            "classifier__n_estimators": [150, 250, 350],
            "classifier__max_depth": [6, 8, 12, None],
            "classifier__min_samples_split": [2, 5],
            "classifier__min_samples_leaf": [1, 2],
        }
        grid_search = GridSearchCV(
            final_pipeline,
            param_grid=param_grid,
            cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
            scoring="f1_macro",
            n_jobs=-1,
        )
        grid_search.fit(X_train, y_train)
        print(f"  -> Best Hyperparameters: {grid_search.best_params_}")
        print(f"  -> Best CV Macro F1: {grid_search.best_score_:.3f}")
        final_pipeline = grid_search.best_estimator_
        tuned_params = grid_search.best_params_
    elif tune and best_model_name == "LogisticRegression":
        print("\n" + "=" * 60)
        print(f"[*] STEP 2: Hyperparameter Optimization for {best_model_name}")
        print("=" * 60)
        param_grid = {
            "classifier__C": [0.01, 0.1, 1.0, 5.0, 10.0],
            "classifier__penalty": ["l2"],
            "classifier__solver": ["lbfgs"],
        }
        grid_search = GridSearchCV(
            final_pipeline,
            param_grid=param_grid,
            cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
            scoring="f1_macro",
            n_jobs=-1,
        )
        grid_search.fit(X_train, y_train)
        print(f"  -> Best Hyperparameters: {grid_search.best_params_}")
        print(f"  -> Best CV Macro F1: {grid_search.best_score_:.3f}")
        final_pipeline = grid_search.best_estimator_
        tuned_params = grid_search.best_params_
    else:
        final_pipeline.fit(X_train, y_train)
        tuned_params = {"default": True}

    print("\n" + "=" * 60)
    print("[*] STEP 3: Evaluating Best Model on Held-Out Test Set")
    print("=" * 60)

    # Train final model on full train split
    final_pipeline.fit(X_train, y_train)

    y_pred = final_pipeline.predict(X_test)
    y_proba = final_pipeline.predict_proba(X_test)

    test_accuracy = accuracy_score(y_test, y_pred)
    test_balanced_acc = balanced_accuracy_score(y_test, y_pred)
    test_f1_macro = f1_score(y_test, y_pred, average="macro")
    test_f1_weighted = f1_score(y_test, y_pred, average="weighted")
    test_precision_macro = precision_score(y_test, y_pred, average="macro")
    test_recall_macro = recall_score(y_test, y_pred, average="macro")

    try:
        test_roc_auc = roc_auc_score(y_test, y_proba, multi_class="ovr")
    except Exception:
        test_roc_auc = None

    print(f"  -> Test Accuracy:         {test_accuracy:.4f}")
    print(f"  -> Test Balanced Accuracy: {test_balanced_acc:.4f}")
    print(f"  -> Test Macro F1-Score:    {test_f1_macro:.4f}")
    print(f"  -> Test Macro Precision:   {test_precision_macro:.4f}")
    print(f"  -> Test Macro Recall:      {test_recall_macro:.4f}")
    if test_roc_auc:
        print(f"  -> Test ROC-AUC (OvR):     {test_roc_auc:.4f}")

    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=classes))

    # Confusion Matrix Plot
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=classes,
        yticklabels=classes,
        cbar=False,
    )
    plt.title(f"Confusion Matrix - {best_model_name} (Synthetic Test Set)", fontsize=11)
    plt.xlabel("Predicted Risk Label")
    plt.ylabel("Actual Risk Label")
    plt.tight_layout()
    cm_path = plots_dir / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=180)
    plt.close()

    # Model Comparison Plot
    plt.figure(figsize=(7, 4))
    model_names = list(comparison_results.keys())
    cv_means = [comparison_results[m]["cv_f1_macro_mean"] for m in model_names]
    cv_stds = [comparison_results[m]["cv_f1_macro_std"] for m in model_names]
    colors = ["#7B9E87", "#3F6E52", "#C98A2C"]
    bars = plt.bar(model_names, cv_means, yerr=cv_stds, capsize=5, color=colors, alpha=0.9)
    plt.ylabel("5-Fold CV Macro F1")
    plt.title("Model Comparison: 5-Fold Stratified Cross-Validation")
    plt.ylim(0, 1.0)
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, h + 0.03, f"{h:.3f}", ha="center", va="bottom", fontsize=10)
    plt.tight_layout()
    comp_path = plots_dir / "model_comparison.png"
    plt.savefig(comp_path, dpi=180)
    plt.close()

    # Global Feature Importance
    fitted_preprocessor = final_pipeline.named_steps["preprocessor"]
    fitted_classifier = final_pipeline.named_steps["classifier"]

    # Retrieve transformed feature names
    cat_encoder = fitted_preprocessor.named_transformers_["cat"].named_steps["onehot"]
    transformed_cat_features = list(cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES))
    all_transformed_features = NUMERICAL_FEATURES + transformed_cat_features

    if hasattr(fitted_classifier, "feature_importances_"):
        raw_importances = fitted_classifier.feature_importances_
        imp_title = f"Top 15 Feature Importances (Gini - {best_model_name})"
    elif hasattr(fitted_classifier, "coef_"):
        raw_importances = np.mean(np.abs(fitted_classifier.coef_), axis=0)
        imp_title = f"Top 15 Feature Importances (Mean |Coef| - {best_model_name})"
    else:
        raw_importances = np.ones(len(all_transformed_features)) / len(all_transformed_features)
        imp_title = f"Top 15 Feature Importances ({best_model_name})"

    feat_imp_df = pd.DataFrame({
        "feature": all_transformed_features,
        "importance": raw_importances,
    }).sort_values(by="importance", ascending=False)
    feat_imp_df.to_csv(output_dir / "feature_importance.csv", index=False)

    # Plot top features
    plt.figure(figsize=(8, 5))
    top15 = feat_imp_df.head(15).sort_values(by="importance", ascending=True)
    plt.barh(top15["feature"], top15["importance"], color="#3F6E52")
    plt.title(imp_title)
    plt.xlabel("Importance")
    plt.tight_layout()
    plt.savefig(plots_dir / "feature_importance_top15.png", dpi=180)
    plt.close()

    # SHAP Global Explainability
    print("\n" + "=" * 60)
    print("[*] STEP 4: Computing SHAP Explainability Artifacts")
    print("=" * 60)

    # Transform test set using the fitted preprocessor
    X_test_transformed = fitted_preprocessor.transform(X_test)
    X_train_transformed = fitted_preprocessor.transform(X_train)

    if hasattr(fitted_classifier, "feature_importances_"):
        explainer = shap.TreeExplainer(fitted_classifier)
        shap_values = explainer.shap_values(X_test_transformed)
    elif hasattr(fitted_classifier, "coef_"):
        explainer = shap.LinearExplainer(fitted_classifier, X_train_transformed)
        shap_values = explainer.shap_values(X_test_transformed)
    else:
        explainer = shap.Explainer(fitted_classifier, X_train_transformed)
        shap_values = explainer(X_test_transformed).values

    # Normalize SHAP values across classes to get mean absolute impact
    if isinstance(shap_values, list):
        mean_abs_shap = np.mean([np.abs(sv) for sv in shap_values], axis=0)
    else:
        sv = np.asarray(shap_values)
        if sv.ndim == 3:
            mean_abs_shap = np.mean(np.abs(sv), axis=2)
        else:
            mean_abs_shap = np.abs(sv)

    shap_summary_df = pd.DataFrame(
        mean_abs_shap, columns=all_transformed_features
    ).mean().sort_values(ascending=False).reset_index()
    shap_summary_df.columns = ["feature", "mean_abs_shap"]
    shap_summary_df.to_csv(output_dir / "shap_feature_importance.csv", index=False)

    plt.figure(figsize=(8, 5))
    top_shap = shap_summary_df.head(12).sort_values(by="mean_abs_shap", ascending=True)
    plt.barh(top_shap["feature"], top_shap["mean_abs_shap"], color="#C98A2C")
    plt.title("Global SHAP Importance (Mean |SHAP value| on Test Set)")
    plt.xlabel("Mean |SHAP value|")
    plt.tight_layout()
    plt.savefig(plots_dir / "shap_summary.png", dpi=180)
    plt.close()

    # Model Artifact Metadata
    metadata = {
        "version": "2.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_type": best_model_name,
        "model_selection_rationale": selection_rationale,
        "dataset_hash": data_hash,
        "dataset_rows": len(df),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "target_classes": classes,
        "numerical_features": NUMERICAL_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "all_input_features": ALL_FEATURE_COLUMNS,
        "transformed_feature_names": all_transformed_features,
        "best_hyperparameters": tuned_params,
        "metrics": {
            "test_accuracy": round(test_accuracy, 4),
            "test_balanced_accuracy": round(test_balanced_acc, 4),
            "test_f1_macro": round(test_f1_macro, 4),
            "test_f1_weighted": round(test_f1_weighted, 4),
            "test_precision_macro": round(test_precision_macro, 4),
            "test_recall_macro": round(test_recall_macro, 4),
            "test_roc_auc_ovr": round(test_roc_auc, 4) if test_roc_auc else None,
        },
        "cv_benchmark": comparison_results,
        "model_selection_rationale": selection_rationale,
        "disclaimer": DISCLAIMER_TEXT,
    }

    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Save Bundle Artifacts for Inference
    bundle = {
        "pipeline": final_pipeline,
        "target_encoder": target_encoder,
        "metadata": metadata,
        "all_features": ALL_FEATURE_COLUMNS,
        "transformed_features": all_transformed_features,
    }
    joblib.dump(bundle, output_dir / "model_bundle.joblib")
    # Also save legacy-compatible files for smooth fallback
    joblib.dump(fitted_classifier, output_dir / "model.pkl")
    joblib.dump(ALL_FEATURE_COLUMNS, output_dir / "feature_columns.pkl")

    print("\n" + "=" * 60)
    print(f"[*] Training Complete! Artifacts written to {output_dir}")
    print("=" * 60)
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Siddha AI Model Pipeline")
    parser.add_argument("--data-path", type=str, default="../data/siddha_synthetic_dataset.csv")
    parser.add_argument("--output-dir", type=str, default=".")
    parser.add_argument("--model", type=str, default="auto", choices=["auto", "LogisticRegression", "RandomForest", "XGBoost"], help="Model selection (auto chooses highest CV F1)")
    parser.add_argument("--no-tune", action="store_true", help="Skip hyperparameter grid search")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    resolved_data = (base_dir / args.data_path).resolve()
    resolved_out = (base_dir / args.output_dir).resolve()

    train_and_benchmark(
        data_path=resolved_data,
        output_dir=resolved_out,
        tune=not args.no_tune,
        model_choice=args.model,
    )
