"""Real, fast tests over the reviewer-gate benchmark scenarios.

These run the actual scenarios in `multi_agent_system_pattern.benchmark`
(the same code `scripts/benchmark_reviewer_gate.py` and
`tests/test_golden_eval_gate.py` use) -- no mocking, no LLM calls, no
network. Everything here is deterministic and fast because every `Agent`
in this package is a deterministic stub by design.
"""

from __future__ import annotations

from multi_agent_system_pattern.benchmark import aggregate, run_all


def test_benchmark_produces_twenty_scenarios_across_four_conditions() -> None:
    results = run_all()
    assert len(results) == 20

    conditions = {r.condition for r in results}
    assert conditions == {
        "orchestrator_complete",
        "single_generalist",
        "orchestrator_incomplete",
        "duplicate_role_guard",
    }


def test_scenario_ids_are_unique() -> None:
    results = run_all()
    ids = [r.scenario_id for r in results]
    assert len(ids) == len(set(ids))


def test_complete_specialist_roster_beats_single_generalist_on_reviewer_approval() -> None:
    """The core claim this benchmark exists to check: the orchestrator's
    full specialist roster clears the real reviewer gate at a strictly
    higher rate than a single generalist agent evaluated by the exact
    same, unmodified reviewer."""
    summaries = {s.condition: s for s in aggregate(run_all())}

    complete = summaries["orchestrator_complete"]
    generalist = summaries["single_generalist"]

    assert complete.rate == 1.0
    assert generalist.rate == 0.0
    assert complete.rate > generalist.rate


def test_incomplete_roster_is_rejected_by_the_real_reviewer_gate() -> None:
    """A deliberately incomplete roster (AnalystAgent missing) must still be
    caught by the real gate -- this is the safety-net check, not theater."""
    summaries = {s.condition: s for s in aggregate(run_all())}
    incomplete = summaries["orchestrator_incomplete"]

    assert incomplete.total >= 2
    assert incomplete.rate == 0.0
    for result in run_all():
        if result.condition == "orchestrator_incomplete":
            assert result.approved is False
            assert result.decision.startswith("rejected")


def test_duplicate_role_construction_raises_valueerror() -> None:
    """MultiAgentOrchestrator.__init__ must refuse duplicate agent roles."""
    duplicate_results = [r for r in run_all() if r.condition == "duplicate_role_guard"]

    assert len(duplicate_results) >= 2
    for result in duplicate_results:
        assert result.guard_raised is True
        assert result.error_message == "Agent roles must be unique"


def test_reordered_complete_roster_still_approves() -> None:
    """Construction order shouldn't matter to the gate -- it checks
    end-state artifact presence, not sequencing."""
    complete_results = [r for r in run_all() if r.condition == "orchestrator_complete"]
    rosters_seen = {r.roster for r in complete_results}

    # Both the default order and the reordered (analysis-before-research)
    # order appear among the complete-roster scenarios, and all approve.
    assert ("research", "analysis", "writer", "reviewer") in rosters_seen
    assert ("analysis", "research", "writer", "reviewer") in rosters_seen
    assert all(r.approved for r in complete_results)
