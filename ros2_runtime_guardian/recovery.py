from __future__ import annotations

from dataclasses import dataclass

from .models import Finding, RecoveryDecision, Severity


@dataclass(frozen=True)
class RecoveryConfig:
    cooldown_s: float = 30.0
    max_attempts: int = 3
    execute: bool = False


class RecoveryController:
    """Turn diagnostics into bounded recovery decisions.

    This class deliberately does not execute operating-system commands. A
    deployment-specific supervisor adapter must consume accepted decisions.
    """

    def __init__(self, config: RecoveryConfig | None = None) -> None:
        self.config = config or RecoveryConfig()
        self._attempts: dict[str, int] = {}
        self._last_decision_at: dict[str, float] = {}

    def decide(self, finding: Finding, *, now: float) -> RecoveryDecision:
        target = f"{finding.node}:{finding.pid}"
        attempts = self._attempts.get(target, 0)
        previous = self._last_decision_at.get(target)

        if finding.severity < Severity.ERROR:
            return RecoveryDecision(target, "observe", False, "severity is below recovery threshold", attempts)
        if previous is not None and now - previous < self.config.cooldown_s:
            return RecoveryDecision(target, "observe", False, "recovery cooldown is active", attempts)
        if attempts >= self.config.max_attempts:
            return RecoveryDecision(target, "escalate", False, "recovery attempt budget is exhausted", attempts)

        attempts += 1
        self._attempts[target] = attempts
        self._last_decision_at[target] = now
        action = "request_supervised_restart"
        return RecoveryDecision(
            target=target,
            action=action,
            execute=self.config.execute,
            reason="dry-run decision" if not self.config.execute else "execution delegated to supervisor adapter",
            attempt=attempts,
        )

