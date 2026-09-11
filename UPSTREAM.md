# Upstream references and authorship boundary

本项目采用“接口/思路复现 + 独立实现”的方式，不把上游项目代码或成果计入个人工作量。

| 上游项目 | 参考内容 | 本仓库的处理 |
|---|---|---|
| [ros/diagnostics](https://github.com/ros/diagnostics) | `/diagnostics`、分级状态、聚合式诊断思路 | 独立定义轻量 Finding，并增加 ROS/OS 跨层证据 |
| [ros2/ros2_tracing](https://github.com/ros2/ros2_tracing) | 运行时事件追踪与离线分析方法 | 当前仅保留路线图，尚未声称完成 LTTng 实测 |
| [ros2/rclpy](https://github.com/ros2/rclpy) | ROS 2 Python 接口和 Graph API | 后续在线适配层的依赖，不复制其实现 |
| [ros-navigation/navigation2](https://github.com/ros-navigation/navigation2) | Lifecycle 节点与恢复行为的应用场景 | 仅作为后续实验负载，不实现导航或机械控制 |

## 可归属于本仓库的实现

- Linux `/proc` 采样与单位转换；
- 心跳和进程资源的跨层关联规则；
- Finding 证据模型；
- 冷却时间、恢复预算和 dry-run 决策；
- JSONL 故障轨迹回放；
- 单元测试、CI 与复现文档。

## 不应声称的内容

- 不声称独立实现 ROS 2、DDS、Nav2 或 LTTng；
- 不声称设计机器人机械结构或控制算法；
- 未完成真机实验前，不填写检测延迟、吞吐量、CPU开销等数字；
- 示例轨迹只能证明软件逻辑可复现，不能替代树莓派/机器人实测。

