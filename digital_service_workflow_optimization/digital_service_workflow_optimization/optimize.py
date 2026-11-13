"""Test workflow improvements and greedily allocate extra workers."""
import pandas as pd

from analyze import find_bottleneck, metrics, stage_report
from workflow_sim import DEFAULT_WORKERS, simulate


def compare_scenarios(requests, extra_workers=3):
    """Run baseline and improvement scenarios, return a comparison table."""
    base_log, base_sum = simulate(requests, DEFAULT_WORKERS, "fifo")
    bottleneck = find_bottleneck(stage_report(base_log, DEFAULT_WORKERS))

    boosted = dict(DEFAULT_WORKERS)
    boosted[bottleneck] += 1

    scenarios = {
        "Baseline (FIFO)": (DEFAULT_WORKERS, "fifo"),
        "Priority queue": (DEFAULT_WORKERS, "priority"),
        f"+1 worker @ {bottleneck}": (boosted, "fifo"),
        "Priority + 1 worker": (boosted, "priority"),
    }
    rows = []
    for name, (workers, discipline) in scenarios.items():
        _, summary = simulate(requests, workers, discipline)
        rows.append({"scenario": name, **metrics(summary)})
    return pd.DataFrame(rows), bottleneck


def greedy_allocation(requests, extra_workers=3, discipline="priority"):
    """Add workers one at a time to whichever stage currently has the longest wait."""
    workers = dict(DEFAULT_WORKERS)
    log, summary = simulate(requests, workers, discipline)
    steps = [{"step": 0, "added_to": "-", **metrics(summary), **{f"w_{k}": v for k, v in workers.items()}}]
    for step in range(1, extra_workers + 1):
        target = find_bottleneck(stage_report(log, workers))
        workers[target] += 1
        log, summary = simulate(requests, workers, discipline)
        steps.append({"step": step, "added_to": target, **metrics(summary),
                      **{f"w_{k}": v for k, v in workers.items()}})
    return pd.DataFrame(steps), workers
