from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from .replay import replay


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ROS 2 and Linux runtime diagnostics experiments")
    commands = parser.add_subparsers(dest="command", required=True)
    replay_parser = commands.add_parser("replay", help="replay a deterministic JSONL fault trace")
    replay_parser.add_argument("trace", help="path to JSONL trace")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "replay":
        findings = replay(args.trace)
        for finding in findings:
            print(json.dumps(finding.as_dict(), ensure_ascii=False, sort_keys=True))
        print(json.dumps({"finding_count": len(findings)}, sort_keys=True))
        return 0
    return 2

