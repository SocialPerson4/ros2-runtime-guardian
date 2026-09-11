FROM ros:jazzy-ros-base

WORKDIR /workspace
COPY . /workspace
RUN python3 -m pip install --break-system-packages --no-cache-dir -e .

CMD ["python3", "-m", "ros2_runtime_guardian", "replay", "examples/traces/node_stall.jsonl"]

