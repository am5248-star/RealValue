"""Leakage-safe tabular estimators and portable model bundle."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from xgboost import XGBRegressor

from .pipeline import CATEGORICAL, FEATURES, NUMERIC


ESTIMATORS = ("ridge", "random_forest", "xgboost")


class TabularValuator:
    def __init__(self, model_type: str = "xgboost"):
        if model_type not in ESTIMATORS:
            raise ValueError(f"model_type must be one of {ESTIMATORS}")
        self.model_type = model_type
        self.columns: list[str] = []
        self.means: list[float] = []
        self.scales: list[float] = []
        self.estimator = None
        self.residual_quantile = 0.0
        self.calibration_count = 0
        self.train_cutoff = ""
        self.locality_ppsf: dict[str, float] = {}
        self.global_ppsf = 0.0

    def _matrix(self, frame: pd.DataFrame, fitting: bool = False) -> np.ndarray:
        numeric = frame[NUMERIC].apply(pd.to_numeric, errors="coerce")
        categorical = pd.get_dummies(frame[CATEGORICAL].fillna("Unknown").astype(str), prefix=CATEGORICAL, dtype=float)
        x = pd.concat([numeric, categorical], axis=1)
        if fitting:
            self.columns = list(x.columns)
            self.means = [float(x[c].mean()) if pd.notna(x[c].mean()) else 0.0 for c in self.columns]
            x = x.fillna(pd.Series(self.means, index=self.columns)).fillna(0)
            arr = x.to_numpy(dtype=float)
            scales = arr.std(axis=0)
            self.scales = [float(v) if v > 1e-12 else 1.0 for v in scales]
        else:
            x = x.reindex(columns=self.columns, fill_value=0)
            x = x.fillna(pd.Series(self.means, index=self.columns)).fillna(0)
            arr = x.to_numpy(dtype=float)
        return (arr - np.asarray(self.means)) / np.asarray(self.scales)

    def fit(self, frame: pd.DataFrame, y: pd.Series) -> "TabularValuator":
        x = self._matrix(frame, fitting=True)
        if self.model_type == "ridge":
            self.estimator = Ridge(alpha=10.0)
        elif self.model_type == "random_forest":
            self.estimator = RandomForestRegressor(n_estimators=300, min_samples_leaf=2, max_features=0.9,
                                                   n_jobs=-1, random_state=42)
        else:
            self.estimator = XGBRegressor(n_estimators=500, max_depth=5, learning_rate=0.04,
                                          subsample=0.85, colsample_bytree=0.85,
                                          reg_lambda=5.0, reg_alpha=0.0,
                                          objective="reg:squarederror", eval_metric="mae",
                                          tree_method="hist", n_jobs=4, random_state=42)
        self.estimator.fit(x, y.to_numpy(dtype=float))
        return self

    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        if self.estimator is None:
            raise RuntimeError("Estimator is not fitted")
        return np.asarray(self.estimator.predict(self._matrix(frame)), dtype=float)

    def explain(self, row: pd.DataFrame, limit: int = 8) -> list[dict]:
        x = self._matrix(row)
        if self.model_type == "xgboost":
            import xgboost as xgb

            contribution = self.estimator.get_booster().predict(
                xgb.DMatrix(x, feature_names=self.columns), pred_contribs=True
            )[0, :-1]
        elif self.model_type == "ridge":
            contribution = x[0] * self.estimator.coef_
        else:
            # Random Forest has no exact additive local decomposition; show strongest
            # learned feature influences and label them as global importance below.
            importance = self.estimator.feature_importances_
            indexes = np.argsort(importance)[::-1][:limit]
            return [{"feature": self.columns[i], "importance": round(float(importance[i]), 6),
                     "method": "global_feature_importance"} for i in indexes]
        indexes = np.argsort(np.abs(contribution))[::-1][:limit]
        return [{"feature": self.columns[i], "contribution": round(float(contribution[i]), 2),
                 "method": "TreeSHAP" if self.model_type == "xgboost" else "ridge_contribution"}
                for i in indexes]

    def calibrate(self, y_true: pd.Series, y_pred: np.ndarray, alpha: float = 0.10) -> None:
        residuals = np.abs(y_true.to_numpy(dtype=float) - y_pred)
        rank = min(len(residuals), int(np.ceil((len(residuals) + 1) * (1 - alpha))))
        self.residual_quantile = float(np.partition(residuals, rank - 1)[rank - 1])
        self.calibration_count = int(len(residuals))

    def set_market_reference(self, frame: pd.DataFrame, y: pd.Series) -> None:
        rows = pd.DataFrame({"area": frame["AREA"].astype(str), "sqft": pd.to_numeric(frame["INT_SQFT"], errors="coerce"), "price": y})
        rows = rows[(rows.sqft > 0) & (rows.price > 0)]
        rows["ppsf"] = rows.price / rows.sqft
        self.global_ppsf = float(rows.ppsf.median())
        self.locality_ppsf = {str(k): float(v) for k, v in rows.groupby("area").ppsf.median().items()}

    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"format_version": 2, "model_type": self.model_type, "columns": self.columns,
                     "means": self.means, "scales": self.scales, "estimator": self.estimator,
                     "residual_quantile_90": self.residual_quantile, "calibration_count": self.calibration_count,
                     "train_cutoff": self.train_cutoff, "locality_ppsf": self.locality_ppsf,
                     "global_ppsf": self.global_ppsf, "feature_schema": FEATURES,
                     "rule_version": "mvp-2"}, path, compress=3)

    @classmethod
    def load(cls, path: str | Path) -> "TabularValuator":
        value = joblib.load(path)
        if value.get("format_version") != 2 or value.get("feature_schema") != FEATURES:
            raise ValueError("Model bundle version or feature schema is incompatible with this runtime")
        model = cls(value["model_type"])
        model.columns, model.means, model.scales = value["columns"], value["means"], value["scales"]
        model.estimator = value["estimator"]
        model.residual_quantile, model.calibration_count = value["residual_quantile_90"], value["calibration_count"]
        model.train_cutoff, model.locality_ppsf, model.global_ppsf = value["train_cutoff"], value["locality_ppsf"], value["global_ppsf"]
        return model
