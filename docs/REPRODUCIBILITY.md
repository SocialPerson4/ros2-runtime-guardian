# Reproducibility guide

## Reproduction levels

### Level A: core logic (current CI scope)

- Platform: Linux, macOS or Windows
- Runtime: Python 3.10+
- External dependencies: none
- Command: `make reproduce`
- Evidence: unit-test output and deterministic JSONL findings

### Level B: Linux procfs sampling

- Platform: Linux or Raspberry Pi OS
- Command: instantiate `ProcfsSampler()` with the default `/proc`
- Evidence to retain: `uname -a`, Python version, kernel version, PID command line and raw JSON output

### Level C: ROS 2 online experiment (roadmap)

- Planned baseline: Ubuntu 24.04, ROS 2 Jazzy
- Required evidence: ROS distribution, RMW implementation, workload, fault injection parameters, at least five repeated runs
- Required metrics: detection latency, recovery latency, CPU/RSS overhead and false-positive count

Level C is not complete in `v0.1`. Do not convert planned experiments into resume results.

## Determinism

The checked-in JSONL trace is immutable test input. Rules operate only on its explicit fields; no random numbers, clock reads or external services are used during replay. A change in output therefore indicates a code or configuration change.

## Recording new evidence

Store generated artifacts outside Git by default. Each experiment record should contain:

1. commit SHA;
2. operating-system and ROS versions;
3. configuration thresholds;
4. fault type and injection time;
5. raw findings;
6. summary statistics derived from raw data.

