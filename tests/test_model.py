import unittest
from dataclasses import fields

from boundarywatch.model import Action, TraceMessage, VisibleMessage


class DataModelTests(unittest.TestCase):
    def test_visible_message_cannot_hold_hidden_action_label(self):
        names = {field.name for field in fields(VisibleMessage)}
        self.assertNotIn("action", names)
        self.assertNotIn("ground_truth", names)

    def test_internal_trace_preserves_action_label(self):
        action = Action("m1", "B", "A", "gateway", "request_restricted_records", {})
        message = TraceMessage("m1", "B", "A", "gateway", "request", "Please help.", 0, action.action)
        self.assertEqual(message.action, "request_restricted_records")


if __name__ == "__main__":
    unittest.main()