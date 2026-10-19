# RealValue AI — Roadmap

## Milestones

- [x] **Milestone 1: ML Backend MVP** (Shipped 2026-10-13)
  - Phase 1: Ingestion, Leakage-Safe Pipeline & Chronological Modeling
  - Phase 2: Trust Intervals, TreeSHAP & Comparable Retrieval
- [ ] **Milestone 2: Desktop GUI Demonstration Suite** (Active)
  - Phase 3: GUI Core Framework & Integration Adapter
  - Phase 4: Valuation Calculator & Trust Display Components
  - Phase 5: TreeSHAP Visualizer & Comparable Sales Explorer
  - Phase 6: Demo Presets, Model Diagnostics Hub & End-to-End Verification

---

## Milestone 2 Phases

### Phase 3: GUI Core Framework & Integration Adapter
- **Goal:** Set up CustomTkinter application shell, async background loader for model and historical data, and state manager.
- **Plans:**
  - Plan 3.1: Data/Model loader adapter (`realvalue/gui_adapter.py` / `gui.py`) connecting to existing `ValuationService` without blocking the UI thread.
  - Plan 3.2: Main CustomTkinter window shell with tabbed navigation ("Property Valuator", "Model Diagnostics & Metrics").

### Phase 4: Valuation Calculator & Trust Display Components
- **Goal:** Build the interactive input form and immediate valuation results header with 90% conformal prediction interval and trust status badge.
- **Plans:**
  - Plan 4.1: Input form widgets for all categorical and numerical features with sensible defaults.
  - Plan 4.2: Results banner displaying formatted INR estimate, conformal confidence interval, and alert box for review reasons.

### Phase 5: TreeSHAP Visualizer & Comparable Sales Explorer
- **Goal:** Build rich visual inspection of model reasoning and nearest historical evidence.
- **Plans:**
  - Plan 5.1: Matplotlib-embedded bar chart displaying TreeSHAP positive and negative feature contributions.
  - Plan 5.2: Scrollable cards displaying top 5 comparable historical transactions with similarity scores.

### Phase 6: Demo Presets, Model Diagnostics Hub & End-to-End Verification
- **Goal:** Add one-click showcase presets, model benchmarking tab, and verify execution end-to-end.
- **Plans:**
  - Plan 6.1: One-click scenario preset buttons for quick stakeholder demonstration.
  - Plan 6.2: Diagnostics tab visualizing metrics from `artifacts/metrics.json` (comparison table and split info).
  - Plan 6.3: Launch verification and documentation update in README.
