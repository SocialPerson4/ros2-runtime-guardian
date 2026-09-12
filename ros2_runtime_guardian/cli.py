from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections.abc import Sequence

from .procfs import ProcessGoneError, ProcfsSampler
from .replay import replay


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Linux process diagnostics core for future ROS 2 integration"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    replay_parser = commands.add_parser("replay", help="replay a deterministic JSONL fault trace")
    replay_parser.add_argument("trace", help="path to JSONL trace")
    sample_parser = commands.add_parser("sample", help="read one Linux process from procfs")
    sample_parser.add_argument("--pid", default="self", help="numeric PID or 'self' (default)")
    sample_parser.add_argument("--proc-root", default="/proc", help="procfs root; useful for tests")
    sample_parser.add_argument(
        "--interval",
        type=float,
        default=0.2,
        help="seconds between CPU baseline and measurement (default: 0.2)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "replay":
        findings = replay(args.trace)
        for finding in findings:
            print(json.dumps(finding.as_dict(), ensure_ascii=False, sort_keys=True))
        print(json.dumps({"finding_count": len(findings)}, sort_keys=True))
        return 0
    if args.command == "sample":
        try:
            pid = os.getpid() if args.pid == "self" else int(args.pid)
            if args.interval < 0:
                raise ValueError("interval must be non-negative")
            sampler = ProcfsSampler(args.proc_root)
            sampler.sample(pid)
            if args.interval:
                time.sleep(args.interval)
            snapshot = sampler.sample(pid)
        except (ValueError, ProcessGoneError, PermissionError) as exc:
            print(f"sample failed: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(snapshot.as_dict(), ensure_ascii=False, sort_keys=True))
        return 0
    return 2
