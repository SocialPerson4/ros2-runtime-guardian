# Roadmap

## v0.1 — reproducible OS core

- [x] procfs process sampler
- [x] cross-layer state model
- [x] explainable correlation rules
- [x] bounded dry-run recovery decisions
- [x] deterministic replay and tests

## v0.2 — ROS 2 adapter

- [ ] subscribe to heartbeat and `/diagnostics`
- [ ] explicit node-to-PID registration protocol
- [ ] export findings as `diagnostic_msgs/DiagnosticArray`
- [ ] QoS Deadline and Liveliness event adapter

## v0.3 — Linux supervision experiment

- [ ] systemd user-service adapter
- [ ] cgroup v2 memory and CPU pressure evidence
- [ ] safe fault-injection scripts with cleanup traps
- [ ] repeated measurements and CSV artifacts

## v0.4 — Raspberry Pi validation

- [ ] document board, OS, kernel and ROS image
- [ ] collect monitoring overhead
- [ ] compare single-layer and cross-layer alert precision
- [ ] publish only measured results

