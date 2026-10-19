"""Automated tests for One-Click Presets and Model Diagnostics Hub."""

import time
import unittest

from realvalue.gui_adapter import ModelAdapter
from realvalue.gui_app import RealValueApp
from realvalue.gui_components import DEMO_PRESETS


class TestPresetsAndDiagnostics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = ModelAdapter(
            model_path="artifacts/model.joblib",
            data_path="data/Chennai houseing sale.csv",
            metrics_path="artifacts/metrics.json",
        )
        cls.adapter.load_sync()

    def test_presets_completeness_and_execution(self):
        non_empty_presets = {k: v for k, v in DEMO_PRESETS.items() if v is not None}
        self.assertEqual(len(non_empty_presets), 4)

        # Test each preset executes cleanly against the serving model
        for name, preset_data in non_empty_presets.items():
            result = self.adapter.predict(preset_data)
            self.assertIn("estimated_price", result)
            self.assertGreater(result["estimated_price"], 0)
            self.assertIn("explanation", result)
            self.assertIn("comparables", result)

        # Verify specific behavior of Outlier preset
        outlier = DEMO_PRESETS["⚠ Review Trigger (Outlier Case)"]
        outlier_res = self.adapter.predict(outlier)
        self.assertTrue(outlier_res["abstained"])
        self.assertGreaterEqual(len(outlier_res["review_reasons"]), 1)

    def test_preset_selection_triggers_ui_update(self):
        app = RealValueApp(adapter=self.adapter)
        app.withdraw()

        deadline = time.time() + 5.0
        while time.time() < deadline:
            app.update()
            if app.current_result is not None:
                break
            time.sleep(0.05)

        # Trigger Luxury preset
        app.input_form._on_preset_selected("💎 Luxury Villa (Anna Nagar)")
        app.update()

        self.assertEqual(app.input_form.area_var.get(), "Anna Nagar")
        self.assertIn("Cr", app.result_banner.price_label.cget("text"))
        self.assertIn("7,737", app.result_banner.consistency_label.cget("text"))

        # Trigger Outlier preset
        app.input_form._on_preset_selected("⚠ Review Trigger (Outlier Case)")
        app.update()

        self.assertIn("Under Review", app.result_banner.confidence_badge.cget("text"))
        self.assertTrue(app.current_result["abstained"])

        app.destroy()

    def test_diagnostics_cards_rendering(self):
        app = RealValueApp(adapter=self.adapter)
        app.withdraw()

        deadline = time.time() + 5.0
        while time.time() < deadline:
            app.update()
            if len(app.cards_frame.winfo_children()) >= 4:
                break
            time.sleep(0.05)

        app.update()

        # Check sample size pills
        self.assertEqual(len(app.split_frame.winfo_children()), 3)
        # Check 4 model comparison cards
        self.assertEqual(len(app.cards_frame.winfo_children()), 4)

        app.destroy()


if __name__ == "__main__":
    unittest.main()
