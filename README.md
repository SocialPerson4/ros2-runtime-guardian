# ROS 2 Runtime Guardian

面向 Linux 机器人主机的进程观测与故障关联规则原型。项目尝试把节点心跳状态与 Linux 进程指标组合为可解释诊断，并为后续接入 ROS 2 在线数据和受控恢复机制建立独立、可测试的 OS 侧核心。

- 开发方式：独立开发
- 开发时间：2026.07 至今
- 当前版本：v0.1 OS 侧原型

## 问题背景

ROS 2 的节点、Topic 和 QoS 状态通常从中间件侧观察，而 CPU、内存、线程、文件描述符和进程状态属于 Linux OS 层。单独观察一个层面时，难以区分进程退出、进程仍存活但资源压力较高、以及通信或回调暂时延迟等情况。

本项目将两类信息收敛到统一数据模型中，通过规则输出诊断级别、触发证据和建议动作。当前版本已经实现 Linux 采样与规则核心；心跳年龄由回放数据或调用方提供，ROS 2 在线适配仍在路线图中。

## 系统结构

```text
外部节点状态                 Linux 进程状态
heartbeat_age_s             /proc/<pid>/{stat,status,cmdline,fd}
        │                              │
        └──────────┬───────────────────┘
                   ▼
            NodeSnapshot 数据模型
                   │
                   ▼
           CrossLayerCorrelator
                   │
                   ├── Finding 证据与严重级别
                   └── RecoveryController
                         冷却时间 次数预算 dry-run
```

## 已实现功能

- **Linux 进程采样**：读取 `/proc/<pid>/stat`、`status`、`cmdline` 和 `fd`。
- **CPU 双采样计算**：根据进程 tick 增量与单调时钟区间计算 CPU 占用。
- **PID 复用保护**：保存 `start_time_ticks`，进程启动时间变化时重置 CPU 基线。
- **关联规则**：组合心跳年龄、进程存活、CPU、RSS 和文件描述符数量生成诊断。
- **可解释输出**：每条 Finding 保存规则编号、严重级别、原始证据和建议动作。
- **受限恢复决策**：使用冷却时间和次数预算生成 dry-run 决策，不直接执行系统命令。
- **确定性回放**：通过固定 JSONL 轨迹复现正常、CPU 压力和进程退出场景。
- **持续验证**：15 项单元测试与 GitHub Actions；Ubuntu CI 额外读取真实 `/proc` 数据。

## 工程设计

1. **多源证据关联**：把节点状态和 OS 指标放入同一诊断上下文，减少只看单一阈值时的信息缺失。
2. **机器可读 Finding**：统一保存诊断原因、证据和动作提示，便于记录、回放和后续适配。
3. **确定性回归输入**：固定轨迹与固定规则输出，使规则调整可以重复比较。
4. **受限决策机制**：恢复建议受冷却时间和次数预算限制，避免连续触发重启请求。

## 快速复现

要求 Python 3.10 及以上。v0.1 的 OS 侧核心不要求安装 ROS 2。

```bash
git clone https://github.com/SocialPerson4/ros2-runtime-guardian.git
cd ros2-runtime-guardian
python3 -m unittest discover -s tests -v
python3 -m ros2_runtime_guardian replay examples/traces/node_stall.jsonl
```

Linux 环境还可以运行真实 procfs 采样：

```bash
python3 -m ros2_runtime_guardian sample --pid self --interval 0.2
```

也可以使用统一命令：

```bash
make reproduce
```

示例回放会输出 `heartbeat_stale_with_cpu_pressure` 和 `process_missing` 两类诊断。

## 当前实现范围

| 模块 | 状态 | 验证方式 |
|---|---|---|
| `/proc` 进程采样 | 已实现 | 单元测试与 Ubuntu CI 冒烟测试 |
| JSONL 规则回放 | 已实现 | 固定轨迹回归测试 |
| 心跳与进程指标关联 | 原型完成 | 调用方提供心跳年龄 |
| dry-run 恢复决策 | 原型完成 | 冷却时间与预算测试 |
| `rclpy` 与 ROS Graph 接入 | 规划中 | 尚无在线采集数据 |
| 树莓派 ROS 2 实验 | 规划中 | 尚无性能数据 |

详细状态见 [项目状态](docs/PROJECT_STATUS.md)，复现层级与实验记录格式见 [复现说明](docs/REPRODUCIBILITY.md)。

## 项目结构

```text
ros2_runtime_guardian/
  models.py       # 进程 节点 Finding 与恢复决策数据模型
  procfs.py       # Linux procfs 采样器
  correlator.py   # 节点状态与 OS 指标关联规则
  recovery.py     # 有预算的 dry-run 恢复决策
  replay.py       # JSONL 故障轨迹回放
  cli.py          # 命令行入口
examples/traces/  # 可重复的输入轨迹
tests/            # 单元测试
docs/             # 项目状态 复现说明与路线图
```

## 后续计划

- 订阅节点心跳和 `/diagnostics`。
- 设计节点名称、PID、进程启动时间和可执行文件的显式注册协议。
- 输出 `diagnostic_msgs/DiagnosticArray`。
- 接入 QoS Deadline 和 Liveliness 事件。
- 增加 systemd 适配、cgroup v2 与 PSI 指标。
- 在树莓派上记录检测延迟、恢复耗时和监控开销。

完整阶段计划见 [ROADMAP](docs/ROADMAP.md)。

## 上游参考与许可证

项目依据 ROS 2 公开概念和接口设计数据边界，没有复制 ROS 2、diagnostics、ros2_tracing 或 Nav2 的源码。上游来源和差异见 [UPSTREAM.md](UPSTREAM.md)。

本项目采用 MIT License。
