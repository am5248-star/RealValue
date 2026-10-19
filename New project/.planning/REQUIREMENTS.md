# Requirements — Milestone 2: Desktop GUI Demonstration Suite

## Purpose
Provide a standalone, responsive, and visually modern desktop application to demonstrate the pre-trained RealValue Chennai valuation model without modifying model internals.

## Scoped Requirements

### Architecture & Non-Interference
- **REQ-ARCH-01**: Zero changes to existing ML model files (`realvalue/model.py`, `realvalue/pipeline.py`, `artifacts/model.joblib`).
- **REQ-ARCH-02**: UI executes as a standalone Python desktop application (`python -m realvalue.gui` or `python run_gui.py`).
- **REQ-ARCH-03**: The UI consumes `ValuationService(model, historical_df)` directly and handles loading gracefully.

### User Interface & Layout
- **REQ-UI-01**: Built with `CustomTkinter` featuring a dark mode palette, structured two-column layout, and clean typography.
- **REQ-UI-02**: Property Input Form covering all essential parameters:
  - Locality (`AREA` dropdown: Karapakkam, Adyar, Chrompet, Velachery, KK Nagar, Anna Nagar, T Nagar)
  - Built-up area (`INT_SQFT` slider / numeric entry)
  - Layout (`N_BEDROOM`, `N_BATHROOM`, `N_ROOM`)
  - Property attributes (`BUILDTYPE`, `SALE_COND`, `PARK_FACIL`, `UTILITY_AVAIL`, `STREET`, `MZZONE`)
  - Quality scores (`QS_ROOMS`, `QS_BATHROOM`, `QS_BEDROOM`, `QS_OVERALL`)
  - Dates (`DATE_SALE`, `DATE_BUILD`) for automatic property age calculation
- **REQ-UI-03**: Real-time Valuation Output:
  - Prominent valuation estimate in INR (with formatted Lakhs / Crores string, e.g. `₹74.93 Lakhs`)
  - 90% Conformal Prediction Interval (e.g. `₹71.76 L – ₹78.10 L`)
  - Confidence / Review Badge (Green "Standard" vs Amber "Under Review" with clear reasons if abstained)
- **REQ-UI-04**: TreeSHAP Explainability Visualization:
  - Embedded chart showing positive and negative price drivers for the specific prediction.
  - Formatted feature contribution amounts in INR.
- **REQ-UI-05**: Comparable Transactions Explorer:
  - Scrollable view of top 5 comparable properties from historical sales data.
  - Displays property ID, locality, sqft, transaction sale price, price/sqft, and similarity score.
- **REQ-UI-06**: One-Click Demo Presets:
  - Instant loading presets: "Luxury Anna Nagar Villa", "Karapakkam Mid-tier Commercial", "Chrompet Budget Flat", and "Outlier / Review Warning Edge Case".
- **REQ-UI-07**: Model Diagnostics & Metrics Hub:
  - Dedicated tab or view summarizing test MAE (₹1.51L), MAPE (1.22%), split dates, and comparative performance against Random Forest, Ridge, and training median baseline.
