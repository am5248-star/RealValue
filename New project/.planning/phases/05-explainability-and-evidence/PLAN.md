# Phase 5: TreeSHAP Visualizer & Comparable Sales Explorer — Plan

## Goal
Build rich visual inspection components for model reasoning (TreeSHAP feature attribution bar chart embedded via Matplotlib) and historical evidence (scrollable cards of top 5 comparable sales) in the RealValue desktop application.

## Context & Constraints
- The UI strictly consumes the outputs of `ValuationService`: `explanation` and `comparables`.
- Zero changes to `realvalue/model.py` or `realvalue/pipeline.py`.
- Visualizations must match the dark mode theme and provide clear monetary labels in Indian Rupees (₹ Lakhs).

---

## Tasks

### Task 1: TreeSHAP Feature Attributions Visualizer (`realvalue/gui_evidence.py`)
- **Action:** Create `TreeSHAPVisualizer` using Matplotlib's `FigureCanvasTkAgg`.
- **Details:**
  - Embedded canvas styled to match dark theme (`#141720` background).
  - Horizontal bar chart plotting the top positive and negative feature contributions.
  - Green bars (`#10B981`) for factors increasing the estimated value, red/coral (`#F43F5E`) for factors decreasing it.
  - Clean feature labels (e.g., transforming raw dummy column names like `BUILDTYPE_Commercial` -> `Commercial Building Type`, `AREA_Karapakkam` -> `Locality: Karapakkam`, `INT_SQFT` -> `Built-up Area`).
  - Axis formatted in ₹ Lakhs (`+₹20.6 L`, `-₹19.4 L`).
  - Re-render dynamically whenever a new valuation is computed.

### Task 2: Comparable Transactions Explorer (`realvalue/gui_evidence.py`)
- **Action:** Create `ComparablesExplorer` scrollable container.
- **Details:**
  - Displays top 5 nearest historical sales retrieved by `ValuationService`.
  - Individual property cards showing:
    - Header: Property ID (`PRT_ID`), locality badge, and similarity rank / score.
    - Transaction metrics: Sale price in ₹ Lakhs / Crores, floor area in sqft, and price per sqft.
  - Graceful handling of empty or low comparable counts with a helpful indicator.

### Task 3: Integrate Evidence Explorer into Valuation Studio (`realvalue/gui_app.py`)
- **Action:** Integrate `TreeSHAPVisualizer` and `ComparablesExplorer` into `RealValueApp`.
- **Details:**
  - Add segmented control toggle: `["🧠 TreeSHAP Drivers", "🏘️ Comparable Sales (5)"]` in the results panel.
  - Connect `display_result()` to update both views automatically when a new prediction arrives.

### Task 4: Automated Verification
- **Action:** Write headless integration tests in `tests/test_evidence_components.py`.
- **Checks:**
  - Verify TreeSHAP plot rendering with real feature contributions without throwing Tkinter/Matplotlib exceptions.
  - Verify comparable property cards creation from model output.
  - Verify tab switching and update synchronization.
