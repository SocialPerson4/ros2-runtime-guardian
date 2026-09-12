from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import IntEnum
from typing import Any


class Severity(IntEnum):
    OK = 0
    WARN = 1
    ERROR = 2
    CRITICAL = 3


@dataclass(frozen=True)
class ProcessSnapshot:
    pid: int
    name: str
    state: str
    cpu_percent: float
    rss_bytes: int
    threads: int
    fd_count: int
    cmdline: str = ""
    start_time_ticks: int = 0

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NodeSnapshot:
    name: str
    namespace: str
    pid: int
    heartbeat_age_s: float
    process: ProcessSnapshot | None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def fq_name(self) -> str:
        namespace = self.namespace.strip("/")
        namespace = f"/{namespace}" if namespace else ""
        return f"{namespace}/{self.name}" if namespace else f"/{self.name}"


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: Severity
    node: str
    pid: int
    summary: str
    evidence: dict[str, Any]
    action_hint: str

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["severity"] = self.severity.name
        return result


@dataclass(frozen=True)
class RecoveryDecision:
    target: str
    action: str
    execute: bool
    reason: str
    attempt: int
