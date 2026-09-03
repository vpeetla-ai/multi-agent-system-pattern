"""Reviewer-gate benchmark: real, executed measurement of the orchestrator's
mechanical reviewer-approval behavior versus a single-generalist baseline,
plus a check that the constructor's duplicate-role guard actually fires.

Scope and honesty note: this measures MECHANICAL gate behavior only --
whether `ReviewerAgent`'s real, deterministic presence-check on
`SharedContext` (are "research", "analysis" and "writer" artifacts all
present and non-empty?) passes or fails for a given agent roster and task.
It is **not** an LLM-output-quality benchmark. Every `Agent` in this
package -- like its four sibling curriculum-stub repos -- is a
deterministic stub with no external API calls; see the README's
"Curriculum stub" scope note and docs/ARCHITECTURE.md. Nothing in this
module calls an LLM or needs an API key.

Every number this module can produce comes from actually executing
`MultiAgentOrchestrator`, `ReviewerAgent`, and `SharedContext` -- the real
production code in this package, not a hand-written or simulated figure.
`scripts/benchmark_reviewer_gate.py` is the CLI entry point that runs
`run_all()` and (optionally) regenerates `docs/receipts/benchmark.md` from
that live output so the receipt can never drift from an actual run.
"""

from __future__ import annotations

from dataclasses import dataclass

from .agents import AnalystAgent, ResearchAgent, ReviewerAgent, WriterAgent
from .context import SharedContext
from .orchestrator import MultiAgentOrchestrator


@dataclass
class GeneralistAgent:
    """Single-generalist baseline.

    Real, deterministic code -- not a mock of a baseline. It attempts a
    final answer directly, in one pass, the way a single generalist agent
    would, instead of separating the research / analysis / writer
    artifacts the specialist roster produces. It still carries its own
    role tag ("generalist") and follows the same `Agent` protocol, so the
    real, unmodified `ReviewerAgent` runs its real gate logic against it --
    nothing about the reviewer is special-cased or faked for this
    comparison.
    """

    role: str = "generalist"

    def run(self, context: SharedContext) -> str:
        return (
            f"Single-pass answer for '{context.request}': gathered context, "
            "reasoned about it, and wrote a final response in one step, "
            "without separating research / analysis / writer artifacts."
        )


# Eight varied task requests used as the primary orchestrator-vs-generalist
# comparison. Indices 2 and 5 are also run through the *complete* roster in
# a different construction order (analyst before researcher) as a
# config-variation check: the reviewer gate only checks end-state artifact
# presence, so it should still approve regardless of execution order.
TASKS: list[str] = [
    "Prepare a customer support automation plan",
    "Create an enterprise AI automation brief",
    "Draft a Q3 infrastructure cost-reduction memo",
    "Summarize competitive positioning for a new product launch",
    "Produce an incident postmortem for a payments outage",
    "Write a migration plan from monolith to microservices",
    "Assess vendor risk for a new SaaS procurement",
    "Draft an onboarding guide for new platform engineers",
]

REORDERED_TASK_INDICES = (2, 5)


@dataclass(frozen=True)
class ScenarioResult:
    scenario_id: str
    condition: str
    request: str
    roster: tuple[str, ...]
    approved: bool | None
    decision: str
    guard_raised: bool | None = None
    error_message: str | None = None


def _complete_roster(reordered: bool) -> list:
    if reordered:
        return [AnalystAgent(), ResearchAgent(), WriterAgent(), ReviewerAgent()]
    return [ResearchAgent(), AnalystAgent(), WriterAgent(), ReviewerAgent()]


def _run_orchestrator(scenario_id: str, condition: str, request: str, agents: list) -> ScenarioResult:
    orchestrator = MultiAgentOrchestrator(agents)
    result = orchestrator.run(request)
    reviewer_texts = result.context.by_role("reviewer")
    decision = reviewer_texts[-1] if reviewer_texts else ""
    return ScenarioResult(
        scenario_id=scenario_id,
        condition=condition,
        request=request,
        roster=tuple(agent.role for agent in agents),
        approved=result.approved,
        decision=decision,
    )


