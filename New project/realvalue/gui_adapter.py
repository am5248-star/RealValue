"""GUI Integration Adapter for RealValue Engine.

Provides thread-safe model and historical dataset loading, valuation invocation,
and metadata extraction without modifying model internals or blocking the GUI.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from .model import TabularValuator
from .pipeline import load_dataset
from .service import ValuationResponse, ValuationService

DEFAULT_MODEL_PATH = Path("artifacts/model.joblib")
DEFAULT_DATA_PATH = Path("data/Chennai houseing sale.csv")
DEFAULT_METRICS_PATH = Path("artifacts/metrics.json")

# Clean, canonical locality list supported by the model and historical data
PRIMARY_LOCALITIES = [
    "Karapakkam",
    "Adyar",
    "Chrompet",
    "Velachery",
    "KK Nagar",
    "Anna Nagar",
    "T Nagar",
]

CATEGORICAL_CHOICES = {
    "BUILDTYPE": ["House", "Commercial", "Others"],
    "SALE_COND": ["Normal Sale", "AbNormal", "Family", "Partial", "AdjLand"],
    "PARK_FACIL": ["Yes", "No"],
    "UTILITY_AVAIL": ["AllPub", "ELO", "NoSeWa", "NoSewr "],
    "STREET": ["Paved", "Gravel", "No Access"],
    "MZZONE": ["RL", "RM", "RH", "A", "C", "I"],
}


class ModelAdapter:
    """Thread-safe adapter bridging the CustomTkinter GUI to ValuationService."""

    def __init__(
        self,
        model_path: str | Path | None = None,
        data_path: str | Path | None = None,
        metrics_path: str | Path | None = None,
    ):
        self.model_path = Path(model_path or DEFAULT_MODEL_PATH)
        self.data_path = self._resolve_data_path(data_path)
        self.metrics_path = Path(metrics_path or DEFAULT_METRICS_PATH)

        self.model: TabularValuator | None = None
        self.raw_data: pd.DataFrame | None = None
        self.service: ValuationService | None = None
        self.metrics: dict[str, Any] = {}
        self.is_loaded: bool = False
        self.load_error: str | None = None

        self._lock = threading.Lock()

    def _resolve_data_path(self, explicit_path: str | Path | None) -> Path:
        if explicit_path:
            return Path(explicit_path)
        if DEFAULT_DATA_PATH.exists():
            return DEFAULT_DATA_PATH
        env_path = os.environ.get("REALVALUE_DATA")
        if env_path and Path(env_path).exists():
            return Path(env_path)
        downloads_candidate = Path.home() / "Downloads" / "Chennai houseing sale.csv"
        if downloads_candidate.exists():
            return downloads_candidate
        return DEFAULT_DATA_PATH

    def load_sync(self) -> None:
        """Synchronously loads model and historical dataset."""
        with self._lock:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model bundle not found at {self.model_path}")
            if not self.data_path.exists():
                raise FileNotFoundError(f"Historical dataset not found at {self.data_path}")

            self.model = TabularValuator.load(self.model_path)
            dataset = load_dataset(self.data_path)
            self.raw_data = dataset.raw
            self.service = ValuationService(self.model, self.raw_data)

            if self.metrics_path.exists():
                try:
                    self.metrics = json.loads(self.metrics_path.read_text(encoding="utf-8"))
                except Exception:
                    self.metrics = {}
            else:
                self.metrics = {}

            self.is_loaded = True
            self.load_error = None

    def load_async(
        self,
        on_success: Callable[["ModelAdapter"], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> threading.Thread:
        """Asynchronously loads artifacts in a background daemon thread."""

        def _worker():
            try:
                self.load_sync()
                if on_success:
                    on_success(self)
            except Exception as exc:
                self.load_error = str(exc)
                if on_error:
                    on_error(exc)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return thread

    def predict(self, request: dict[str, Any]) -> dict[str, Any]:
        """Performs a valuation request and returns dict response."""
        with self._lock:
            if not self.is_loaded or self.service is None:
                raise RuntimeError("Valuation engine is not loaded yet")
            response: ValuationResponse = self.service.value(request)
            return response.to_dict()

    def get_localities(self) -> list[str]:
        """Returns sorted canonical list of Chennai localities."""
        return list(PRIMARY_LOCALITIES)

    def get_categorical_choices(self) -> dict[str, list[str]]:
        """Returns standard categorical choices for UI forms."""
        return dict(CATEGORICAL_CHOICES)

    def get_default_property(self) -> dict[str, Any]:
        """Returns standard representative property parameters."""
        return {
            "AREA": "Karapakkam",
            "INT_SQFT": 1200,
            "DIST_MAINROAD": 50,
            "N_BEDROOM": 2,
            "N_BATHROOM": 1,
            "N_ROOM": 4,
            "SALE_COND": "Normal Sale",
            "PARK_FACIL": "Yes",
            "BUILDTYPE": "House",
            "UTILITY_AVAIL": "AllPub",
            "STREET": "Paved",
            "MZZONE": "RL",
            "QS_ROOMS": 3.8,
            "QS_BATHROOM": 3.6,
            "QS_BEDROOM": 3.7,
            "QS_OVERALL": 3.7,
            "DATE_SALE": "15-05-2012",
            "DATE_BUILD": "15-05-2002",
        }

    def get_status_info(self) -> dict[str, Any]:
        """Returns summary status for the UI status bar."""
        with self._lock:
            if not self.is_loaded or self.model is None:
                return {
                    "is_loaded": False,
                    "model_type": "N/A",
                    "rows_count": 0,
                    "radius": 0.0,
                    "train_cutoff": "N/A",
                }
            return {
                "is_loaded": True,
                "model_type": getattr(self.model, "model_type", "xgboost"),
                "rows_count": len(self.raw_data) if self.raw_data is not None else 0,
                "radius": getattr(self.model, "residual_quantile", 0.0),
                "train_cutoff": getattr(self.model, "train_cutoff", "Unknown"),
                "global_ppsf": getattr(self.model, "global_ppsf", 0.0),
            }
