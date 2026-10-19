"""Automated verification for TreeSHAP Visualizer and Comparables Explorer."""

import time
import unittest

from realvalue.gui_adapter import ModelAdapter
from realvalue.gui_app import RealValueApp
from realvalue.gui_evidence import format_feature_name, TreeSHAPVisualizer, ComparablesExplorer, EvidenceExplorer


class TestEvidenceComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = ModelAdapter(
            model_path="artifacts/model.joblib",
            data_path="data/Chennai houseing sale.csv",
            metrics_path="artifacts/metrics.json",
        )
        cls.adapter.load_sync()

    def test_feature_name_formatting(self):
        self.assertEqual(format_feature_name("BUILDTYPE_Commercial"), "Build: Commercial")
        self.assertEqual(format_feature_name("AREA_Karapakkam"), "Locality: Karapakkam")
        self.assertEqual(format_feature_name("MZZONE_RL"), "Zone: RL")
        self.assertEqual(format_feature_name("INT_SQFT"), "Floor Area (SqFt)")
        self.assertEqual(format_feature_name("HOUSE_AGE"), "Property Age")

    def test_treeshap_visualizer_rendering(self):
        app = RealValueApp(adapter=self.adapter)
        app.withdraw()

        viz = TreeSHAPVisualizer(app)
        sample_exp = [
            {"feature": "BUILDTYPE_Commercial", "contribution": 2060816.25, "method": "TreeSHAP"},
            {"feature": "AREA_Karapakkam", "contribution": -1938969.38, "method": "TreeSHAP"},
            {"feature": "INT_SQFT", "contribution": -1816845.25, "method": "TreeSHAP"},
        ]
        viz.display_explanation(sample_exp)
        self.assertEqual(len(viz.ax.patches), 3)

        # Test empty explanation
        viz.display_explanation([])
        self.assertEqual(len(viz.ax.patches), 0)

        app.destroy()

    def test_comparables_explorer_rendering(self):
        app = RealValueApp(adapter=self.adapter)
        app.withdraw()

        comps_exp = ComparablesExplorer(app)
        sample_comps = [
            {
                "property_id": "P05180",
                "locality": "Karapakkam",
                "area_sqft": 1003,
                "sale_price": 10090000,
                "price_per_sqft": 10059.82,
                "similarity_score": 0.0,
            },
            {
                "property_id": "P03583",
                "locality": "Karapakkam",
                "area_sqft": 1028,
                "sale_price": 8255500,
                "price_per_sqft": 8030.64,
                "similarity_score": 0.007,
            },
        ]
        comps_exp.display_comparables(sample_comps)
        # Should contain cards
        self.assertGreater(len(comps_exp.winfo_children()), 1)

        app.destroy()

    def test_evidence_toggle_and_app_integration(self):
        app = RealValueApp(adapter=self.adapter)
        app.withdraw()

        # Wait for auto valuation
        deadline = time.time() + 5.0
        while time.time() < deadline:
            app.update()
            if app.current_result is not None:
                break
            time.sleep(0.05)

        app.update()

        self.assertIsNotNone(app.current_result)
        # Verify TreeSHAP bars rendered
        self.assertGreater(len(app.evidence_explorer.shap_view.ax.patches), 0)

        # Toggle to comparables
        app.evidence_explorer._on_tab_change("🏘️ Comparable Sales (5)")
        app.update()
        self.assertGreater(len(app.evidence_explorer.comps_view.winfo_children()), 1)

        # Toggle back to TreeSHAP
        app.evidence_explorer._on_tab_change("🧠 TreeSHAP Drivers")
        app.update()
        self.assertGreater(len(app.evidence_explorer.shap_view.ax.patches), 0)

        app.destroy()


if __name__ == "__main__":
    unittest.main()
