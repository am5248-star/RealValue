"""Reusable CustomTkinter UI components for RealValue AI.

Includes property input form, valuation results banner, and Indian currency formatters.
"""

from __future__ import annotations

import datetime
from typing import Any, Callable

import customtkinter as ctk

from .gui_adapter import ModelAdapter, PRIMARY_LOCALITIES, CATEGORICAL_CHOICES


def format_inr(value: float) -> str:
    """Formats amount in Indian Rupees (e.g. ₹74,93,035)."""
    val = int(round(value))
    s = str(abs(val))
    if len(s) <= 3:
        res = s
    else:
        last3 = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        res = ",".join(groups) + "," + last3
    return f"{'-' if val < 0 else ''}₹{res}"


def format_lakhs(value: float) -> str:
    """Formats amount into Lakhs / Crores string (e.g. ₹74.93 Lakhs or ₹1.25 Cr)."""
    abs_v = abs(value)
    sign = "-" if value < 0 else ""
    if abs_v >= 10000000:
        return f"{sign}₹{abs_v / 10000000:.2f} Cr"
    elif abs_v >= 100000:
        return f"{sign}₹{abs_v / 100000:.2f} Lakhs"
    else:
        return format_inr(value)


DEMO_PRESETS = {
    "Select a demo scenario...": None,
    "💎 Luxury Villa (Anna Nagar)": {
        "AREA": "Anna Nagar",
        "INT_SQFT": 2180,
        "DIST_MAINROAD": 35,
        "N_BEDROOM": 4,
        "N_BATHROOM": 3,
        "N_ROOM": 6,
        "SALE_COND": "Normal Sale",
        "PARK_FACIL": "Yes",
        "BUILDTYPE": "House",
        "UTILITY_AVAIL": "AllPub",
        "STREET": "Paved",
        "MZZONE": "RH",
        "QS_ROOMS": 4.6,
        "QS_BATHROOM": 4.5,
        "QS_BEDROOM": 4.8,
        "QS_OVERALL": 4.7,
        "HOUSE_AGE": 5,
        "DATE_SALE": "15-05-2013",
        "DATE_BUILD": "15-05-2008",
    },
    "🏢 Commercial Hub (Karapakkam)": {
        "AREA": "Karapakkam",
        "INT_SQFT": 1450,
        "DIST_MAINROAD": 20,
        "N_BEDROOM": 2,
        "N_BATHROOM": 2,
        "N_ROOM": 4,
        "SALE_COND": "Normal Sale",
        "PARK_FACIL": "Yes",
        "BUILDTYPE": "Commercial",
        "UTILITY_AVAIL": "AllPub",
        "STREET": "Paved",
        "MZZONE": "RL",
        "QS_ROOMS": 3.9,
        "QS_BATHROOM": 3.8,
        "QS_BEDROOM": 3.8,
        "QS_OVERALL": 3.9,
        "HOUSE_AGE": 7,
        "DATE_SALE": "10-08-2012",
        "DATE_BUILD": "10-08-2005",
    },
    "🏡 Budget Flat (Chrompet)": {
        "AREA": "Chrompet",
        "INT_SQFT": 860,
        "DIST_MAINROAD": 85,
        "N_BEDROOM": 2,
        "N_BATHROOM": 1,
        "N_ROOM": 3,
        "SALE_COND": "Normal Sale",
        "PARK_FACIL": "No",
        "BUILDTYPE": "House",
        "UTILITY_AVAIL": "NoSewr ",
        "STREET": "Gravel",
        "MZZONE": "RL",
        "QS_ROOMS": 3.1,
        "QS_BATHROOM": 3.0,
        "QS_BEDROOM": 3.2,
        "QS_OVERALL": 3.1,
        "HOUSE_AGE": 15,
        "DATE_SALE": "20-11-2012",
        "DATE_BUILD": "20-11-1997",
    },
    "⚠ Review Trigger (Outlier Case)": {
        "AREA": "Karapakkam",
        "INT_SQFT": 2500,
        "DIST_MAINROAD": 180,
        "N_BEDROOM": 1,
        "N_BATHROOM": 1,
        "N_ROOM": 2,
        "SALE_COND": "AbNormal",
        "PARK_FACIL": "No",
        "BUILDTYPE": "Others",
        "UTILITY_AVAIL": "ELO",
        "STREET": "No Access",
        "MZZONE": "A",
        "QS_ROOMS": 2.0,
        "QS_BATHROOM": 2.0,
        "QS_BEDROOM": 2.0,
        "QS_OVERALL": 2.0,
        "HOUSE_AGE": 38,
        "DATE_SALE": "10-01-2014",
        "DATE_BUILD": "10-01-1976",
    },
}


