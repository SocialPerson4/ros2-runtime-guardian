import unittest

from ros2_runtime_guardian.correlator import CorrelationConfig, CrossLayerCorrelator
from ros2_runtime_guardian.models import NodeSnapshot, ProcessSnapshot, Severity


def process(**changes):
    values = {
        "pid": 42,
        "name": "demo_node",
        "state": "S",
        "cpu_percent": 10.0,
        "rss_bytes": 64 * 1024 * 1024,
        "threads": 4,
        "fd_count": 20,
        "cmdline": "demo_node",
    }
    values.update(changes)
    return ProcessSnapshot(**values)


class CorrelatorTests(unittest.TestCase):
    def setUp(self):
        self.engine = CrossLayerCorrelator(CorrelationConfig())

    def test_healthy_snapshot_has_no_findings(self):
        snapshot = NodeSnapshot("demo", "/robot", 42, 0.1, process())
        self.assertEqual(self.engine.evaluate(snapshot), [])

    def test_node_namespace_is_normalized(self):
        snapshot = NodeSnapshot("demo", "robot", 42, 0.1, process())
        self.assertEqual(snapshot.fq_name, "/robot/demo")

    def test_missing_process_is_critical(self):
        snapshot = NodeSnapshot("demo", "/robot", 42, 8.0, None)
        finding = self.engine.evaluate(snapshot)[0]
        self.assertEqual(finding.rule_id, "process_missing")
        self.assertEqual(finding.severity, Severity.CRITICAL)

    def test_stale_heartbeat_and_hot_cpu_are_correlated(self):
        snapshot = NodeSnapshot("demo", "/robot", 42, 7.0, process(cpu_percent=96.0, state="R"))
        findings = self.engine.evaluate(snapshot)
        self.assertEqual([item.rule_id for item in findings], ["heartbeat_stale_with_cpu_pressure"])
        self.assertEqual(findings[0].evidence["cpu_percent"], 96.0)

    def test_memory_and_fd_limits_are_independent_evidence(self):
        snapshot = NodeSnapshot(
            "demo", "/robot", 42, 0.1,
            process(rss_bytes=700 * 1024 * 1024, fd_count=900),
        )
        rules = {item.rule_id for item in self.engine.evaluate(snapshot)}
        self.assertEqual(rules, {"rss_limit_exceeded", "fd_limit_exceeded"})


if __name__ == "__main__":
    unittest.main()
