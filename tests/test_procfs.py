import os
import tempfile
import unittest
from pathlib import Path

from ros2_runtime_guardian.procfs import ProcfsSampler, ProcessGoneError


def stat_line(pid: int, name: str, utime: int, stime: int, starttime: int = 12345) -> str:
    fields = ["S"] + ["0"] * 49
    fields[11] = str(utime)
    fields[12] = str(stime)
    fields[19] = str(starttime)
    return f"{pid} ({name}) " + " ".join(fields)


class ProcfsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.pid_dir = self.root / "321"
        self.pid_dir.mkdir()
        (self.pid_dir / "fd").mkdir()
        (self.pid_dir / "fd" / "0").touch()
        (self.pid_dir / "cmdline").write_bytes(b"demo_node\x00--flag\x00")
        (self.pid_dir / "status").write_text(
            "Name:\tdemo node\nState:\tS (sleeping)\nVmRSS:\t2048 kB\nThreads:\t3\n"
        )
        (self.pid_dir / "stat").write_text(stat_line(321, "demo node", 100, 20))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sample_parses_status_and_cmdline(self):
        sampler = ProcfsSampler(self.root)
        snapshot = sampler.sample(321, now=10.0)
        self.assertEqual(snapshot.name, "demo node")
        self.assertEqual(snapshot.rss_bytes, 2048 * 1024)
        self.assertEqual(snapshot.threads, 3)
        self.assertEqual(snapshot.fd_count, 1)
        self.assertEqual(snapshot.cmdline, "demo_node --flag")
        self.assertEqual(snapshot.start_time_ticks, 12345)

    def test_second_sample_calculates_cpu_delta(self):
        sampler = ProcfsSampler(self.root)
        sampler.sample(321, now=10.0)
        ticks = sampler.clock_ticks
        (self.pid_dir / "stat").write_text(stat_line(321, "demo node", 100 + ticks, 20))
        snapshot = sampler.sample(321, now=12.0)
        self.assertAlmostEqual(snapshot.cpu_percent, 50.0)

    def test_pid_reuse_resets_cpu_baseline(self):
        sampler = ProcfsSampler(self.root)
        sampler.sample(321, now=10.0)
        ticks = sampler.clock_ticks
        (self.pid_dir / "stat").write_text(
            stat_line(321, "new process", 100 + ticks, 20, starttime=99999)
        )
        snapshot = sampler.sample(321, now=12.0)
        self.assertEqual(snapshot.cpu_percent, 0.0)
        self.assertEqual(snapshot.start_time_ticks, 99999)

    def test_missing_process_raises_typed_error(self):
        sampler = ProcfsSampler(self.root)
        with self.assertRaises(ProcessGoneError):
            sampler.sample(999, now=10.0)


if __name__ == "__main__":
    unittest.main()