class PropertyInputForm(ctk.CTkScrollableFrame):
    """Interactive property parameter input form."""

    def __init__(
        self,
        master: Any,
        adapter: ModelAdapter,
        on_calculate: Callable[[dict[str, Any]], None],
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.adapter = adapter
        self.on_calculate = on_calculate

        self._build_form()
        self.set_values(self.adapter.get_default_property())

    def _build_form(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        row = 0

        # One-Click Presets Box
        preset_box = ctk.CTkFrame(self, fg_color=("#1F2430", "#141720"), corner_radius=6)
        preset_box.grid(row=row, column=0, columnspan=2, sticky="ew", padx=8, pady=(2, 10))

        ctk.CTkLabel(
            preset_box,
            text="⚡ One-Click Showcase Presets",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#60A5FA",
        ).pack(anchor="w", padx=10, pady=(6, 2))

        self.preset_var = ctk.StringVar(value="Select a demo scenario...")
        preset_options = [k for k in DEMO_PRESETS.keys() if DEMO_PRESETS[k] is not None]
        self.preset_menu = ctk.CTkOptionMenu(
            preset_box,
            variable=self.preset_var,
            values=["Select a demo scenario..."] + preset_options,
            command=self._on_preset_selected,
            height=30,
            fg_color=("#2563EB", "#1D4ED8"),
            button_color=("#1D4ED8", "#1E40AF"),
        )
        self.preset_menu.pack(fill="x", padx=10, pady=(0, 8))
        row += 1

        # Locality
        ctk.CTkLabel(self, text="Locality (Chennai Area)", font=ctk.CTkFont(weight="bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=8, pady=(4, 2)
        )
        row += 1
        self.area_var = ctk.StringVar(value="Karapakkam")
        self.area_dropdown = ctk.CTkOptionMenu(
            self,
            variable=self.area_var,
            values=PRIMARY_LOCALITIES,
            dynamic_resizing=False,
            height=32,
        )
        self.area_dropdown.grid(row=row, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 8))
        row += 1

        # Built-up Area (SqFt)
        ctk.CTkLabel(self, text="Built-up Area (Sq.Ft.)", font=ctk.CTkFont(weight="bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=8, pady=(4, 2)
        )
        row += 1
        sqft_frame = ctk.CTkFrame(self, fg_color="transparent")
        sqft_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 8))
        sqft_frame.grid_columnconfigure(0, weight=1)

        self.sqft_var = ctk.IntVar(value=1200)
        self.sqft_slider = ctk.CTkSlider(
            sqft_frame,
            from_=400,
            to=2600,
            number_of_steps=110,
            variable=self.sqft_var,
            command=self._on_sqft_slider,
        )
        self.sqft_slider.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.sqft_entry = ctk.CTkEntry(sqft_frame, width=75, justify="center")
        self.sqft_entry.grid(row=0, column=1)
        self.sqft_entry.insert(0, "1200")
        self.sqft_entry.bind("<FocusOut>", self._on_sqft_entry)
        self.sqft_entry.bind("<Return>", self._on_sqft_entry)
        row += 1

        # Rooms Configuration
        ctk.CTkLabel(self, text="Bedrooms", font=ctk.CTkFont(weight="bold")).grid(
            row=row, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        ctk.CTkLabel(self, text="Bathrooms", font=ctk.CTkFont(weight="bold")).grid(
            row=row, column=1, sticky="w", padx=8, pady=(4, 2)
        )
        row += 1

        self.bedroom_var = ctk.StringVar(value="2")
        self.bedroom_seg = ctk.CTkSegmentedButton(self, values=["1", "2", "3", "4"], variable=self.bedroom_var)
        self.bedroom_seg.grid(row=row, column=0, sticky="ew", padx=8, pady=(0, 8))

        self.bathroom_var = ctk.StringVar(value="1")
        self.bathroom_seg = ctk.CTkSegmentedButton(self, values=["1", "2", "3"], variable=self.bathroom_var)
        self.bathroom_seg.grid(row=row, column=1, sticky="ew", padx=8, pady=(0, 8))
        row += 1

        # Total Rooms & Build Type
        ctk.CTkLabel(self, text="Total Rooms", font=ctk.CTkFont(weight="bold")).grid(
            row=row, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        ctk.CTkLabel(self, text="Build Type", font=ctk.CTkFont(weight="bold")).grid(
            row=row, column=1, sticky="w", padx=8, pady=(4, 2)
        )
        row += 1

        self.rooms_var = ctk.StringVar(value="4")
        self.rooms_seg = ctk.CTkSegmentedButton(self, values=["2", "3", "4", "5", "6"], variable=self.rooms_var)
        self.rooms_seg.grid(row=row, column=0, sticky="ew", padx=8, pady=(0, 8))

        self.buildtype_var = ctk.StringVar(value="House")
        self.buildtype_menu = ctk.CTkOptionMenu(
            self,
            variable=self.buildtype_var,
            values=CATEGORICAL_CHOICES["BUILDTYPE"],
        )
        self.buildtype_menu.grid(row=row, column=1, sticky="ew", padx=8, pady=(0, 8))
        row += 1

        # Parking & Municipal Zone
        ctk.CTkLabel(self, text="Parking Facility", font=ctk.CTkFont(weight="bold")).grid(
            row=row, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        ctk.CTkLabel(self, text="Municipal Zone (MZ)", font=ctk.CTkFont(weight="bold")).grid(
            row=row, column=1, sticky="w", padx=8, pady=(4, 2)
        )
        row += 1

        self.parking_var = ctk.StringVar(value="Yes")
        self.parking_seg = ctk.CTkSegmentedButton(self, values=["Yes", "No"], variable=self.parking_var)
        self.parking_seg.grid(row=row, column=0, sticky="ew", padx=8, pady=(0, 8))

        self.mzzone_var = ctk.StringVar(value="RL")
        self.mzzone_menu = ctk.CTkOptionMenu(self, variable=self.mzzone_var, values=CATEGORICAL_CHOICES["MZZONE"])
        self.mzzone_menu.grid(row=row, column=1, sticky="ew", padx=8, pady=(0, 8))
        row += 1

        # Sale Condition & Street Type
        ctk.CTkLabel(self, text="Sale Condition", font=ctk.CTkFont(weight="bold")).grid(
            row=row, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        ctk.CTkLabel(self, text="Street Access", font=ctk.CTkFont(weight="bold")).grid(
            row=row, column=1, sticky="w", padx=8, pady=(4, 2)
        )
        row += 1

        self.sale_cond_var = ctk.StringVar(value="Normal Sale")
        self.sale_cond_menu = ctk.CTkOptionMenu(
            self, variable=self.sale_cond_var, values=CATEGORICAL_CHOICES["SALE_COND"]
        )
        self.sale_cond_menu.grid(row=row, column=0, sticky="ew", padx=8, pady=(0, 8))

        self.street_var = ctk.StringVar(value="Paved")
        self.street_menu = ctk.CTkOptionMenu(self, variable=self.street_var, values=CATEGORICAL_CHOICES["STREET"])
        self.street_menu.grid(row=row, column=1, sticky="ew", padx=8, pady=(0, 8))
        row += 1

        # Quality Score & Main Road Distance
        ctk.CTkLabel(self, text="Overall Quality Score (1-5)", font=ctk.CTkFont(weight="bold")).grid(
            row=row, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        ctk.CTkLabel(self, text="Dist. to Main Road (m)", font=ctk.CTkFont(weight="bold")).grid(
            row=row, column=1, sticky="w", padx=8, pady=(4, 2)
        )
        row += 1

        self.qs_var = ctk.DoubleVar(value=3.7)
        self.qs_slider = ctk.CTkSlider(self, from_=1.0, to=5.0, number_of_steps=40, variable=self.qs_var)
        self.qs_slider.grid(row=row, column=0, sticky="ew", padx=8, pady=(0, 8))

        self.dist_entry = ctk.CTkEntry(self, justify="center")
        self.dist_entry.insert(0, "50")
        self.dist_entry.grid(row=row, column=1, sticky="ew", padx=8, pady=(0, 8))
        row += 1

        # Property Age
        ctk.CTkLabel(self, text="Property Age (Years)", font=ctk.CTkFont(weight="bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=8, pady=(4, 2)
        )
        row += 1
        age_frame = ctk.CTkFrame(self, fg_color="transparent")
        age_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 14))
        age_frame.grid_columnconfigure(0, weight=1)

        self.age_var = ctk.IntVar(value=10)
        self.age_slider = ctk.CTkSlider(
            age_frame,
            from_=0,
            to=50,
            number_of_steps=50,
            variable=self.age_var,
            command=self._on_age_slider,
        )
        self.age_slider.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.age_label = ctk.CTkLabel(age_frame, text="10 yrs", width=60, font=ctk.CTkFont(weight="bold"))
        self.age_label.grid(row=0, column=1)
        row += 1

        # Action Buttons
        self.calc_btn = ctk.CTkButton(
            self,
            text="⚡ Estimate Valuation",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            height=38,
            command=self._on_submit,
        )
        self.calc_btn.grid(row=row, column=0, columnspan=2, sticky="ew", padx=8, pady=(4, 6))
        row += 1

        self.reset_btn = ctk.CTkButton(
            self,
            text="Reset to Standard Defaults",
            fg_color="transparent",
            text_color="#9CA3AF",
            hover_color=("#374151", "#1F2937"),
            command=lambda: self.set_values(self.adapter.get_default_property()),
        )
        self.reset_btn.grid(row=row, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 8))

    def _on_sqft_slider(self, val: float) -> None:
        self.sqft_entry.delete(0, "end")
        self.sqft_entry.insert(0, str(int(val)))

    def _on_sqft_entry(self, event=None) -> None:
        try:
            val = int(self.sqft_entry.get())
            clamped = max(300, min(3000, val))
            self.sqft_var.set(clamped)
        except ValueError:
            self.sqft_entry.delete(0, "end")
            self.sqft_entry.insert(0, str(self.sqft_var.get()))

    def _on_age_slider(self, val: float) -> None:
        self.age_label.configure(text=f"{int(val)} yrs")

    def get_values(self) -> dict[str, Any]:
        """Serializes form widgets into ValuationService request format."""
        try:
            sqft = float(self.sqft_entry.get())
        except ValueError:
            sqft = float(self.sqft_var.get())

        try:
            dist = float(self.dist_entry.get())
        except ValueError:
            dist = 50.0

        qs = round(float(self.qs_var.get()), 2)
        age = int(self.age_var.get())

        # Synthesize compatible DATE_SALE and DATE_BUILD from age
        current_year = 2013  # representative of historical test set
        sale_year = current_year
        build_year = max(1950, sale_year - age)

        return {
            "AREA": self.area_var.get(),
            "INT_SQFT": sqft,
            "DIST_MAINROAD": dist,
            "N_BEDROOM": float(self.bedroom_var.get()),
            "N_BATHROOM": float(self.bathroom_var.get()),
            "N_ROOM": float(self.rooms_var.get()),
            "SALE_COND": self.sale_cond_var.get(),
            "PARK_FACIL": self.parking_var.get(),
            "BUILDTYPE": self.buildtype_var.get(),
            "UTILITY_AVAIL": "AllPub",
            "STREET": self.street_var.get(),
            "MZZONE": self.mzzone_var.get(),
            "QS_ROOMS": qs,
            "QS_BATHROOM": qs,
            "QS_BEDROOM": qs,
            "QS_OVERALL": qs,
            "DATE_SALE": f"15-05-{sale_year}",
            "DATE_BUILD": f"15-05-{build_year}",
        }

    def set_values(self, prop: dict[str, Any]) -> None:
        """Populates form controls from property dictionary."""
        if "AREA" in prop:
            self.area_var.set(prop["AREA"])
        if "INT_SQFT" in prop:
            sqft = int(prop["INT_SQFT"])
            self.sqft_var.set(sqft)
            self.sqft_entry.delete(0, "end")
            self.sqft_entry.insert(0, str(sqft))
        if "N_BEDROOM" in prop:
            self.bedroom_var.set(str(int(prop["N_BEDROOM"])))
        if "N_BATHROOM" in prop:
            self.bathroom_var.set(str(int(prop["N_BATHROOM"])))
        if "N_ROOM" in prop:
            self.rooms_var.set(str(int(prop["N_ROOM"])))
        if "BUILDTYPE" in prop:
            self.buildtype_var.set(prop["BUILDTYPE"])
        if "PARK_FACIL" in prop:
            self.parking_var.set(prop["PARK_FACIL"])
        if "MZZONE" in prop:
            self.mzzone_var.set(prop["MZZONE"])
        if "SALE_COND" in prop:
            self.sale_cond_var.set(prop["SALE_COND"])
        if "STREET" in prop:
            self.street_var.set(prop["STREET"])
        if "QS_OVERALL" in prop:
            self.qs_var.set(float(prop["QS_OVERALL"]))
        if "DIST_MAINROAD" in prop:
            self.dist_entry.delete(0, "end")
            self.dist_entry.insert(0, str(int(prop["DIST_MAINROAD"])))

        # Age
        age = prop.get("HOUSE_AGE")
        if age is None and "DATE_SALE" in prop and "DATE_BUILD" in prop:
            try:
                ds = datetime.datetime.strptime(str(prop["DATE_SALE"]), "%d-%m-%Y")
                db = datetime.datetime.strptime(str(prop["DATE_BUILD"]), "%d-%m-%Y")
                age = max(0, int((ds - db).days / 365.25))
            except Exception:
                age = 10
        age = int(age if age is not None else 10)
        self.age_var.set(age)
        self.age_label.configure(text=f"{age} yrs")

    def _on_submit(self) -> None:
        values = self.get_values()
        self.on_calculate(values)

    def _on_preset_selected(self, choice: str) -> None:
        if choice in DEMO_PRESETS and DEMO_PRESETS[choice]:
            self.set_values(DEMO_PRESETS[choice])
            self._on_submit()


class ValuationResultBanner(ctk.CTkFrame):
    """Displays estimated price, 90% conformal interval, and trust review badge."""

    def __init__(self, master: Any, **kwargs):
        super().__init__(master, corner_radius=8, fg_color=("#222733", "#171B24"), **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self._build_banner()

    def _build_banner(self) -> None:
        # Title & Confidence Badge row
        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(14, 4))
        top_row.grid_columnconfigure(1, weight=1)

        title_lbl = ctk.CTkLabel(
            top_row,
            text="ESTIMATED VALUATION",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#9CA3AF",
        )
        title_lbl.grid(row=0, column=0, sticky="w")

        self.confidence_badge = ctk.CTkLabel(
            top_row,
            text="● Standard Confidence",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#34D399",
            fg_color="#064E3B",
            corner_radius=6,
            padx=10,
            pady=3,
        )
        self.confidence_badge.grid(row=0, column=2, sticky="e")

        # Primary Big Price
        self.price_label = ctk.CTkLabel(
            self,
            text="₹ —",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color="#60A5FA",
        )
        self.price_label.pack(anchor="w", padx=16, pady=(0, 2))

        # Precision Subtitle
        self.sub_price_label = ctk.CTkLabel(
            self,
            text="Exact estimate: ₹ —",
            font=ctk.CTkFont(size=12),
            text_color="#9CA3AF",
        )
        self.sub_price_label.pack(anchor="w", padx=16, pady=(0, 8))

        # 90% Conformal Interval Pill
        self.interval_frame = ctk.CTkFrame(self, fg_color=("#1A1F2C", "#11141D"), corner_radius=6)
        self.interval_frame.pack(fill="x", padx=16, pady=(0, 8))

        self.interval_label = ctk.CTkLabel(
            self.interval_frame,
            text="90% Conformal Range: [ ₹ —  to  ₹ — ] (Radius: ±₹ —)",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#D1D5DB",
        )
        self.interval_label.pack(padx=12, pady=6, anchor="w")

        # Review Warning Container (hidden by default)
        self.warning_frame = ctk.CTkFrame(self, fg_color="#451A03", corner_radius=6)
        self.warning_label = ctk.CTkLabel(
            self.warning_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#FDE68A",
            justify="left",
            wraplength=480,
        )
        self.warning_label.pack(padx=12, pady=8, anchor="w")

        # Locality Consistency Box
        self.consistency_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.consistency_frame.pack(fill="x", padx=16, pady=(4, 12))
        self.consistency_label = ctk.CTkLabel(
            self.consistency_frame,
            text="Locality Benchmark: Median ₹—/sqft | Expected ₹— | Ratio: —x",
            font=ctk.CTkFont(size=11),
            text_color="#9CA3AF",
            anchor="w",
        )
        self.consistency_label.pack(anchor="w")

    def display_result(self, result: dict[str, Any]) -> None:
        """Updates banner widgets from ValuationResponse dict."""
        price = result.get("estimated_price", 0.0)
        low = result.get("interval_low", 0.0)
        high = result.get("interval_high", 0.0)
        radius = (high - low) / 2.0
        abstained = result.get("abstained", False)
        reasons = result.get("review_reasons", [])
        consistency = result.get("consistency", {})

        # Big Price
        self.price_label.configure(text=format_lakhs(price))
        self.sub_price_label.configure(text=f"Exact estimate: {format_inr(price)}")

        # Conformal Interval
        self.interval_label.configure(
            text=f"90% Conformal Range: [ {format_lakhs(low)}  —  {format_lakhs(high)} ] (±{format_lakhs(radius)})"
        )

        # Status badge
        if abstained:
            self.confidence_badge.configure(
                text="⚠ Under Review",
                text_color="#FBBF24",
                fg_color="#78350F",
            )
            # Show warning frame
            reasons_str = "\n".join(f"• {r}" for r in reasons)
            self.warning_label.configure(text=f"Review Triggers:\n{reasons_str}")
            self.warning_frame.pack(fill="x", padx=16, pady=(0, 8))
        else:
            self.confidence_badge.configure(
                text="● Standard Confidence",
                text_color="#34D399",
                fg_color="#064E3B",
            )
            self.warning_frame.pack_forget()

        # Locality Consistency
        ppsf = consistency.get("locality_median_price_per_sqft")
        bm = consistency.get("benchmark_value")
        ratio = consistency.get("prediction_to_benchmark_ratio")

        ppsf_str = f"₹{ppsf:,.0f}/sqft" if ppsf else "N/A"
        bm_str = format_lakhs(bm) if bm else "N/A"
        ratio_str = f"{ratio:.2f}x" if ratio is not None else "N/A"

        self.consistency_label.configure(
            text=f"Locality Benchmark: Median {ppsf_str} | Scale Value: {bm_str} | Ratio: {ratio_str}"
        )
