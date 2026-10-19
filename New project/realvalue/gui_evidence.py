"""Explainability and Evidence components for RealValue AI.

Includes embedded Matplotlib TreeSHAP feature attributions visualizer and
scrollable nearest historical comparable property sales cards.
"""

from __future__ import annotations

from typing import Any

import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .gui_components import format_inr, format_lakhs


def format_feature_name(name: str) -> str:
    """Transforms raw model dummy column names into clean human-readable labels."""
    if name.startswith("BUILDTYPE_"):
        return f"Build: {name.replace('BUILDTYPE_', '')}"
    if name.startswith("AREA_"):
        return f"Locality: {name.replace('AREA_', '')}"
    if name.startswith("MZZONE_"):
        return f"Zone: {name.replace('MZZONE_', '')}"
    if name.startswith("PARK_FACIL_"):
        return f"Parking: {name.replace('PARK_FACIL_', '')}"
    if name.startswith("SALE_COND_"):
        return f"Sale: {name.replace('SALE_COND_', '')}"
    if name.startswith("STREET_"):
        return f"Street: {name.replace('STREET_', '')}"
    if name.startswith("UTILITY_AVAIL_"):
        return f"Utility: {name.replace('UTILITY_AVAIL_', '').strip()}"

    mapping = {
        "INT_SQFT": "Floor Area (SqFt)",
        "HOUSE_AGE": "Property Age",
        "N_ROOM": "Total Rooms",
        "N_BEDROOM": "Bedrooms",
        "N_BATHROOM": "Bathrooms",
        "DIST_MAINROAD": "Dist to Road",
        "QS_OVERALL": "Quality Score",
        "QS_ROOMS": "Room Quality",
        "QS_BATHROOM": "Bath Quality",
        "QS_BEDROOM": "Bed Quality",
    }
    return mapping.get(name, name)


class TreeSHAPVisualizer(ctk.CTkFrame):
    """Visualizes additive TreeSHAP contributions as a horizontal bar chart."""

    def __init__(self, master: Any, **kwargs):
        super().__init__(master, fg_color=("#1F2430", "#141720"), corner_radius=8, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Matplotlib figure setup
        self.fig = Figure(figsize=(5.6, 3.4), dpi=100)
        self.fig.patch.set_facecolor("#141720")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#141720")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

    def display_explanation(self, explanations: list[dict[str, Any]]) -> None:
        """Plots top feature drivers onto the Matplotlib canvas."""
        self.ax.clear()
        self.fig.patch.set_facecolor("#141720")
        self.ax.set_facecolor("#141720")

        if not explanations:
            self.ax.text(
                0.5, 0.5, "No feature attributions available.",
                color="#9CA3AF", ha="center", va="center", transform=self.ax.transAxes
            )
            self.canvas.draw()
            return

        # Sort features so negative values are at the bottom, positive on top
        sorted_exp = sorted(explanations, key=lambda x: x.get("contribution", 0.0))

        labels = [format_feature_name(item.get("feature", "")) for item in sorted_exp]
        values = [float(item.get("contribution", 0.0)) for item in sorted_exp]
        colors = ["#10B981" if v >= 0 else "#F43F5E" for v in values]

        y_positions = range(len(labels))
        bars = self.ax.barh(y_positions, values, color=colors, height=0.6, align="center")

        # Zero reference line
        self.ax.axvline(0, color="#4B5563", linestyle="--", linewidth=0.9, alpha=0.7)

        # Labels and ticks
        self.ax.set_yticks(y_positions)
        self.ax.set_yticklabels(labels, color="#E5E7EB", fontsize=9, fontweight="medium")

        # Hide top/right spines
        for spine in ["top", "right"]:
            self.ax.spines[spine].set_visible(False)
        self.ax.spines["left"].set_color("#374151")
        self.ax.spines["bottom"].set_color("#374151")

        self.ax.tick_params(axis="x", colors="#9CA3AF", labelsize=8)
        self.ax.tick_params(axis="y", colors="#E5E7EB", length=0)

        # Format X axis in Lakhs
        def x_fmt(x, _):
            if abs(x) >= 100000:
                return f"{x/100000:+.1f}L"
            return f"{x:+.0f}"

        self.ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(x_fmt))

        # Add text labels on the bars
        for bar, val in zip(bars, values):
            width = bar.get_width()
            val_str = f"{format_lakhs(val)}"
            if width >= 0:
                self.ax.text(
                    width + (max(abs(v) for v in values) * 0.02),
                    bar.get_y() + bar.get_height() / 2,
                    f"+{val_str}",
                    va="center",
                    ha="left",
                    color="#34D399",
                    fontsize=8,
                    fontweight="bold",
                )
            else:
                self.ax.text(
                    width - (max(abs(v) for v in values) * 0.02),
                    bar.get_y() + bar.get_height() / 2,
                    f"-{val_str}",
                    va="center",
                    ha="right",
                    color="#FB7185",
                    fontsize=8,
                    fontweight="bold",
                )

        # Adjust limits to ensure text fits
        max_abs = max(abs(v) for v in values) if values else 1.0
        self.ax.set_xlim(-max_abs * 1.35, max_abs * 1.35)

        self.ax.set_title("TreeSHAP Local Drivers (Impact on Price)", color="#D1D5DB", fontsize=10, pad=8)
        self.fig.tight_layout()
        self.canvas.draw()


