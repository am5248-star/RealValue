"""Ingestion, validation, feature construction, and temporal splitting."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

TARGET = "SALES_PRICE"
ID = "PRT_ID"
DATE = "DATE_SALE"
NUMERIC = ["INT_SQFT", "DIST_MAINROAD", "N_BEDROOM", "N_BATHROOM", "N_ROOM", "QS_ROOMS", "QS_BATHROOM", "QS_BEDROOM", "QS_OVERALL", "HOUSE_AGE"]
CATEGORICAL = ["AREA", "SALE_COND", "PARK_FACIL", "BUILDTYPE", "UTILITY_AVAIL", "STREET", "MZZONE"]
FEATURES = NUMERIC + CATEGORICAL


@dataclass
class Dataset:
    raw: pd.DataFrame
    features: pd.DataFrame
    target: pd.Series
    dates: pd.Series


def load_dataset(path: str | Path) -> Dataset:
    raw = pd.read_csv(path)
    raw_numeric = [col for col in NUMERIC if col != "HOUSE_AGE"]
    required = {ID, DATE, "DATE_BUILD", TARGET, *raw_numeric, *CATEGORICAL}
    missing = sorted(required - set(raw.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    dates = pd.to_datetime(raw[DATE], dayfirst=True, errors="coerce")
    build_dates = pd.to_datetime(raw["DATE_BUILD"], dayfirst=True, errors="coerce")
    target = pd.to_numeric(raw[TARGET], errors="coerce")
    valid = dates.notna() & target.notna() & (target > 0)
    raw, dates, build_dates, target = raw.loc[valid].copy(), dates.loc[valid], build_dates.loc[valid], target.loc[valid]
    features = pd.DataFrame(index=raw.index)
    for col in NUMERIC:
        if col == "HOUSE_AGE":
            features[col] = ((dates - build_dates).dt.days / 365.25).clip(lower=0)
        else:
            features[col] = pd.to_numeric(raw[col], errors="coerce")
    for col in CATEGORICAL:
        features[col] = raw[col].fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    return Dataset(raw, features, target.astype(float), dates)


def chronological_indices(dates: pd.Series) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    order = np.argsort(dates.to_numpy(), kind="stable")
    n = len(order)
    a, b = int(n * 0.70), int(n * 0.85)
    if a < 10 or b <= a or n - b < 10:
        raise ValueError("At least 50 valid rows are required for chronological train/calibration/test splits")
    return order[:a], order[a:b], order[b:]


def profile(path: str | Path) -> dict:
    ds = load_dataset(path)
    return {
        "rows_valid": int(len(ds.raw)), "columns": list(ds.raw.columns),
        "duplicate_rows": int(ds.raw.duplicated().sum()), "unique_property_ids": int(ds.raw[ID].nunique()),
        "missing_by_column": {k: int(v) for k, v in ds.raw.isna().sum().items() if v},
        "sale_date_min": ds.dates.min().date().isoformat(), "sale_date_max": ds.dates.max().date().isoformat(),
        "target_min": float(ds.target.min()), "target_median": float(ds.target.median()), "target_max": float(ds.target.max()),
        "localities": {str(k): int(v) for k, v in ds.raw["AREA"].value_counts().items()},
        "excluded_target_leakage_fields": ["PRT_ID", "REG_FEE", "COMMIS", "SALES_PRICE", "DATE_BUILD(raw)"],
    }
