# RealValue AI — Project Specification & History

## Overview
RealValue AI is an explainable, trust-aware property valuation engine for the Chennai real estate market. It combines machine learning with conformal prediction intervals, TreeSHAP feature attributions, locality benchmarks, and historical comparable retrieval to deliver transparent valuations.

## Milestone History

### Milestone 1: ML Backend MVP (Completed)
- **Goal:** Build an end-to-end, leakage-safe tabular valuation pipeline, benchmark candidate models, and implement a trust layer without UI dependencies.
- **Key Deliverables:**
  - Leakage-safe dataset ingestion and validation (`realvalue/pipeline.py`)
  - Chronological 70/15/15 train/calibration/test temporal split
  - Candidate models trained and evaluated: Ridge, Random Forest, XGBoost
  - XGBoost serving model bundle with MAE ₹151,739 (1.22% MAPE) and 90% conformal residual intervals (`artifacts/model.joblib`, `artifacts/metrics.json`)
  - Trust layer: TreeSHAP local attributions, historical comparable sales retrieval, locality price-per-sqft benchmarks, and conservative review/abstention rules
  - CLI commands (`profile`, `train`, `value`, `batch`)

### Milestone 2: Desktop GUI Demonstration Suite (Current)
- **Goal:** Build a desktop GUI application (using CustomTkinter) on top of the existing `ValuationService` and `model.joblib` bundle so stakeholders can interact with and test the model in real time.
- **Strict Boundary:** The ML model (`realvalue/model.py`, `realvalue/pipeline.py`, `artifacts/model.joblib`) remains untouched. The UI strictly consumes the existing `ValuationService.value(...)` API.
- **Core Capabilities:**
  - Interactive property valuation calculator (all property attributes)
  - 90% conformal interval and confidence/review badge
  - TreeSHAP feature attributions visualization
  - Top 5 comparable sales cards with similarity scores
  - Preloaded one-click demo presets (Luxury, Budget, Commercial, Review Trigger)
  - Model diagnostics & benchmark comparison tab (XGBoost vs RF vs Ridge vs Baseline)
