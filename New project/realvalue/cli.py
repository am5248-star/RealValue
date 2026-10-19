"""Command line entry points for non-UI backend workflows."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from .model import ESTIMATORS, TabularValuator
from .pipeline import chronological_indices, load_dataset, profile
from .service import ValuationService


def train(data_path: str, artifacts: str) -> dict:
    ds = load_dataset(data_path)
    train_idx, cal_idx, test_idx = chronological_indices(ds.dates)
    actual = ds.target.iloc[test_idx].to_numpy()
    baseline = float(ds.target.iloc[train_idx].median())
    results = {}
    fitted = {}
    for model_type in ESTIMATORS:
        candidate = TabularValuator(model_type).fit(ds.features.iloc[train_idx], ds.target.iloc[train_idx])
        candidate.train_cutoff = ds.dates.iloc[train_idx].max().date().isoformat()
        candidate.calibrate(ds.target.iloc[cal_idx], candidate.predict(ds.features.iloc[cal_idx]))
        pred = candidate.predict(ds.features.iloc[test_idx])
        radius = candidate.residual_quantile
        results[model_type] = {
            "test_mae_inr": float(np.mean(np.abs(actual - pred))),
            "test_rmse_inr": float(np.sqrt(np.mean((actual - pred) ** 2))),
            "test_mape": float(np.mean(np.abs(actual - pred) / actual)),
            "calibration_absolute_residual_quantile_inr": radius,
            "test_interval_coverage": float(np.mean((actual >= pred - radius) & (actual <= pred + radius))),
            "test_mean_interval_width_inr": float(2 * radius),
        }
        fitted[model_type] = candidate
    model = fitted["xgboost"]
    model.set_market_reference(ds.features.iloc[train_idx], ds.target.iloc[train_idx])
    metrics = {"rows": {"train": len(train_idx), "calibration": len(cal_idx), "test": len(test_idx)},
               "split_dates": {"train_end": model.train_cutoff, "calibration_end": ds.dates.iloc[cal_idx].max().date().isoformat(),
                               "test_start": ds.dates.iloc[test_idx].min().date().isoformat(), "test_end": ds.dates.iloc[test_idx].max().date().isoformat()},
               "selected_model": "xgboost", "model_comparison": results,
               "median_baseline_mae_inr": float(np.mean(np.abs(actual - baseline))),
               "median_baseline_rmse_inr": float(np.sqrt(np.mean((actual - baseline) ** 2))),
               "interval_nominal_coverage": 0.90,
               "limitations": ["Historical chronological split; drift can invalidate exchangeability", "No geography beyond locality labels", "Review rules are not calibrated probabilities"]}
    out = Path(artifacts)
    out.mkdir(parents=True, exist_ok=True)
    model.save(out / "model.joblib")
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(prog="realvalue")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ["profile", "train"]:
        cmd = sub.add_parser(command)
        cmd.add_argument("--data", default=os.environ.get("REALVALUE_DATA"), required=os.environ.get("REALVALUE_DATA") is None)
        if command == "train":
            cmd.add_argument("--artifacts", default="artifacts")
    value = sub.add_parser("value")
    value.add_argument("--model", required=True); value.add_argument("--data", required=True); value.add_argument("--row", type=int, default=0)
    batch = sub.add_parser("batch")
    batch.add_argument("--model", required=True); batch.add_argument("--input", required=True); batch.add_argument("--output", required=True)
    batch.add_argument("--history", required=True, help="Historical transaction CSV used for comparable evidence")
    args = parser.parse_args()
    if args.command == "profile":
        result = profile(args.data)
    elif args.command == "train":
        result = train(args.data, args.artifacts)
    elif args.command == "value":
        ds = load_dataset(args.data); model = TabularValuator.load(args.model)
        record = ds.raw.iloc[args.row].to_dict()
        svc = ValuationService(model, ds.raw)
        result = svc.value(record).to_dict()
    else:
        model = TabularValuator.load(args.model)
        requests = pd.read_csv(args.input)
        history = pd.read_csv(args.history)
        service = ValuationService(model, history)
        responses = [service.value(row.to_dict()).to_dict() for _, row in requests.iterrows()]
        pd.DataFrame(responses).to_csv(args.output, index=False)
        result = {"rows_written": len(responses), "output": args.output}
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
