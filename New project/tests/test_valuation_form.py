"""Automated tests for Valuation Calculator form and Results Banner."""

import time
import unittest

from realvalue.gui_adapter import ModelAdapter
from realvalue.gui_app import RealValueApp
from realvalue.gui_components import format_inr, format_lakhs, PropertyInputForm, ValuationResultBanner


class TestValuationFormAndBanner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = ModelAdapter(
            model_path="artifacts/model.joblib",
            data_path="data/Chennai houseing sale.csv",
            metrics_path="artifacts/metrics.json",
        )
        cls.adapter.load_sync()

    def test_currency_formatters(self):
        self.assertEqual(format_inr(7493035), "₹74,93,035")
        self.assertEqual(format_inr(500), "₹500")
        self.assertIn("Lakhs", format_lakhs(7493035))
        self.assertIn("Cr", format_lakhs(12500000))

    def test_form_serialization(self):
        app = RealValueApp(adapter=self.adapter)
        app.withdraw()

        form = app.input_form
        values = form.get_values()

        self.assertIn("AREA", values)
        self.assertIn("INT_SQFT", values)
        self.assertIn("N_BEDROOM", values)
        self.assertIn("N_BATHROOM", values)
        self.assertIn("N_ROOM", values)
        self.assertIn("BUILDTYPE", values)
        self.assertIn("PARK_FACIL", values)
        self.assertIn("MZZONE", values)
        self.assertIn("DATE_SALE", values)
        self.assertIn("DATE_BUILD", values)

        # Predict with extracted values
        pred = self.adapter.predict(values)
        self.assertGreater(pred["estimated_price"], 0)
        self.assertIn("interval_low", pred)
        self.assertIn("interval_high", pred)

        app.destroy()

    def test_results_banner_rendering(self):
        app = RealValueApp(adapter=self.adapter)
        app.withdraw()

        # Test standard confidence display
        standard_result = {
            "estimated_price": 7500000.0,
            "interval_low": 7180000.0,
            "interval_high": 7820000.0,
            "abstained": False,
            "review_reasons": [],
            "consistency": {
                "locality_median_price_per_sqft": 6500.0,
                "benchmark_value": 7800000.0,
                "prediction_to_benchmark_ratio": 0.96,
            },
        }
        app.result_banner.display_result(standard_result)
        self.assertIn("Standard", app.result_banner.confidence_badge.cget("text"))
        self.assertIn("75.00 Lakhs", app.result_banner.price_label.cget("text"))

        # Test review / abstention display
        review_result = {
            "estimated_price": 4000000.0,
            "interval_low": 3680000.0,
            "interval_high": 4320000.0,
            "abstained": True,
            "review_reasons": ["Fewer than three comparable transactions"],
            "consistency": {
                "locality_median_price_per_sqft": 6500.0,
                "benchmark_value": 7800000.0,
                "prediction_to_benchmark_ratio": 0.51,
            },
        }
        app.result_banner.display_result(review_result)
        self.assertIn("Under Review", app.result_banner.confidence_badge.cget("text"))
        self.assertIn("Fewer than three", app.result_banner.warning_label.cget("text"))

        app.destroy()

    def test_full_app_integration_valuation(self):
        app = RealValueApp(adapter=self.adapter)
        app.withdraw()

        deadline = time.time() + 5.0
        while time.time() < deadline:
            app.update()
            if app.current_result is not None:
                break
            time.sleep(0.05)

        app.update()

        self.assertIsNotNone(app.current_result)
        self.assertGreater(app.current_result["estimated_price"], 0)
        self.assertIn("₹", app.result_banner.price_label.cget("text"))
        self.assertIn("Conformal", app.result_banner.interval_label.cget("text"))

        app.destroy()


if __name__ == "__main__":
    unittest.main()
