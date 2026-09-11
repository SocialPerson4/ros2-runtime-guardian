.PHONY: test demo check reproduce

test:
	python3 -m unittest discover -s tests -v

demo:
	python3 -m ros2_runtime_guardian replay examples/traces/node_stall.jsonl

check:
	python3 -m compileall -q ros2_runtime_guardian tests

reproduce: check test demo

