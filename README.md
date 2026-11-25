# Siddha AI: Digital Neerkuri & Neikuri Diagnostic Analysis Platform

[![CI Pipeline](https://github.com/your-username/siddha-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/siddha-ai/actions)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Important Academic Disclaimer:**
> **Siddha AI is an academic machine learning engineering prototype developed using synthetic research distributions.**
> It standardizes traditional physical observation methods into measurable parameters for research demonstration and is **not intended for clinical diagnosis, patient management, or medical decision-making.**

---

## 1. Project Overview

In traditional Siddha and Ayurvedic medicine, **Neerkuri** (visual examination of urine: color, optical clarity, sediment, and surface foam) and **Neikuri** (examination of a sesame oil drop placed upon the urine surface: circularity, spreading rate, boundary contour, and branching) serve as classical physical examination techniques.

Historically, these assessments have relied upon subjective manual observation. **Siddha AI** digitizes these modalities through a modern engineering stack:
- **Computer Vision Pipeline:** Automated OpenCV image quality checks (blurriness, exposure, contrast) and geometric contour segmentation (circularity, solidity, convexity defects, edge roughness).
- **Dual-Layer Reasoning:**
  1. *Deterministic Rule Engine:* Transparent, rule-based physical observations without unverified disease assertions.
  2. *Machine Learning Classifier:* Calibrated multi-class model (Random Forest benchmarked against XGBoost and Logistic Regression) with Stratified 5-Fold Cross-Validation.
- **Model Explainability:** Global Gini importance and local per-patient **SHAP (SHapley Additive exPlanations)** values.
- **Full-Stack Architecture:** Modular FastAPI backend, persistent SQLite reporting via SQLAlchemy, and a responsive React 18 dashboard.

---

## 2. System Architecture

```
                                 [ Clinical User / Practitioner ]
                                                 │
                                                 ▼
                                     ┌───────────────────────┐
                                     │   React 18 Dashboard  │
                                     │  (Vite + TailwindCSS) │
                                     └───────────┬───────────┘
                                                 │ REST API Calls
                                                 ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │                              FastAPI Backend Application                               │
 │                                                                                        │
 │   ┌───────────────────────┐   ┌───────────────────────────┐   ┌────────────────────┐   │
 │   │  Vision Router (/v1)  │   │   Analysis Router (/v1)   │   │ Report Router(/v1) │   │
 │   └───────────┬───────────┘   └─────────────┬─────────────┘   └─────────┬──────────┘   │
 │               │                             │                           │              │
 │               ▼                             ▼                           ▼              │
 │   ┌───────────────────────┐   ┌───────────────────────────┐   ┌────────────────────┐   │
 │   │  OpenCV Vision Engine │   │   ML Inference Service    │   │  Persistent SQLite │   │
 │   │  - Laplacian Sharpness│   │   - ColumnTransformer     │   │  Database Storage  │   │
 │   │  - Foam & Bubble Zone │   │   - Random Forest Model   │   │  (SQLAlchemy ORM)  │   │
 │   │  - Contour & Hull Seg │   │   - Local SHAP Explainer  │   │                    │   │
 │   └───────────────────────┘   └─────────────┬─────────────┘   └────────────────────┘   │
 │                                             │                                          │
 │                                             ▼                                          │
 │                               ┌───────────────────────────┐                            │
 │                               │ Deterministic Rule Engine │                            │
 │                               │ (Transparent IF/THEN Obs) │                            │
 │                               └───────────────────────────┘                            │
 └────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Machine Learning Engineering & Methodology

### 3.1 Preprocessing & Leakage Prevention
Feature transformations are packaged in a scikit-learn `ColumnTransformer`:
- **Numerical Features (19 inputs):** Transformed via `StandardScaler`. Scaler parameters are calculated strictly inside training folds to prevent data leakage.
- **Categorical Features (4 inputs):** Encoded with `OneHotEncoder(handle_unknown='ignore')` to ensure zero runtime failure when encountering novel values.

### 3.2 Model Comparison (Stratified 5-Fold Cross-Validation)

| Algorithm Family | 5-Fold CV Accuracy | CV Macro F1 | Status |
| :--- | :---: | :---: | :--- |
| **Random Forest (Tuned)** | **0.747 ± 0.065** | **0.715** | **Selected Final Model** |
| Logistic Regression (L2 Balanced) | 0.778 ± 0.038 | 0.724 | Linear Baseline |
| XGBoost (Multi-Softprob) | 0.760 ± 0.056 | 0.690 | Gradient Boosted Baseline |

### 3.3 Test Set Evaluation (Held-Out 20% Split)
- **Accuracy:** `0.7300`
- **Balanced Accuracy:** `0.6881`
- **Macro F1-Score:** `0.6915`
- **Macro Precision:** `0.6965`
- **Macro Recall:** `0.6881`
- **Multi-Class ROC-AUC (One-vs-Rest):** `0.8899`

---

## 4. Computer Vision Specifications

1. **Quality Assessment (`assess_image_quality`):**
   - Blurriness detection via variance of Laplacian ($T = 75.0$).
   - Mean intensity luminance evaluation for underexposure ($< 45$) and overexposure ($> 220$).
   - RMS contrast evaluation.
2. **Neerkuri Extraction (`analyze_neerkuri_image`):**
   - Median hue extraction in OpenCV HSV color space.
   - Siddha color classification: *Pale Yellow, Yellow, Amber, Dark Amber, Reddish, Brownish*.
   - Optical transparency score via Sobel gradient magnitude.
   - Upper meniscus foam segmentation and connected-component bubble counting.
3. **Neikuri Extraction (`analyze_neikuri_image`):**
   - Otsu adaptive surface thresholding with elliptical morphological opening.
   - Drop circularity metric: $\mathcal{C} = \frac{4 \pi \cdot \text{Area}}{\text{Perimeter}^2}$.
   - Convexity defect depth calculation for radial branching.
   - Solidity calculation ($\frac{\text{Area}}{\text{Hull Area}}$) and edge roughness indexing.
   - Base64 annotated contour overlay for practitioner visual inspection.

---

## 5. Repository Structure

```
siddha_ai/
├── .github/workflows/ci.yml     # Automated GitHub Actions CI pipeline
├── backend/
│   ├── app/
│   │   ├── config.py            # Environment-driven pydantic-settings
│   │   ├── database.py          # SQLAlchemy SQLite connection session
│   │   ├── models.py            # AnalysisRecord ORM table model
│   │   ├── schemas.py           # Pydantic v2 validation contracts
│   │   ├── ml_service.py        # Model loading & SHAP inference engine
│   │   ├── rule_engine.py       # Deterministic observation engine
│   │   └── routers/
│   │       ├── health.py        # /api/v1/health & model metadata
│   │       ├── vision.py        # /api/v1/vision/neerkuri & /neikuri
│   │       ├── analysis.py      # /api/v1/analysis/predict
│   │       └── reports.py       # /api/v1/reports (CRUD & pagination)
│   ├── cv_engine.py             # OpenCV computer vision analyzer
│   └── main.py                  # FastAPI application entrypoint
├── data/
│   ├── generate_dataset.py      # Synthetic distribution generator
│   └── siddha_synthetic_dataset.csv
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── UploadPanel.jsx   # Dual image upload & parameter form
│   │   │   ├── RiskCard.jsx      # Confidence meter & rule observations
│   │   │   ├── FeatureImportanceChart.jsx # SHAP attribution visualizer
│   │   │   ├── PatientReport.jsx # Printable report view & JSON export
│   │   │   ├── ReportsHistory.jsx # SQLite historical table with filters
│   │   │   ├── ModelInsights.jsx # Cross-validation benchmark viewer
│   │   │   └── SettingsView.jsx  # Practitioner & endpoint profile
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── ml/
│   ├── train_model.py           # Reproducible model training pipeline
│   ├── model_bundle.joblib      # Serialized scikit-learn pipeline & encoder
│   ├── metadata.json            # Model lineage, hashes, and metrics
│   └── plots/                   # Confusion matrix, CV comparison, SHAP plots
├── tests/
│   ├── conftest.py
│   ├── test_ml_pipeline.py
│   ├── test_cv_engine.py
│   ├── test_rule_engine.py
│   └── test_api_integration.py
├── Dockerfile                   # Multi-stage production container
├── docker-compose.yml
├── requirements.txt             # Consolidated project dependencies
└── README.md
```

---

## 6. Installation & Execution Guide

### Prerequisites
- Python 3.10–3.12
- Node.js 18+ and npm

### Local Setup

```bash
# 1. Clone repository
git clone https://github.com/your-username/siddha-ai.git
cd siddha-ai

# 2. Setup Python virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run reproducible ML training pipeline (optional: pre-trained bundle is included)
python ml/train_model.py --no-tune

# 5. Run automated test suite
pytest tests/ -v

# 6. Start FastAPI backend server
cd backend
python main.py
# Server runs at http://localhost:8000 (OpenAPI docs at http://localhost:8000/docs)
```

In a separate terminal, start the React frontend:

```bash
cd frontend
npm install
npm run dev
# Dashboard launches at http://localhost:5173
```

### Docker Execution

```bash
docker-compose up --build
```

---

## 7. REST API Documentation

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/v1/health` | `GET` | Health probe reporting database and model readiness. |
| `/api/v1/model/metadata` | `GET` | Feature list, cross-validation metrics, and provenance hash. |
| `/api/v1/vision/neerkuri` | `POST` | Upload urine photo; returns color, turbidity, and foam metrics. |
| `/api/v1/vision/neikuri` | `POST` | Upload oil drop photo; returns contour circularity, roughness, and overlay. |
| `/api/v1/analysis/predict`| `POST` | Generates rule observations, model prediction, and local SHAP values. |
| `/api/v1/reports` | `GET` | Paginated listing of historical patient reports with optional risk filter. |
| `/api/v1/reports/{id}` | `GET` | Retrieve structured report by ID. |
| `/api/v1/reports/{id}` | `DELETE` | Remove report from persistent storage. |

---

## 8. Limitations & Clinical Ethics Notice

1. **Synthetic Data Lineage:** All 500 records in `siddha_synthetic_dataset.csv` are synthetically synthesized based on literature distributions. They do not represent validated patient data from hospital trials.
2. **Computer Vision Constraints:** Current CV feature extraction operates on single static photographic frames without controlled photometric calibration rigs.
3. **No Direct Disease Claims:** The rule engine produces physical observations only (e.g., "high foam detected", "irregular branched oil spread"). It intentionally avoids mapping observations to clinical diseases.

---

## 9. License

This project is licensed under the [MIT License](LICENSE).
