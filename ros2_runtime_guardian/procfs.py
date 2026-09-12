from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path

from .models import ProcessSnapshot


class ProcessGoneError(RuntimeError):
    """Raised when a process disappears during sampling."""


@dataclass
class _CpuPoint:
    ticks: int
    observed_at: float
    start_time_ticks: int


class ProcfsSampler:
    """Collect process metrics directly from Linux procfs.

    CPU usage needs two samples. The first observation reports 0.0 percent;
    later observations use process tick delta divided by wall-clock time.
    """

    def __init__(self, proc_root: str | Path = "/proc") -> None:
        self.proc_root = Path(proc_root)
        self.clock_ticks = int(os.sysconf("SC_CLK_TCK"))
        self._cpu_points: dict[int, _CpuPoint] = {}

    def sample(self, pid: int, *, now: float | None = None) -> ProcessSnapshot:
        observed_at = time.monotonic() if now is None else now
        process_dir = self.proc_root / str(pid)
        try:
            status = self._parse_status((process_dir / "status").read_text())
            stat_text = (process_dir / "stat").read_text().strip()
            cmdline_raw = (process_dir / "cmdline").read_bytes()
        except (FileNotFoundError, ProcessLookupError) as exc:
            self._cpu_points.pop(pid, None)
            raise ProcessGoneError(f"process {pid} is not present") from exc

        stat = self._parse_stat(stat_text)
        ticks = stat["utime"] + stat["stime"]
        previous = self._cpu_points.get(pid)
        cpu_percent = 0.0
        if (previous is not None
                and previous.start_time_ticks == stat["starttime"]
                and observed_at > previous.observed_at):
            cpu_seconds = (ticks - previous.ticks) / self.clock_ticks
            cpu_percent = max(0.0, cpu_seconds / (observed_at - previous.observed_at) * 100.0)
        self._cpu_points[pid] = _CpuPoint(
            ticks=ticks,
            observed_at=observed_at,
            start_time_ticks=int(stat["starttime"]),
        )

        try:
            fd_count = sum(1 for _ in (process_dir / "fd").iterdir())
        except (FileNotFoundError, PermissionError):
            fd_count = -1

        return ProcessSnapshot(
            pid=pid,
            name=status.get("Name", stat["name"]),
            state=status.get("State", stat["state"]).split()[0],
            cpu_percent=round(cpu_percent, 2),
            rss_bytes=self._parse_kib(status.get("VmRSS", "0 kB")) * 1024,
            threads=int(status.get("Threads", "0")),
            fd_count=fd_count,
            cmdline=cmdline_raw.replace(b"\x00", b" ").decode(errors="replace").strip(),
            start_time_ticks=int(stat["starttime"]),
        )

    @staticmethod
    def _parse_status(text: str) -> dict[str, str]:
        values: dict[str, str] = {}
        for line in text.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                values[key] = value.strip()
        return values

    @staticmethod
    def _parse_stat(text: str) -> dict[str, int | str]:
        left = text.find("(")
        right = text.rfind(")")
        if left < 0 or right < left:
            raise ValueError("invalid /proc/<pid>/stat format")
        pid = int(text[:left].strip())
        name = text[left + 1 : right]
        rest = text[right + 1 :].strip().split()
        if len(rest) < 20:
            raise ValueError("truncated /proc/<pid>/stat")
        return {
            "pid": pid,
            "name": name,
            "state": rest[0],
            "utime": int(rest[11]),
            "stime": int(rest[12]),
            "starttime": int(rest[19]),
        }

    @staticmethod
    def _parse_kib(value: str) -> int:
        token = value.split()[0] if value else "0"
        return int(token)
