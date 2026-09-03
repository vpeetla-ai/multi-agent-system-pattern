"""Real merge gate: runs the shared `multi_agent_pattern.reviewer_gate_v1`
suite from vpeetla-ai/golden-eval-registry against this repo's real
reviewer-gate benchmark (`multi_agent_system_pattern.benchmark.run_all`),
using the registry's own `mission_gate` scorer
(`golden_eval_registry.runner.score_suite`).

Skips locally when the sibling registry repo isn't checked out; CI always
checks it out first (see .github/workflows/ci.yml) and points
`GOLDEN_EVAL_REGISTRY_PATH` at it.
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from multi_agent_system_pattern.benchmark import run_all, to_mission_gate_actual

try:
    from golden_eval_registry.runner import score_suite
    from golden_eval_registry.schema import parse_manifest
    from golden_eval_registry.validate import load_jsonl

    GOLDEN_EVAL_REGISTRY_AVAILABLE = True
except ImportError:
    GOLDEN_EVAL_REGISTRY_AVAILABLE = False

REGISTRY_PATH = Path(os.getenv("GOLDEN_EVAL_REGISTRY_PATH", "../golden-eval-registry")).resolve()
SUITE_DIR = REGISTRY_PATH / "suites" / "multi_agent_reviewer_gate_v1"


@unittest.skipUnless(
    GOLDEN_EVAL_REGISTRY_AVAILABLE and SUITE_DIR.exists(),
    "golden-eval-registry not available — set GOLDEN_EVAL_REGISTRY_PATH or run in CI",
)
class GoldenEvalGateTests(unittest.TestCase):
    def test_multi_agent_reviewer_gate_v1_suite_passes(self) -> None:
        manifest = parse_manifest(SUITE_DIR / "manifest.json")
        cases = load_jsonl(manifest.cases_path)

        actual_by_id = {result.scenario_id: to_mission_gate_actual(result) for result in run_all()}

        result = score_suite(manifest, cases, actual_by_id)
        failures = "\n".join(f"{failure.case_id}: {failure.detail}" for failure in result.failures)
        self.assertTrue(result.passed, f"golden eval regressions:\n{failures}")

    def test_aggregate_rates_meet_suite_thresholds(self) -> None:
        """The suite's `thresholds` aren't consumed by the generic
        `mission_gate` scorer (they're per-condition aggregates, not
        per-case checks), so this repo enforces them directly against the
        same real benchmark run."""
        manifest = parse_manifest(SUITE_DIR / "manifest.json")
        thresholds = manifest.thresholds

        from multi_agent_system_pattern.benchmark import aggregate

        summaries = {s.condition: s for s in aggregate(run_all())}

        self.assertGreaterEqual(
            summaries["orchestrator_complete"].rate,
            thresholds["orchestrator_complete_approval_rate_min"],
        )
        self.assertLessEqual(
            summaries["single_generalist"].rate,
            thresholds["single_generalist_approval_rate_max"],
        )
        self.assertLessEqual(
            summaries["orchestrator_incomplete"].rate,
            thresholds["orchestrator_incomplete_approval_rate_max"],
        )
        self.assertGreaterEqual(
            summaries["duplicate_role_guard"].rate,
            thresholds["duplicate_role_guard_fire_rate_min"],
        )


if __name__ == "__main__":
    unittest.main()
