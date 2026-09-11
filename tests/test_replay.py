import tempfile
import unittest
from pathlib import Path

from ros2_runtime_guardian.replay import replay


class ReplayTests(unittest.TestCase):
    def test_checked_in_trace_has_stable_findings(self):
        trace = Path("examples/traces/node_stall.jsonl")
        rules = [item.rule_id for item in replay(trace)]
        self.assertEqual(rules, ["heartbeat_stale_with_cpu_pressure", "process_missing"])

    def test_invalid_trace_reports_line_number(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.jsonl"
            path.write_text('{"node": "missing-fields"}\n')
            with self.assertRaisesRegex(ValueError, "line 1"):
                list(replay(path))


if __name__ == "__main__":
    unittest.main()

