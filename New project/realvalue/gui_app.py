"""RealValue AI — Desktop Demonstration Suite (CustomTkinter).

Core GUI window, theme styling, layout panels, and background adapter binding.
"""

from __future__ import annotations

import json
from pathlib import Path
import queue
import tkinter as tk
from typing import Any

import customtkinter as ctk

from .gui_adapter import ModelAdapter
from .gui_components import PropertyInputForm, ValuationResultBanner
from .gui_evidence import EvidenceExplorer

# Configure CustomTkinter defaults
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class RealValueApp(ctk.CTk):
    """Main desktop application window for RealValue AI."""

    def __init__(self, adapter: ModelAdapter | None = None):
        super().__init__()

        self.title("RealValue AI — Chennai Property Valuation Engine")
        self.geometry("1240x820")
        self.minsize(1080, 720)

        self.adapter = adapter or ModelAdapter()
        self._event_queue: queue.Queue = queue.Queue()
        self.current_result: dict[str, Any] | None = None

        # Grid configuration for root window
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_main_tabs()
        self._build_status_bar()

        # Start queue polling and background loading
        self._poll_event_queue()
        self._start_engine_loading()

    def _poll_event_queue(self) -> None:
        """Polls queue on main thread to process background events safely."""
        try:
            if not self.winfo_exists():
                return
            while True:
                event_type, payload = self._event_queue.get_nowait()
                if event_type == "engine_loaded":
                    self._on_engine_loaded()
                elif event_type == "engine_error":
                    self._on_engine_error(payload)
        except (queue.Empty, tk.TclError):
            pass

        try:
            if self.winfo_exists():
                self.after(50, self._poll_event_queue)
        except tk.TclError:
            pass

    def _build_header(self) -> None:
        """Builds top header banner with branding and engine status."""
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#1A1C23", "#12141A"))
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(1, weight=1)

        # Branding & Title
        title_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_container.grid(row=0, column=0, padx=20, pady=12, sticky="w")

        title_label = ctk.CTkLabel(
            title_container,
            text="REALVALUE AI",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=("#3B82F6", "#60A5FA"),
        )
        title_label.pack(side="left")

        subtitle_label = ctk.CTkLabel(
            title_container,
            text="  |  Chennai Property Valuation & Trust Layer",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=("#9CA3AF", "#9CA3AF"),
        )
        subtitle_label.pack(side="left")

        # Right badges
        badge_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        badge_container.grid(row=0, column=2, padx=20, pady=12, sticky="e")

        self.model_badge = ctk.CTkLabel(
            badge_container,
            text="Serving: XGBoost (TreeSHAP • 90% Conformal)",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=("#2563EB", "#1E3A8A"),
            corner_radius=6,
            padx=10,
            pady=4,
        )
        self.model_badge.pack(side="left", padx=(0, 10))

        self.status_badge = ctk.CTkLabel(
            badge_container,
            text="● Initializing Engine...",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#FBBF24",
            fg_color=("#374151", "#1F2937"),
            corner_radius=6,
            padx=10,
            pady=4,
        )
        self.status_badge.pack(side="left")

    def _build_main_tabs(self) -> None:
        """Builds tabbed navigation between Valuation Studio and Model Diagnostics."""
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=16, pady=(10, 10))

        self.tab_studio = self.tabview.add("Valuation Studio")
        self.tab_diagnostics = self.tabview.add("Model Diagnostics & Benchmarks")

        self._setup_studio_layout()
        self._setup_diagnostics_layout()

    def _setup_studio_layout(self) -> None:
        """Sets up responsive two-column layout for Valuation Studio."""
        self.tab_studio.grid_rowconfigure(0, weight=1)
        self.tab_studio.grid_columnconfigure(0, weight=4, minsize=420)  # Left: Inputs
        self.tab_studio.grid_columnconfigure(1, weight=6, minsize=560)  # Right: Results & Analysis

        # Left Column: Inputs Form Container
        self.input_container = ctk.CTkFrame(self.tab_studio, corner_radius=8)
        self.input_container.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)
        self.input_container.grid_rowconfigure(1, weight=1)
        self.input_container.grid_columnconfigure(0, weight=1)

        input_header = ctk.CTkLabel(
            self.input_container,
            text="Property Parameters & Configuration",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            anchor="w",
        )
        input_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))

        self.input_form = PropertyInputForm(
            self.input_container,
            adapter=self.adapter,
            on_calculate=self.calculate_valuation,
            corner_radius=6,
        )
        self.input_form.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Right Column: Valuation Results & Intelligence
        self.results_container = ctk.CTkFrame(self.tab_studio, corner_radius=8)
        self.results_container.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=0)
        self.results_container.grid_rowconfigure(2, weight=1)
        self.results_container.grid_columnconfigure(0, weight=1)

        results_header = ctk.CTkLabel(
            self.results_container,
            text="Valuation Output & Trust Intelligence",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            anchor="w",
        )
        results_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))

        # Valuation Result Banner
        self.result_banner = ValuationResultBanner(self.results_container)
        self.result_banner.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))

        # Evidence Explorer (TreeSHAP & Comps)
        self.evidence_explorer = EvidenceExplorer(self.results_container)
        self.evidence_explorer.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))

    def _setup_diagnostics_layout(self) -> None:
        """Sets up layout for Model Diagnostics & Benchmarks tab."""
        self.tab_diagnostics.grid_rowconfigure(0, weight=1)
        self.tab_diagnostics.grid_columnconfigure(0, weight=1)

        self.diagnostics_container = ctk.CTkScrollableFrame(self.tab_diagnostics, corner_radius=8)
        self.diagnostics_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.diagnostics_container.grid_columnconfigure(0, weight=1)

        diag_title = ctk.CTkLabel(
            self.diagnostics_container,
            text="Chronological Holdout Evaluation & Model Benchmark Comparison",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#60A5FA",
            anchor="w",
        )
        diag_title.pack(anchor="w", padx=16, pady=(16, 4))

        diag_desc = ctk.CTkLabel(
            self.diagnostics_container,
            text=(
                "Models evaluated on identical chronological splits: Train (earliest 70% through Jun 2011), "
                "Calibration (15% through Mar 2012), Test (latest 15% through Feb 2015).\n"
                "Registration fees, sales commission, IDs, and post-transaction fields excluded to prevent target leakage."
            ),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#9CA3AF",
            justify="left",
            wraplength=850,
        )
        diag_desc.pack(anchor="w", padx=16, pady=(0, 14))

        # Sample splits row container
        self.split_frame = ctk.CTkFrame(self.diagnostics_container, fg_color="transparent")
        self.split_frame.pack(fill="x", padx=16, pady=(0, 12))
        self.split_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # 4 Model Comparison Cards Grid
        self.cards_frame = ctk.CTkFrame(self.diagnostics_container, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=16, pady=(0, 12))
        self.cards_frame.grid_columnconfigure((0, 1), weight=1)

        # Benchmarks Summary Card
        self.metrics_card = ctk.CTkFrame(self.diagnostics_container, fg_color=("#222733", "#171B24"), corner_radius=8)
        self.metrics_card.pack(fill="x", padx=16, pady=8)

        self.metrics_text_label = ctk.CTkLabel(
            self.metrics_card,
            text="Loading benchmark metrics from artifacts/metrics.json...",
            font=ctk.CTkFont(family="Consolas", size=12),
            justify="left",
            anchor="w",
        )
        self.metrics_text_label.pack(fill="both", padx=16, pady=16)

    def _build_status_bar(self) -> None:
        """Builds bottom status bar with engine and dataset summary."""
        self.status_bar = ctk.CTkFrame(self, height=28, corner_radius=0, fg_color=("#1A1C23", "#0F1117"))
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        self.status_bar.grid_columnconfigure(1, weight=1)

        self.status_left = ctk.CTkLabel(
            self.status_bar,
            text="Bundle: artifacts/model.joblib | Model: XGBoost Regressor | Historical Cutoff: 2011-06-12",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#9CA3AF",
        )
        self.status_left.grid(row=0, column=0, padx=16, pady=4, sticky="w")

        self.status_right = ctk.CTkLabel(
            self.status_bar,
            text="Historical Transactions: Loading...",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#9CA3AF",
        )
        self.status_right.grid(row=0, column=2, padx=16, pady=4, sticky="e")

    def _start_engine_loading(self) -> None:
        """Triggers background thread to load model and dataset."""
        self.adapter.load_async(
            on_success=lambda ad: self._event_queue.put(("engine_loaded", None)),
            on_error=lambda err: self._event_queue.put(("engine_error", err)),
        )

    def _on_engine_loaded(self) -> None:
        """Callback invoked on main UI thread when engine finishes loading."""
        info = self.adapter.get_status_info()
        self.status_badge.configure(
            text="● Engine Ready (xgboost-mvp-2)",
            text_color="#34D399",
            fg_color=("#064E3B", "#064E3B"),
        )
        self.status_right.configure(text=f"Historical Transactions: {info['rows_count']:,} rows")

        # Update diagnostics display with actual loaded metrics
        metrics = self.adapter.metrics
        if metrics:
            comp = metrics.get("model_comparison", {})
            xgb_m = comp.get("xgboost", {})
            rf_m = comp.get("random_forest", {})
            ridge_m = comp.get("ridge", {})
            rows_m = metrics.get("rows", {})
            dates_m = metrics.get("split_dates", {})

            # Populate Sample Splits Row
            for widget in self.split_frame.winfo_children():
                widget.destroy()

            split_data = [
                ("Training Sample (70%)", f"{rows_m.get('train', 0):,} properties", f"Start to {dates_m.get('train_end', 'N/A')}", "#3B82F6"),
                ("Calibration Sample (15%)", f"{rows_m.get('calibration', 0):,} properties", f"to {dates_m.get('calibration_end', 'N/A')} (90% Quantile)", "#10B981"),
                ("Holdout Test Sample (15%)", f"{rows_m.get('test', 0):,} properties", f"{dates_m.get('test_start', 'N/A')} to {dates_m.get('test_end', 'N/A')}", "#F59E0B"),
            ]
            for col_idx, (title, count, subtitle, color) in enumerate(split_data):
                pill = ctk.CTkFrame(self.split_frame, fg_color=("#222733", "#171B24"), corner_radius=6)
                pill.grid(row=0, column=col_idx, sticky="ew", padx=4, pady=2)
                ctk.CTkLabel(pill, text=title, font=ctk.CTkFont(size=11, weight="bold"), text_color=color).pack(anchor="w", padx=12, pady=(8, 2))
                ctk.CTkLabel(pill, text=count, font=ctk.CTkFont(size=16, weight="bold"), text_color="#E5E7EB").pack(anchor="w", padx=12, pady=(0, 2))
                ctk.CTkLabel(pill, text=subtitle, font=ctk.CTkFont(size=10), text_color="#9CA3AF").pack(anchor="w", padx=12, pady=(0, 8))

            # Populate 4 Model Cards
            for widget in self.cards_frame.winfo_children():
                widget.destroy()

            model_cards = [
                {
                    "title": "XGBoost Regressor",
                    "badge": "★ SELECTED SERVING MODEL",
                    "badge_color": ("#064E3B", "#34D399"),
                    "mae": f"₹{xgb_m.get('test_mae_inr', 0):,.0f}",
                    "rmse": f"₹{xgb_m.get('test_rmse_inr', 0):,.0f}",
                    "mape": f"{xgb_m.get('test_mape', 0)*100:.2f}%",
                    "coverage": f"{xgb_m.get('test_interval_coverage', 0)*100:.1f}%",
                    "width": f"±₹{xgb_m.get('test_mean_interval_width_inr', 0)/2:,.0f}",
                    "row": 0, "col": 0,
                    "highlight": True,
                },
                {
                    "title": "Random Forest Regressor",
                    "badge": "CANDIDATE #2",
                    "badge_color": ("#1E293B", "#94A3B8"),
                    "mae": f"₹{rf_m.get('test_mae_inr', 0):,.0f}",
                    "rmse": f"₹{rf_m.get('test_rmse_inr', 0):,.0f}",
                    "mape": f"{rf_m.get('test_mape', 0)*100:.2f}%",
                    "coverage": f"{rf_m.get('test_interval_coverage', 0)*100:.1f}%",
                    "width": f"±₹{rf_m.get('test_mean_interval_width_inr', 0)/2:,.0f}",
                    "row": 0, "col": 1,
                    "highlight": False,
                },
                {
                    "title": "Ridge Regression",
                    "badge": "LINEAR BASELINE",
                    "badge_color": ("#1E293B", "#94A3B8"),
                    "mae": f"₹{ridge_m.get('test_mae_inr', 0):,.0f}",
                    "rmse": f"₹{ridge_m.get('test_rmse_inr', 0):,.0f}",
                    "mape": f"{ridge_m.get('test_mape', 0)*100:.2f}%",
                    "coverage": f"{ridge_m.get('test_interval_coverage', 0)*100:.1f}%",
                    "width": f"±₹{ridge_m.get('test_mean_interval_width_inr', 0)/2:,.0f}",
                    "row": 1, "col": 0,
                    "highlight": False,
                },
                {
                    "title": "Training Median Baseline",
                    "badge": "NAIVE BENCHMARK",
                    "badge_color": ("#450A0A", "#F87171"),
                    "mae": f"₹{metrics.get('median_baseline_mae_inr', 0):,.0f}",
                    "rmse": f"₹{metrics.get('median_baseline_rmse_inr', 0):,.0f}",
                    "mape": "—",
                    "coverage": "—",
                    "width": "—",
                    "row": 1, "col": 1,
                    "highlight": False,
                },
            ]

            for card_info in model_cards:
                c_frame = ctk.CTkFrame(
                    self.cards_frame,
                    fg_color=("#1E2430", "#141720") if not card_info["highlight"] else ("#1E3A8A", "#0F2042"),
                    border_width=2 if card_info["highlight"] else 1,
                    border_color="#3B82F6" if card_info["highlight"] else "#2D3748",
                    corner_radius=8,
                )
                c_frame.grid(row=card_info["row"], column=card_info["col"], sticky="nsew", padx=4, pady=4)

                top_card = ctk.CTkFrame(c_frame, fg_color="transparent")
                top_card.pack(fill="x", padx=12, pady=(10, 4))
                top_card.grid_columnconfigure(0, weight=1)

                ctk.CTkLabel(top_card, text=card_info["title"], font=ctk.CTkFont(size=14, weight="bold"), text_color="#E5E7EB").grid(row=0, column=0, sticky="w")
                ctk.CTkLabel(
                    top_card,
                    text=card_info["badge"],
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=card_info["badge_color"][1],
                    fg_color=card_info["badge_color"][0],
                    corner_radius=4,
                    padx=6,
                    pady=2,
                ).grid(row=0, column=1, sticky="e")

                # Metrics table row
                ctk.CTkLabel(
                    c_frame,
                    text=f"Test MAE: {card_info['mae']}  •  RMSE: {card_info['rmse']}  •  MAPE: {card_info['mape']}\n90% Conformal Coverage: {card_info['coverage']}  •  Calibration Radius: {card_info['width']}",
                    font=ctk.CTkFont(size=11),
                    text_color="#9CA3AF" if not card_info["highlight"] else "#93C5FD",
                    justify="left",
                    anchor="w",
                ).pack(fill="x", padx=12, pady=(0, 10))

            summary_text = (
                f"Calibration & Trust Specifications:\n"
                f"  • Split-Conformal Method: Held-out empirical absolute-residual quantile calibration at alpha=0.10 (90% nominal)\n"
                f"  • Calibration Residual Quantile (radius): ±₹{info['radius']:,.0f}\n"
                f"  • Locality Median Price/SqFt Benchmark Scale: ₹{info['global_ppsf']:,.2f}/sqft global median\n"
                f"  • Review Flag Triggers: SqFt <= 0, Locality without historical benchmark, Ratio < 0.5 or > 2.0, or Comps < 3\n\n"
                f"Operational Scope & Model Limitations:\n"
                f"  • Source dataset spans Chennai sales from 2004 to 2015; predictions are historical market valuations.\n"
                f"  • Geographic coordinates and POI distance layers are absent from source; locality labels provide spatial conditioning.\n"
                f"  • Review signal is a conservative rule-based safety flag, not a calibrated failure probability."
            )
            self.metrics_text_label.configure(text=summary_text)

        # Trigger initial calculation with default property
        initial_request = self.input_form.get_values()
        self.calculate_valuation(initial_request)

    def calculate_valuation(self, request_dict: dict[str, Any]) -> None:
        """Executes valuation through model adapter and updates UI."""
        if not self.adapter.is_loaded:
            return
        try:
            result = self.adapter.predict(request_dict)
            self.current_result = result
            self.result_banner.display_result(result)
            self.evidence_explorer.update_evidence(result)
        except Exception as exc:
            self.status_right.configure(text=f"Prediction error: {exc}")

    def _on_engine_error(self, err: Exception) -> None:
        """Callback invoked if engine loading encounters an error."""
        self.status_badge.configure(
            text="● Engine Load Error",
            text_color="#EF4444",
            fg_color=("#7F1D1D", "#7F1D1D"),
        )
        self.status_right.configure(text=f"Error: {err}")


def launch_app() -> None:
    """Entry point for running the application."""
    app = RealValueApp()
    app.mainloop()


if __name__ == "__main__":
    launch_app()
