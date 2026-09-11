import unittest

from ros2_runtime_guardian.models import Finding, Severity
from ros2_runtime_guardian.recovery import RecoveryConfig, RecoveryController


def finding(severity=Severity.ERROR):
    return Finding("demo", severity, "/robot/demo", 42, "demo", {}, "restart")


class RecoveryTests(unittest.TestCase):
    def test_default_is_dry_run(self):
        controller = RecoveryController(RecoveryConfig(cooldown_s=10, max_attempts=2))
        decision = controller.decide(finding(), now=0)
        self.assertEqual(decision.action, "request_supervised_restart")
        self.assertFalse(decision.execute)
        self.assertEqual(decision.attempt, 1)

    def test_cooldown_suppresses_restart_storm(self):
        controller = RecoveryController(RecoveryConfig(cooldown_s=10, max_attempts=2))
        controller.decide(finding(), now=0)
        decision = controller.decide(finding(), now=5)
        self.assertEqual(decision.action, "observe")
        self.assertIn("cooldown", decision.reason)

    def test_budget_escalates_after_limit(self):
        controller = RecoveryController(RecoveryConfig(cooldown_s=1, max_attempts=2))
        controller.decide(finding(), now=0)
        controller.decide(finding(), now=2)
        decision = controller.decide(finding(), now=4)
        self.assertEqual(decision.action, "escalate")
        self.assertEqual(decision.attempt, 2)


if __name__ == "__main__":
    unittest.main()