class ComparablesExplorer(ctk.CTkScrollableFrame):
    """Displays top 5 nearest historical comparable property sales."""

    def __init__(self, master: Any, **kwargs):
        super().__init__(master, fg_color=("#1F2430", "#141720"), corner_radius=8, **kwargs)
        self.grid_columnconfigure(0, weight=1)

    def display_comparables(self, comparables: list[dict[str, Any]]) -> None:
        """Renders comparable sales cards."""
        for widget in self.winfo_children():
            widget.destroy()

        if not comparables:
            empty_lbl = ctk.CTkLabel(
                self,
                text="No historical comparable sales available for this query.",
                font=ctk.CTkFont(size=12),
                text_color="#9CA3AF",
            )
            empty_lbl.pack(padx=16, pady=24)
            return

        header_lbl = ctk.CTkLabel(
            self,
            text=f"Nearest Historical Transactions in Chennai Dataset ({len(comparables)} Evidence Comps):",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#9CA3AF",
            anchor="w",
        )
        header_lbl.pack(anchor="w", padx=8, pady=(4, 8))

        for idx, comp in enumerate(comparables, start=1):
            prop_id = comp.get("property_id", f"Comp #{idx}")
            locality = comp.get("locality", "Unknown")
            sqft = comp.get("area_sqft", 0)
            sale_price = comp.get("sale_price", 0)
            ppsf = comp.get("price_per_sqft", 0.0)
            sim_score = comp.get("similarity_score", 0.0)

            card = ctk.CTkFrame(self, fg_color=("#262C3A", "#191D28"), corner_radius=6)
            card.pack(fill="x", padx=6, pady=4)
            card.grid_columnconfigure(0, weight=1)

            # Top row: ID, Locality, Similarity
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=10, pady=(6, 2))
            top.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                top,
                text=f"#{idx}  ID: {prop_id}",
                font=ctk.CTkFont(weight="bold", size=12),
                text_color="#60A5FA",
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                top,
                text=f"{locality}",
                font=ctk.CTkFont(size=11),
                text_color="#9CA3AF",
                fg_color=("#374151", "#242C3A"),
                corner_radius=4,
                padx=6,
                pady=1,
            ).grid(row=0, column=1, sticky="w", padx=(10, 0))

            sim_text = "Exact Match" if sim_score == 0 else f"Dist: {sim_score:.3f}"
            ctk.CTkLabel(
                top,
                text=sim_text,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#34D399" if sim_score < 0.02 else "#FBBF24",
                fg_color=("#064E3B", "#064E3B") if sim_score < 0.02 else ("#78350F", "#78350F"),
                corner_radius=4,
                padx=6,
                pady=1,
            ).grid(row=0, column=2, sticky="e")

            # Bottom row: Sale Price, Sqft, Price/Sqft
            bot = ctk.CTkFrame(card, fg_color="transparent")
            bot.pack(fill="x", padx=10, pady=(2, 6))

            ctk.CTkLabel(
                bot,
                text=f"Sale Price: {format_lakhs(sale_price)} ({format_inr(sale_price)})",
                font=ctk.CTkFont(weight="bold", size=11),
                text_color="#E5E7EB",
            ).pack(side="left")

            ctk.CTkLabel(
                bot,
                text=f"  •  {sqft:,} sqft  •  ₹{ppsf:,.0f}/sqft",
                font=ctk.CTkFont(size=11),
                text_color="#9CA3AF",
            ).pack(side="left")


class EvidenceExplorer(ctk.CTkFrame):
    """Unified container toggling between TreeSHAP visualizer and Comparable Sales cards."""

    def __init__(self, master: Any, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Toggle bar
        self.toggle_var = ctk.StringVar(value="🧠 TreeSHAP Drivers")
        self.toggle_btn = ctk.CTkSegmentedButton(
            self,
            values=["🧠 TreeSHAP Drivers", "🏘️ Comparable Sales (5)"],
            variable=self.toggle_var,
            command=self._on_tab_change,
            height=30,
        )
        self.toggle_btn.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 6))

        # View frames
        self.shap_view = TreeSHAPVisualizer(self)
        self.comps_view = ComparablesExplorer(self)

        # Default view
        self.shap_view.grid(row=1, column=0, sticky="nsew")

    def _on_tab_change(self, selected: str) -> None:
        if "TreeSHAP" in selected:
            self.comps_view.grid_forget()
            self.shap_view.grid(row=1, column=0, sticky="nsew")
        else:
            self.shap_view.grid_forget()
            self.comps_view.grid(row=1, column=0, sticky="nsew")

    def update_evidence(self, result: dict[str, Any]) -> None:
        """Updates both TreeSHAP and Comparables views with new valuation result."""
        explanation = result.get("explanation", [])
        comparables = result.get("comparables", [])

        self.shap_view.display_explanation(explanation)
        self.comps_view.display_comparables(comparables)
