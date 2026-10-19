# Phase 4: Valuation Calculator & Trust Display Components — Plan

## Goal
Build the interactive property parameter input form and the prominent valuation results banner with 90% conformal prediction interval, confidence status badge, and benchmark consistency metrics.

## Context & Constraints
- The UI must not modify `realvalue/model.py` or `realvalue/pipeline.py`.
- Form inputs must correspond to the model features (`NUMERIC` and `CATEGORICAL`).
- Prices must be clearly formatted in Indian currency format (₹ Lakhs and Crores with full rupee precision).

---

## Tasks

### Task 1: Valuation Calculator Input Form (`realvalue/gui_components.py`)
- **Action:** Create `PropertyInputForm` in `realvalue/gui_components.py`.
- **Inputs:**
  - Locality (`AREA` dropdown: Karapakkam, Adyar, Chrompet, Velachery, KK Nagar, Anna Nagar, T Nagar)
  - Built-up area (`INT_SQFT` entry + slider, range 300 - 3000 sqft)
  - Rooms (`N_BEDROOM` 1-4, `N_BATHROOM` 1-3, `N_ROOM` 2-6)
  - Build Type (`BUILDTYPE`: House, Commercial, Others)
  - Parking (`PARK_FACIL`: Yes, No)
  - Municipal Zone (`MZZONE`: RL, RM, RH, A, C, I)
  - Sale Condition & Street (`SALE_COND`, `STREET`)
  - Quality Scores (`QS_OVERALL`, `QS_ROOMS`, etc.)
  - Build Year / Sale Year (calculating `HOUSE_AGE`)
- **Controls:**
  - "Estimate Valuation" primary CTA button
  - "Reset Defaults" button
- **Output:** `get_values() -> dict` matching `ValuationService` request schema.

### Task 2: Valuation Results & Trust Badge Banner (`realvalue/gui_components.py`)
- **Action:** Create `ValuationResultBanner` in `realvalue/gui_components.py`.
- **Displays:**
  - Main estimated price in bold typography (e.g. `₹74.93 Lakhs`)
  - 90% Conformal Prediction Interval card: `[ ₹71.76 L  —  ₹78.10 L ] (±₹3.17 Lakhs margin)`
  - Trust / Review Badge:
    - Green "Standard Confidence" badge if `abstained == False`
    - Amber/Red "Under Review / Caution" badge if `abstained == True`
  - Warning banner detailing active review reasons if any.
  - Locality Benchmark box: Locality median price/sqft, expected benchmark value, and ratio.

### Task 3: Assemble into Valuation Studio (`realvalue/gui_app.py`)
- **Action:** Integrate `PropertyInputForm` and `ValuationResultBanner` into `RealValueApp`.
- **Workflow:**
  - On launch, when engine loads, automatically run default valuation to show initial result.
  - Clicking "Estimate Valuation" runs prediction and smoothly updates the results banner.

### Task 4: Automated Verification
- **Action:** Write headless integration tests in `tests/test_valuation_form.py`.
- **Checks:** Verify form serialization, prediction pipeline trigger, and results rendering.
