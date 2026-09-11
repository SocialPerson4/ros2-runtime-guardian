from __future__ import annotations

from dataclasses import dataclass

from .models import Finding, NodeSnapshot, Severity


@dataclass(frozen=True)
class CorrelationConfig:
    heartbeat_warn_s: float = 2.0
    heartbeat_error_s: float = 5.0
    cpu_pressure_percent: float = 85.0
    rss_limit_bytes: int = 512 * 1024 * 1024
    fd_limit: int = 512


class CrossLayerCorrelator:
    def __init__(self, config: CorrelationConfig | None = None) -> None:
        self.config = config or CorrelationConfig()

    def evaluate(self, node: NodeSnapshot) -> list[Finding]:
        process = node.process
        if process is None:
            return [
                Finding(
                    rule_id="process_missing",
                    severity=Severity.CRITICAL,
                    node=node.fq_name,
                    pid=node.pid,
                    summary="ROS node mapping exists but the Linux process is absent",
                    evidence={"heartbeat_age_s": node.heartbeat_age_s, "process_present": False},
                    action_hint="verify PID identity, then request a supervised restart",
                )
            ]

        findings: list[Finding] = []
        if node.heartbeat_age_s >= self.config.heartbeat_error_s:
            if process.cpu_percent >= self.config.cpu_pressure_percent:
                findings.append(
                    Finding(
                        rule_id="heartbeat_stale_with_cpu_pressure",
                        severity=Severity.ERROR,
                        node=node.fq_name,
                        pid=node.pid,
                        summary="Heartbeat is stale while the mapped process is CPU constrained",
                        evidence={
                            "heartbeat_age_s": node.heartbeat_age_s,
                            "cpu_percent": process.cpu_percent,
                            "process_state": process.state,
                        },
                        action_hint="capture a trace before requesting a supervised restart",
                    )
                )
            else:
                findings.append(
                    Finding(
                        rule_id="heartbeat_stale_process_alive",
                        severity=Severity.ERROR,
                        node=node.fq_name,
                        pid=node.pid,
                        summary="Heartbeat is stale although the mapped process is still alive",
                        evidence={
                            "heartbeat_age_s": node.heartbeat_age_s,
                            "cpu_percent": process.cpu_percent,
                            "process_state": process.state,
                        },
                        action_hint="inspect executor, middleware and callback latency",
                    )
                )
        elif node.heartbeat_age_s >= self.config.heartbeat_warn_s:
            findings.append(
                Finding(
                    rule_id="heartbeat_delayed",
                    severity=Severity.WARN,
                    node=node.fq_name,
                    pid=node.pid,
                    summary="Heartbeat delay exceeded the warning threshold",
                    evidence={"heartbeat_age_s": node.heartbeat_age_s},
                    action_hint="observe another interval before recovery",
                )
            )

        if process.rss_bytes >= self.config.rss_limit_bytes:
            findings.append(
                Finding(
                    rule_id="rss_limit_exceeded",
                    severity=Severity.WARN,
                    node=node.fq_name,
                    pid=node.pid,
                    summary="Process resident memory crossed the configured limit",
                    evidence={"rss_bytes": process.rss_bytes, "limit_bytes": self.config.rss_limit_bytes},
                    action_hint="inspect allocation growth and cgroup memory events",
                )
            )

        if process.fd_count >= self.config.fd_limit:
            findings.append(
                Finding(
                    rule_id="fd_limit_exceeded",
                    severity=Severity.WARN,
                    node=node.fq_name,
                    pid=node.pid,
                    summary="Open file descriptor count crossed the configured limit",
                    evidence={"fd_count": process.fd_count, "limit": self.config.fd_limit},
                    action_hint="inspect sockets, files and descriptor lifecycle",
                )
            )
        return findings

