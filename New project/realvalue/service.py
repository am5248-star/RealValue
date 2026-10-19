"""Valuation orchestration, evidence retrieval, and trust checks."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from .model import TabularValuator
from .pipeline import CATEGORICAL, NUMERIC


@dataclass
class ValuationResponse:
    estimated_price: float
    interval_low: float
    interval_high: float
    currency: str
    confidence_flag: str
    abstained: bool
    review_reasons: list[str]
    explanation: list[dict]
    comparables: list[dict]
    consistency: dict
    model_version: str = "xgboost-mvp-2"

    def to_dict(self) -> dict:
        return asdict(self)


class ValuationService:
    def __init__(self, model: TabularValuator, historical: pd.DataFrame | None = None):
        self.model, self.historical = model, historical

    def value(self, request: dict) -> ValuationResponse:
        row = pd.DataFrame([request])
        sale_date = pd.to_datetime(row.get("DATE_SALE"), dayfirst=True, errors="coerce") if "DATE_SALE" in row else None
        build_date = pd.to_datetime(row.get("DATE_BUILD"), dayfirst=True, errors="coerce") if "DATE_BUILD" in row else None
        if sale_date is not None and build_date is not None:
            row["HOUSE_AGE"] = ((sale_date - build_date).dt.days / 365.25).clip(lower=0)
        for col in CATEGORICAL:
            if col not in row:
                row[col] = "Unknown"
        for col in NUMERIC:
            if col not in row:
                row[col] = np.nan
        prediction = max(0.0, float(self.model.predict(row)[0]))
        radius = self.model.residual_quantile
        low, high = max(0.0, prediction - radius), prediction + radius
        review: list[str] = []
        sqft = float(request.get("INT_SQFT") or 0)
        locality = str(request.get("AREA", "Unknown")).strip()
        ppsf = self.model.locality_ppsf.get(locality, self.model.global_ppsf)
        benchmark = ppsf * sqft if sqft > 0 else 0.0
        ratio = prediction / benchmark if benchmark else None
        if sqft <= 0:
            review.append("Missing or invalid floor area")
        if locality not in self.model.locality_ppsf:
            review.append("No historical locality benchmark")
        if ratio is not None and (ratio < 0.5 or ratio > 2.0):
            review.append("Prediction differs materially from historical locality price-per-square-foot scale")
        comps = self._comparables(row, limit=5)
        if len(comps) < 3:
            review.append("Fewer than three comparable transactions")
        return ValuationResponse(
            estimated_price=round(prediction, 2), interval_low=round(low, 2), interval_high=round(high, 2),
            currency="INR", confidence_flag="review" if review else "standard", abstained=bool(review),
            review_reasons=review, explanation=self.model.explain(row), comparables=comps,
            consistency={"locality_median_price_per_sqft": round(ppsf, 2) if ppsf else None,
                         "benchmark_value": round(benchmark, 2) if benchmark else None,
                         "prediction_to_benchmark_ratio": round(ratio, 3) if ratio is not None else None})

    def _comparables(self, request: pd.DataFrame, limit: int) -> list[dict]:
        if self.historical is None or self.historical.empty:
            return []
        source = self.historical.copy()
        if "DATE_SALE" in source and "DATE_SALE" in request:
            cutoff = pd.to_datetime(request.iloc[0]["DATE_SALE"], dayfirst=True, errors="coerce")
            source_dates = pd.to_datetime(source["DATE_SALE"], dayfirst=True, errors="coerce")
            if pd.notna(cutoff):
                source = source.loc[source_dates <= cutoff]
        if "PRT_ID" in source and "PRT_ID" in request:
            source = source.loc[source["PRT_ID"].astype(str) != str(request.iloc[0]["PRT_ID"])]
        source = source[source["AREA"].astype(str).str.casefold() == str(request.iloc[0]["AREA"]).casefold()]
        if source.empty:
            return []
        score = np.zeros(len(source), dtype=float)
        weights = {"INT_SQFT": 0.30, "N_BEDROOM": 0.15, "N_BATHROOM": 0.10, "N_ROOM": 0.10}
        for col, weight in weights.items():
            target = pd.to_numeric(request.iloc[0].get(col), errors="coerce")
            values = pd.to_numeric(source[col], errors="coerce")
            med = max(float(values.median()), 1.0)
            score += weight * ((values - target).abs() / med).fillna(1.0).to_numpy()
        for col in ["SALE_COND", "BUILDTYPE", "PARK_FACIL"]:
            score += 0.08 * (source[col].astype(str).to_numpy() != str(request.iloc[0].get(col, "Unknown")))
        source = source.assign(_score=score).nsmallest(limit, "_score")
        output = []
        for _, item in source.iterrows():
            output.append({"property_id": str(item.get("PRT_ID", "")), "locality": str(item["AREA"]),
                           "area_sqft": int(item["INT_SQFT"]), "sale_price": int(item["SALES_PRICE"]),
                           "price_per_sqft": round(float(item["SALES_PRICE"]) / max(float(item["INT_SQFT"]), 1), 2),
                           "similarity_score": round(float(item["_score"]), 3)})
        return output
