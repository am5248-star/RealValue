"""Headless integration test for RealValueApp window and background loading."""

import time
import unittest

from realvalue.gui_adapter import ModelAdapter
from realvalue.gui_app import RealValueApp


class TestRealValueApp(unittest.TestCase):
    def test_app_lifecycle_and_async_binding(self):
        adapter = ModelAdapter(
            model_path="artifacts/model.joblib",
            data_path="data/Chennai houseing sale.csv",
            metrics_path="artifacts/metrics.json",
        )
        app = RealValueApp(adapter=adapter)
        app.withdraw()  # keep hidden during automated test

        # Wait up to 5 seconds for async load to trigger UI update
        deadline = time.time() + 5.0
        while time.time() < deadline:
            app.update()
            if "Engine Ready" in app.status_badge.cget("text"):
                break
            time.sleep(0.05)

        app.update()

        self.assertTrue(adapter.is_loaded, "Adapter should have loaded asynchronously")
        self.assertIn("Engine Ready", app.status_badge.cget("text"))
        self.assertIn("Calibration & Trust", app.metrics_text_label.cget("text"))
        self.assertEqual(len(app.cards_frame.winfo_children()), 4)

        app.destroy()


if __name__ == "__main__":
    unittest.main()
