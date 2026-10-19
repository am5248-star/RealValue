# Roadmap status

The notes describe an ambitious layered system. This implementation deliberately ships the non-UI MVP boundary and records which phases need more data or infrastructure.

| Area | Status | Implementation |
|---|---|---|
| Scope and data inventory | Done | Chennai historical sale CSV selected; mismatched sources documented |
| Ingestion and validation | Done | Required schema, parsing, invalid-target/date removal, missingness profile |
| Leakage-safe feature engineering | Done | Fees, commission, ID excluded; age calculated relative to transaction |
| EDA/data audit | Done | Source counts, date range, missingness, target distribution, locality variants |
| Temporal evaluation | Done | Chronological 70/15/15 train/calibration/test split |
| Baseline and main models | Done | Ridge, Random Forest, and XGBoost evaluated on the same chronological split; XGBoost selected for serving |
| Trust layer | MVP | Held-out absolute residual interval, conservative review/abstention rules, locality price/sqft check |
| Explanations and evidence | MVP | Native XGBoost TreeSHAP contributions and locality/attribute comparable retrieval |
| Unified response | Done | `ValuationResponse` data class and JSON form |
| API and batch delivery | Partial | API-ready service boundary and batch CLI; HTTP service not wired |
| Geographic feature enrichment | Deferred | Source lacks coordinates and POI data |
| Market trend evidence | Deferred | Historical periods are available, but trend semantics and reliable locality normalization need review |
| Gradient boosting / multi-task model | Partial | XGBoost is implemented; LightGBM and the optional multi-task deep model remain deferred |
| MAPIE, PostGIS/H3 | Deferred | Current calibration is a small empirical residual method; no coordinates or spatial infrastructure are available |
| Registry, tracking, deployment, UI | Deferred | Beyond requested non-UI MVP; UI explicitly left out |

## Current chronological holdout results

| Model | MAE (INR) | RMSE (INR) | MAPE | 90% interval coverage |
|---|---:|---:|---:|---:|
| Ridge | 690,719 | 921,542 | 5.29% | 89.4% |
| Random Forest | 364,378 | 468,077 | 3.11% | 93.6% |
| XGBoost (serving model) | 151,739 | 215,754 | 1.22% | 89.0% |
| Training median baseline | 3,161,303 | 4,281,174 | — | — |

The results are from the same chronological split: train through 12 Jun 2011, calibration through 22 Mar 2012, and test from 23 Mar 2012 through 17 Feb 2015. This is one historical holdout and is not evidence of present-day Chennai market accuracy.

## Risks to address next

1. Manually reconcile locality aliases using a reviewed mapping.
2. Add grouped/geographic stress tests and locality-stratified error analysis alongside the chronological model comparison.
3. Evaluate interval coverage by time and locality; recalibrate for drift and sparse segments.
4. Validate comparable retrieval and review thresholds with a domain reviewer.
5. Add real coordinates and licensed POI/market sources before claiming geographic evidence or current valuations.
