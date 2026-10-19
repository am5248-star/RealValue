"""Automated verification for ModelAdapter."""

import unittest
from pathlib import Path

from realvalue.gui_adapter import ModelAdapter


class TestModelAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = ModelAdapter(
            model_path="artifacts/model.joblib",
            data_path="data/Chennai houseing sale.csv",
            metrics_path="artifacts/metrics.json",
        )

    def test_sync_loading_and_prediction(self):
        self.assertFalse(self.adapter.is_loaded)
        self.adapter.load_sync()
        self.assertTrue(self.adapter.is_loaded)

        default_prop = self.adapter.get_default_property()
        result = self.adapter.predict(default_prop)

        self.assertIn("estimated_price", result)
        self.assertGreater(result["estimated_price"], 0)
        self.assertIn("interval_low", result)
        self.assertIn("interval_high", result)
        self.assertIn("explanation", result)
        self.assertIsInstance(result["explanation"], list)
        self.assertGreaterEqual(len(result["explanation"]), 1)
        self.assertIn("comparables", result)
        self.assertIsInstance(result["comparables"], list)

        status = self.adapter.get_status_info()
        self.assertTrue(status["is_loaded"])
        self.assertEqual(status["model_type"], "xgboost")
        self.assertGreater(status["rows_count"], 0)

    def test_async_loading(self):
        adapter = ModelAdapter()
        loaded_event = []

        def on_success(ad):
            loaded_event.append(ad.is_loaded)

        thread = adapter.load_async(on_success=on_success)
        thread.join(timeout=10.0)

        self.assertEqual(loaded_event, [True])
        self.assertTrue(adapter.is_loaded)


if __name__ == "__main__":
    unittest.main()
