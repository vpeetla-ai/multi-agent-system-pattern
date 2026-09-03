#!/usr/bin/env python3
"""CLI entry point for the reviewer-gate benchmark.

Runs the real `MultiAgentOrchestrator` / `ReviewerAgent` / `GeneralistAgent`
scenarios defined in `multi_agent_system_pattern.benchmark` and prints the
resulting receipt to stdout. Pass `--write` to also (re)write
`docs/receipts/benchmark.md` from that live run output, so the committed
receipt is always generated from an actual execution rather than
hand-edited.

Usage:
    python scripts/benchmark_reviewer_gate.py
    python scripts/benchmark_reviewer_gate.py --write
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

from multi_agent_system_pattern.benchmark import render_report, run_all  # noqa: E402

RECEIPT_PATH = _REPO_ROOT / "docs" / "receipts" / "benchmark.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="write the generated report to docs/receipts/benchmark.md",
    )
    args = parser.parse_args()

    results = run_all()
    report = render_report(results)
    print(report)

    if args.write:
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(report + "\n", encoding="utf-8")
        print(f"\nWrote {RECEIPT_PATH}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
