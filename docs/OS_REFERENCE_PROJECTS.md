# OS-oriented reference projects

This list is deliberately biased toward operating systems, runtime software,
middleware and observability. It excludes mechanical design and robot control
algorithms.

| Priority | Project | OS/software focus | Recommended use here |
|---:|---|---|---|
| 1 | [ros/diagnostics](https://github.com/ros/diagnostics) | Robot diagnostic messages, aggregation and hardware/system health | Reproduce the diagnostic model; compare it with cross-layer Findings |
| 2 | [ros2/ros2_tracing](https://github.com/ros2/ros2_tracing) | LTTng tracepoints, callback/executor runtime analysis | Reproduce trace collection; correlate traces with procfs evidence |
| 3 | [ros2/rclpy](https://github.com/ros2/rclpy) | ROS 2 Python client and graph APIs | Implement the online graph/heartbeat adapter |
| 4 | [eclipse-cyclonedds/cyclonedds](https://github.com/eclipse-cyclonedds/cyclonedds) | DDS discovery, transport and shared-memory configuration | Run controlled middleware configuration experiments |
| 5 | [eProsima/Fast-DDS](https://github.com/eProsima/Fast-DDS) | DDS/RTPS, reliable and best-effort transport, discovery | Compare failure signals under the same workload |
| 6 | [eclipse-zenoh/zenoh-plugin-ros2dds](https://github.com/eclipse-zenoh/zenoh-plugin-ros2dds) | ROS 2/DDS bridging over constrained or distributed networks | Optional weak-network reproduction, not a v0.1 dependency |
| 7 | [eclipse-iceoryx/iceoryx2](https://github.com/eclipse-iceoryx/iceoryx2) | Zero-copy and lock-free IPC on Linux/AArch64 | Advanced IPC benchmark after the ROS adapter is stable |
| 8 | [micro-ROS/micro_ros_setup](https://github.com/micro-ROS/micro_ros_setup) | ROS 2 clients on RTOS/MCU targets | Read-only future direction; not selected without MCU hardware |

## Suggested order

1. Finish `diagnostics`-compatible output and the `rclpy` online adapter.
2. Add `ros2_tracing` evidence to stale-heartbeat findings.
3. Reproduce one Cyclone DDS/Fast DDS configuration comparison.
4. Consider Zenoh or iceoryx2 only after the first three stages have real data.

The goal is not to fork every repository. Each upstream project should be a
pinned dependency or an experiment target; original work remains in the
guardian adapters, correlation rules, recovery policy and evaluation scripts.