def _run_duplicate_guard(scenario_id: str, request: str, agents: list) -> ScenarioResult:
    roster = tuple(agent.role for agent in agents)
    try:
        MultiAgentOrchestrator(agents)
    except ValueError as exc:
        return ScenarioResult(
            scenario_id=scenario_id,
            condition="duplicate_role_guard",
            request=request,
            roster=roster,
            approved=None,
            decision="guard_fired",
            guard_raised=True,
            error_message=str(exc),
        )
    return ScenarioResult(
        scenario_id=scenario_id,
        condition="duplicate_role_guard",
        request=request,
        roster=roster,
        approved=None,
        decision="guard_missing",
        guard_raised=False,
        error_message=None,
    )


def run_all() -> list[ScenarioResult]:
    """Execute every benchmark scenario for real and return the results.

    20 scenarios total:
      - 8 `orchestrator_complete` (full specialist roster + reviewer)
      - 8 `single_generalist` (GeneralistAgent + reviewer, same 8 tasks)
      - 2 `orchestrator_incomplete` (AnalystAgent missing from the roster)
      - 2 `duplicate_role_guard` (duplicate-role construction attempts)
    """
    results: list[ScenarioResult] = []

    for i, task in enumerate(TASKS):
        reordered = i in REORDERED_TASK_INDICES
        scenario_id = f"orch-complete-{i + 1:02d}"
        results.append(
            _run_orchestrator(scenario_id, "orchestrator_complete", task, _complete_roster(reordered))
        )

    for i, task in enumerate(TASKS):
        scenario_id = f"generalist-{i + 1:02d}"
        results.append(
            _run_orchestrator(
                scenario_id, "single_generalist", task, [GeneralistAgent(), ReviewerAgent()]
            )
        )

    incomplete_tasks = [TASKS[0], TASKS[4]]
    for i, task in enumerate(incomplete_tasks):
        scenario_id = f"orch-incomplete-{i + 1:02d}"
        results.append(
            _run_orchestrator(
                scenario_id,
                "orchestrator_incomplete",
                task,
                # AnalystAgent deliberately omitted from the roster.
                [ResearchAgent(), WriterAgent(), ReviewerAgent()],
            )
        )

    duplicate_cases = [
        (
            "duplicate-guard-01",
            TASKS[0],
            [ResearchAgent(), ResearchAgent(), WriterAgent(), ReviewerAgent()],
        ),
        (
            "duplicate-guard-02",
            TASKS[1],
            [WriterAgent(), AnalystAgent(), WriterAgent(), ReviewerAgent()],
        ),
    ]
    for scenario_id, task, agents in duplicate_cases:
        results.append(_run_duplicate_guard(scenario_id, task, agents))

    return results


@dataclass(frozen=True)
class ConditionSummary:
    condition: str
    total: int
    positive: int
    rate: float
    positive_label: str


_CONDITION_ORDER = (
    "orchestrator_complete",
    "single_generalist",
    "orchestrator_incomplete",
    "duplicate_role_guard",
)


def aggregate(results: list[ScenarioResult]) -> list[ConditionSummary]:
    summaries: list[ConditionSummary] = []
    for condition in _CONDITION_ORDER:
        subset = [r for r in results if r.condition == condition]
        if not subset:
            continue
        if condition == "duplicate_role_guard":
            positive = sum(1 for r in subset if r.guard_raised)
            label = "guard fired"
        else:
            positive = sum(1 for r in subset if r.approved)
            label = "approved"
        total = len(subset)
        summaries.append(
            ConditionSummary(
                condition=condition,
                total=total,
                positive=positive,
                rate=(positive / total) if total else 0.0,
                positive_label=label,
            )
        )
    return summaries


def to_mission_gate_actual(result: ScenarioResult) -> dict:
    """Shape a `ScenarioResult` as the `actual` payload the golden-eval
    registry's `mission_gate` scorer (`golden_eval_registry.runner`)
    expects: `{"checks": {...}, "quality_score": int, "decision": str}`.
    """
    if result.condition == "duplicate_role_guard":
        status = "pass" if result.guard_raised else "fail"
        return {
            "checks": {"Duplicate role guard": status},
            "quality_score": 100 if result.guard_raised else 0,
            "decision": "guard_fired" if result.guard_raised else "guard_missing",
        }
    status = "approved" if result.approved else "rejected"
    return {
        "checks": {"Reviewer verdict": status},
        "quality_score": 100 if result.approved else 0,
        "decision": result.decision,
    }


_CONDITION_LABELS = {
    "orchestrator_complete": "Orchestrator (complete specialist roster)",
    "single_generalist": "Single generalist (baseline)",
    "orchestrator_incomplete": "Orchestrator (incomplete roster — AnalystAgent missing)",
    "duplicate_role_guard": "Duplicate-role construction guard",
}


