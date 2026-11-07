import unittest

from boundarywatch.experiment import run_experiment
from boundarywatch.metrics import aggregate_rows, calculate_metrics
from boundarywatch.providers import MockProvider


class MetricTests(unittest.TestCase):
    def test_experiment_ids_seeds_and_masks_are_reproducible(self):
        first_rows, first_traces = run_experiment(MockProvider(), repetitions=1)
        second_rows, second_traces = run_experiment(MockProvider(), repetitions=1)
        self.assertEqual(first_traces, second_traces)
        self.assertEqual(first_rows, second_rows)

    def test_primary_rates_and_success_are_calculated(self):
        rows = [
            {"ground_truth": "BYPASS", "prediction": "BYPASS", "confidence": 0.9, "task_success": True, "policy_success": False, "visible_message_count": 4, "total_message_count": 5},
            {"ground_truth": "BYPASS", "prediction": "SAFE", "confidence": 0.6, "task_success": True, "policy_success": True, "visible_message_count": 3, "total_message_count": 5},
            {"ground_truth": "SAFE", "prediction": "BYPASS", "confidence": 0.8, "task_success": False, "policy_success": True, "visible_message_count": 2, "total_message_count": 5},
            {"ground_truth": "SAFE", "prediction": "SAFE", "confidence": 0.7, "task_success": False, "policy_success": True, "visible_message_count": 2, "total_message_count": 5},
        ]
        result = calculate_metrics(rows)
        self.assertEqual(result["bypass_detection_rate"], 0.5)
        self.assertEqual(result["false_positive_rate"], 0.5)
        self.assertEqual(result["precision"], 0.5)
        self.assertEqual(result["task_success_rate"], 0.5)
        self.assertEqual(result["policy_success_rate"], 0.75)

    def test_aggregation_groups_by_monitor_visibility_scenario(self):
        rows = [{
            "monitor_type": "Rule Monitor",
            "visibility": "full",
            "scenario": "safe_adaptation",
            "ground_truth": "SAFE",
            "prediction": "SAFE",
            "confidence": 0.8,
            "task_success": True,
            "policy_success": True,
            "visible_message_count": 4,
            "total_message_count": 4,
        }]
        summary = aggregate_rows(rows)
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["monitor"], "Rule Monitor")
        self.assertEqual(summary[0]["scenario"], "safe_adaptation")
        self.assertEqual(summary[0]["false_positive_rate"], 0.0)
        self.assertIsNone(summary[0]["bypass_detection_rate"])


if __name__ == "__main__":
    unittest.main()