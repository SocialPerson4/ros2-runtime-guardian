from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .correlator import CrossLayerCorrelator
from .models import Finding, NodeSnapshot, ProcessSnapshot


def load_trace(path: str | Path) -> Iterable[NodeSnapshot]:
    with Path(path).open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            try:
                row = json.loads(line)
                process_data = row.get("process")
                process = ProcessSnapshot(**process_data) if process_data is not None else None
                yield NodeSnapshot(
                    name=row["node"],
                    namespace=row.get("namespace", "/"),
                    pid=int(row["pid"]),
                    heartbeat_age_s=float(row["heartbeat_age_s"]),
                    process=process,
                    metadata={"time_s": row.get("time_s")},
                )
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid trace record at line {line_number}: {exc}") from exc


def replay(path: str | Path, correlator: CrossLayerCorrelator | None = None) -> list[Finding]:
    engine = correlator or CrossLayerCorrelator()
    findings: list[Finding] = []
    for snapshot in load_trace(path):
        findings.extend(engine.evaluate(snapshot))
    return findings

