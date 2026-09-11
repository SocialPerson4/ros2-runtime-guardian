# ROS 2 Runtime Guardian

面向 Linux 机器人主机的 ROS 2 运行时观测与故障关联实验项目。

> 项目定位：复现 ROS 2 diagnostics / tracing 的基本观测思路，并在此基础上实现少量、可验证的跨层关联与安全恢复策略。它不是机器人机械结构或控制算法项目。

## 当前状态

`v0.1` 是一个可运行的最小基线：Linux `/proc` 进程采样、ROS/OS 状态关联、确定性故障回放和单元测试已经实现。ROS 2 在线节点与树莓派性能实验仍列在路线图中，因此 README 不报告尚未产生的真机指标。

## 为什么做这个项目

ROS 2 的节点、Topic 和 QoS 异常通常在中间件层被观察，而 CPU、内存、线程、文件描述符和进程状态属于 Linux OS 层。只看其中一层，很难区分“节点真的退出”“进程仍在但被资源压力拖慢”以及“通信暂时抖动”。本项目尝试把两层证据合并成可解释诊断。

## 已实现

- **Linux采样**：直接读取 `/proc/<pid>/stat`、`status`、`cmdline` 和 `fd`，不依赖常驻采集代理。
- **跨层规则**：联合节点心跳年龄与进程存活、CPU、RSS、线程数、文件描述符数量生成诊断。
- **解释性输出**：每条 Finding 保存触发规则、严重级别、原始证据和建议动作。
- **安全恢复**：提供冷却时间与恢复预算，只生成恢复决策；默认不执行 `kill`、重启或网络配置命令。
- **确定性回放**：使用 JSONL 轨迹复现节点正常、CPU饱和和进程退出场景。
- **持续验证**：标准库单元测试与 GitHub Actions，不需要机械硬件即可检查核心逻辑。

## 工程改进点

这些是相对基础监控流程的工程改进，不宣称学术首创：

1. **ROS—OS跨层关联**：把心跳超时与进程状态、CPU/RSS等证据合并，减少单指标告警。
2. **可解释Finding**：诊断结果携带机器可读证据，便于复盘“为什么报警”。
3. **确定性故障回放**：固定轨迹、固定输出，使规则修改前后可以回归比较。
4. **受限恢复策略**：冷却时间、次数预算和默认 dry-run，避免监控器造成重启风暴。

## 30秒复现

要求：Python 3.10+。核心复现不要求安装 ROS 2。

```bash
git clone https://github.com/SocialPerson4/ros2-runtime-guardian.git
cd ros2-runtime-guardian
python3 -m unittest discover -s tests -v
python3 -m ros2_runtime_guardian replay examples/traces/node_stall.jsonl
```

也可以运行：

```bash
make reproduce
```

预期现象：测试全部通过；回放输出 `heartbeat_stale_with_cpu_pressure` 与 `process_missing` 两类诊断。不要在论文或简历中把回放结果写成真机实验结果。

## ROS 2 在线模式边界

仓库保留了 ROS 2 接入层的接口位置，但 `v0.1` 的自动化测试只覆盖与 ROS 解耦的核心。后续计划在 Ubuntu 24.04 + ROS 2 Jazzy 上：

- 读取 ROS graph 与 `/diagnostics`；
- 通过显式注册建立 Node 与 PID 的映射；
- 接入 QoS Deadline / Liveliness 事件；
- 在树莓派上记录检测延迟、恢复耗时和监控开销。

## 项目结构

```text
ros2_runtime_guardian/
  models.py       # 跨层状态与诊断数据模型
  procfs.py       # Linux /proc 采样器
  correlator.py   # ROS/OS关联规则
  recovery.py     # 有预算的dry-run恢复决策
  replay.py       # JSONL故障轨迹回放
  cli.py          # 命令行入口
examples/traces/  # 可重复的输入轨迹
tests/            # 单元测试
docs/             # 复现说明、边界与路线图
```

## 开源来源与个人工作边界

本仓库没有复制 ROS 2、diagnostics、ros2_tracing 或 Nav2 的源码。它使用 ROS 2 的公开概念和接口作为复现依据，所有上游地址、复现范围和差异见 [UPSTREAM.md](UPSTREAM.md)。个人完成内容应仅指本仓库中的采样、关联、回放、策略和测试代码。

## License

MIT

