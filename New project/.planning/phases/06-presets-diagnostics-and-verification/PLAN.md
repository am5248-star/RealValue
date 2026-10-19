# Phase 6: Demo Presets, Model Diagnostics Hub & Polish — Plan

## Goal
Add one-click scenario presets for rapid stakeholder demonstration, enrich the Model Diagnostics tab with styled comparison cards, and perform final end-to-end testing and documentation updates.

## Context & Constraints
- Zero changes to ML model code (`realvalue/model.py`, `realvalue/pipeline.py`, `artifacts/model.joblib`).
- Presets must represent diverse market segments (Luxury, Commercial, Budget, Review Outlier).
- App must launch effortlessly with `python run_gui.py`.

---

## Tasks

### Task 1: One-Click Demo Presets (`realvalue/gui_components.py` & `realvalue/gui_app.py`)
- **Action:** Add preset definitions and UI selector bar at top of Property Parameters panel.
- **Presets:**
  1. **Luxury Anna Nagar Villa**: High sqft, prime locality, residential high zone, high quality.
  2. **Commercial Karapakkam Hub**: IT corridor, commercial building type, parking facility.
  3. **Chrompet Budget Flat**: Moderate sqft, normal sale, standard quality.
  4. **Outlier / Review Warning Trigger**: Disproportionate attributes causing ratio or comp deviations to trigger trust layer abstention/review alert.
- **Interaction:** Clicking any preset immediately loads values and triggers live valuation with TreeSHAP and comps refresh.

### Task 2: Styled Model Diagnostics & Benchmarks Hub (`realvalue/gui_app.py`)
- **Action:** Upgrade the "Model Diagnostics & Benchmarks" tab with structured visual cards.
- **Details:**
  - Sample split pills: Train (4,976), Calibration (1,066), Test (1,067).
  - Comparative cards for XGBoost vs Random Forest vs Ridge vs Median Baseline with color-coded MAE, RMSE, and MAPE tags.
  - Conformal Calibration card explaining the ±₹3.17 Lakhs residual quantile radius and 89.0% empirical test coverage.
  - Model limitations & data boundary disclosure.

### Task 3: Documentation Update (`README.md`)
- **Action:** Update root `README.md` with GUI launch instructions, feature tour, and architecture boundary.

### Task 4: Automated Verification
- **Action:** Write `tests/test_presets_and_diagnostics.py` verifying all 4 presets execute and produce valid responses without runtime exceptions.
