import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ros2_runtime_guardian.cli import main


def stat_line(pid: int) -> str:
    fields = ["S"] + ["0"] * 49
    fields[11] = "10"
    fields[12] = "5"
    fields[19] = "12345"
    return f"{pid} (guardian) " + " ".join(fields)


class CliTests(unittest.TestCase):
    def test_sample_command_prints_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            process = root / "77"
            process.mkdir()
            (process / "fd").mkdir()
            (process / "cmdline").write_bytes(b"guardian\x00")
            (process / "status").write_text(
                "Name:\tguardian\nState:\tS (sleeping)\nVmRSS:\t1024 kB\nThreads:\t2\n"
            )
            (process / "stat").write_text(stat_line(77))
            output = io.StringIO()
            with redirect_stdout(output):
                result = main([
                    "sample", "--pid", "77", "--proc-root", directory,
                    "--interval", "0",
                ])
            self.assertEqual(result, 0)
            self.assertIn('"pid": 77', output.getvalue())
            self.assertIn('"rss_bytes": 1048576', output.getvalue())


if __name__ == "__main__":
    unittest.main()