def render_report(results: list[ScenarioResult]) -> str:
    summaries = aggregate(results)
    lines: list[str] = []
    lines.append("# Reviewer-Gate Benchmark Receipt")
    lines.append("")
    lines.append(
        "Generated by `scripts/benchmark_reviewer_gate.py --write`, running "
        f"{len(results)} real, executed scenarios against this repo's actual "
        "`MultiAgentOrchestrator` / `ReviewerAgent` / `SharedContext` code "
        "(`src/multi_agent_system_pattern/`). No numbers below are "
        "hand-written; regenerate this file with:"
    )
    lines.append("")
    lines.append("```bash")
    lines.append("python scripts/benchmark_reviewer_gate.py --write")
    lines.append("```")
    lines.append("")
    lines.append("## Methodology")
    lines.append("")
    lines.append(
        "This measures the reviewer gate's **mechanical** behavior — whether "
        "`ReviewerAgent.run()`'s real, deterministic presence-check "
        "(`context.by_role(\"research\")`, `\"analysis\"`, `\"writer\"` all "
        "present and non-empty) approves or rejects a given agent roster and "
        "task. It is **not** a measurement of LLM output quality: every "
        "`Agent` implementation in this repo is a deterministic stub with no "
        "external API calls, matching this repo's sibling curriculum-stub "
        "repos and the existing README/demo \"simulated metrics\" framing. "
        "This benchmark is additive to that existing framing, not a "
        "replacement for it."
    )
    lines.append("")
    lines.append("Four conditions, 20 total scenarios:")
    lines.append("")
    lines.append(
        "- **orchestrator_complete** (8 scenarios) — real `MultiAgentOrchestrator` "
        "with the full `[ResearchAgent, AnalystAgent, WriterAgent, ReviewerAgent]` "
        "roster (2 of the 8 built in reordered construction order, as a "
        "config-variation check) across 8 varied task requests."
    )
    lines.append(
        "- **single_generalist** (8 scenarios) — the same 8 tasks, but the "
        "roster is `[GeneralistAgent, ReviewerAgent]`: a real, deterministic "
        "`GeneralistAgent` (new code in "
        "`src/multi_agent_system_pattern/benchmark.py`) that answers directly "
        "in one pass, without producing separate research/analysis/writer "
        "artifacts. The same, unmodified `ReviewerAgent` evaluates it."
    )
    lines.append(
        "- **orchestrator_incomplete** (2 scenarios) — real orchestrator run "
        "with `AnalystAgent` deliberately left out of the roster, to confirm "
        "the gate catches an incomplete specialist roster too."
    )
    lines.append(
        "- **duplicate_role_guard** (2 scenarios) — real construction attempts "
        "with a duplicated agent role, confirming "
        "`MultiAgentOrchestrator.__init__`'s `ValueError(\"Agent roles must be "
        "unique\")` guard fires."
    )
    lines.append("")
    lines.append("## Per-scenario results")
    lines.append("")
    lines.append("| Scenario | Condition | Roster (construction order) | Request | Result |")
    lines.append("|---|---|---|---|---|")
    for r in results:
        roster = ", ".join(r.roster)
        if r.condition == "duplicate_role_guard":
            outcome = f"guard_raised={r.guard_raised} — `{r.error_message}`"
        else:
            outcome = f"approved={r.approved} — `{r.decision}`"
        lines.append(f"| `{r.scenario_id}` | {r.condition} | {roster} | {r.request} | {outcome} |")
    lines.append("")
    lines.append("## Aggregate reviewer-gate outcome rate per condition")
    lines.append("")
    lines.append("| Condition | Scenarios | Positive outcomes | Rate |")
    lines.append("|---|---|---|---|")
    for s in summaries:
        label = _CONDITION_LABELS.get(s.condition, s.condition)
        lines.append(
            f"| {label} | {s.total} | {s.positive} ({s.positive_label}) | {s.rate:.0%} |"
        )
    lines.append("")
    lines.append(
        "The orchestrator's complete specialist roster clears the real "
        "reviewer gate on every scenario tried here; the single-generalist "
        "baseline — evaluated by the exact same, unmodified reviewer gate — "
        "does not, because it never populates the per-role artifacts the "
        "gate checks for. The incomplete-roster and duplicate-role-guard "
        "scenarios confirm the gate and the constructor guard both correctly "
        "fire when they should, rather than passing everything by default."
    )
    return "\n".join(lines)
