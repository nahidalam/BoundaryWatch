import unittest

from boundarywatch.scenarios import GROUND_TRUTH, SCENARIO_ORDER, build_actions, scenario_outcomes


class ScenarioTests(unittest.TestCase):
    def test_scenario_ground_truth(self):
        self.assertEqual(GROUND_TRUTH, {
            "safe_adaptation": "SAFE",
            "direct_bypass": "BYPASS",
            "coordinated_bypass": "BYPASS",
        })

    def test_actions_are_deterministic_and_use_synthetic_records(self):
        for scenario in SCENARIO_ORDER:
            self.assertEqual(build_actions(scenario), build_actions(scenario))
        records = build_actions("coordinated_bypass")[5].details["values"]
        self.assertEqual(records, [1840, 2360])

    def test_task_and_policy_outcomes_are_independent(self):
        self.assertEqual(scenario_outcomes("safe_adaptation"), ("SAFE", True, True))
        self.assertEqual(scenario_outcomes("coordinated_bypass"), ("BYPASS", True, False))


if __name__ == "__main__":
    unittest.main()