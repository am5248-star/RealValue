# Phase 3: GUI Core Framework & Integration Adapter — Plan

## Goal
Establish the desktop GUI application architecture using CustomTkinter and create a thread-safe, non-blocking adapter over `ValuationService` that loads `artifacts/model.joblib` and `data/Chennai houseing sale.csv` without modifying existing ML model code.

## Context & Boundary
- **Input:** Existing backend artifacts (`artifacts/model.joblib`, `artifacts/metrics.json`, `data/Chennai houseing sale.csv`, `realvalue/service.py`).
- **Constraint:** Zero modifications to `realvalue/model.py`, `realvalue/pipeline.py`, or existing training scripts.
- **Output:** `realvalue/gui_adapter.py`, `realvalue/gui_app.py`, `run_gui.py`, and verification suite.

---

## Tasks

### Task 1: Integration Adapter (`realvalue/gui_adapter.py`)
- **Action:** Create `realvalue/gui_adapter.py` wrapping `ValuationService`.
- **Details:**
  - Auto-discover default model path (`artifacts/model.joblib`) and dataset path (`data/Chennai houseing sale.csv` with fallback to `REALVALUE_DATA` / download paths).
  - Provide `ModelAdapter` class:
    - `load_sync()` and `load_async(callback)` for non-blocking UI startup.
    - `predict(request_dict)` invoking `ValuationService.value(...)`.
    - `get_localities()` returning sorted unique locality names from the model and dataset.
    - `get_metrics()` loading summary statistics from `artifacts/metrics.json`.
    - `get_default_property()` providing standard median/mode property defaults for form initialization.
- **Verification:** Unit test verifying sync and async loading, prediction return schema, and error handling for missing files.

### Task 2: CustomTkinter Base Shell & Responsive Layout (`realvalue/gui_app.py` & `run_gui.py`)
- **Action:** Create the main application window and shell.
- **Details:**
  - Set dark appearance mode and custom theme styling.
  - Header with app title, subtitle ("Explainable Chennai Property Valuation"), model version badge, and async engine status indicator.
  - Navigation tabview:
    - Tab 1: **Valuation Studio** (divided into left Input Panel frame and right Intelligence/Results frame).
    - Tab 2: **Model Diagnostics** (prepared for Phase 6 metrics hub).
  - Responsive layout with minimum window size (1100x750) and auto-scaling grid weights.
  - Bottom status bar displaying loaded model bundle, training cutoff date, and dataset sample count.
  - Create root runner script `run_gui.py` and `__main__` entrypoint.
- **Verification:** Script initializes window, binds background loading, updates status label upon load completion, and handles graceful close.

### Task 3: Headless Verification Test
- **Action:** Write headless automated test `tests/test_gui_adapter.py`.
- **Details:**
  - Validate adapter initialization with real `model.joblib` and `Chennai houseing sale.csv`.
  - Validate that `predict()` returns valid price, conformal interval, confidence flag, TreeSHAP explanation, and comparables list.
  - Verify no exceptions occur in background thread.
- **Verification:** Run `python -m unittest tests/test_gui_adapter.py` and pass with 0 errors.

---

## Acceptance Criteria
1. `realvalue/gui_adapter.py` successfully loads `model.joblib` and `data/Chennai houseing sale.csv` without modifying any files in `realvalue/model.py` or `realvalue/pipeline.py`.
2. UI launches via `python run_gui.py` and asynchronously loads model artifacts without freezing the window.
3. Status indicator updates from "Loading Engine..." to "Engine Ready (xgboost-mvp-2)" upon completion.
4. Shell contains structured layout frames ready for Phase 4 calculator inputs and Phase 5 visualization panels.
