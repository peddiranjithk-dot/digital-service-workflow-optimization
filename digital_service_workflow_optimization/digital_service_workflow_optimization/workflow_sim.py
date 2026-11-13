"""Simulation engine for a multi-stage digital service workflow.

Every service request moves through the same stages in order:
    intake -> verification -> processing -> approval -> delivery
Each stage has a number of workers (agents / bots). Requests wait in a queue
when all workers of a stage are busy. Time is measured in minutes.
"""
import heapq

import numpy as np
import pandas as pd

STAGES = ["intake", "verification", "processing", "approval", "delivery"]

# Average handling time per stage (minutes) and current staffing
MEAN_SERVICE = {"intake": 4, "verification": 10, "processing": 18,
                "approval": 7, "delivery": 3}
DEFAULT_WORKERS = {"intake": 2, "verification": 3, "processing": 5,
                   "approval": 2, "delivery": 1}

PRIORITIES = ["urgent", "high", "normal", "low"]
PRIORITY_RANK = {p: i for i, p in enumerate(PRIORITIES)}
# Target end-to-end completion time per priority (minutes)
SLA_MINUTES = {"urgent": 120, "high": 240, "normal": 480, "low": 960}

REQUEST_TYPES = {"account_setup": 1.0, "refund": 0.8,
                 "technical_issue": 1.3, "document_review": 1.1}


def generate_requests(n=2000, arrival_rate=0.25, seed=42):
    """Create n random service requests (arrival_rate = requests per minute)."""
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "request_id": np.arange(n),
        "arrival": np.cumsum(rng.exponential(1 / arrival_rate, n)),
        "priority": rng.choice(PRIORITIES, n, p=[0.10, 0.20, 0.50, 0.20]),
        "request_type": rng.choice(list(REQUEST_TYPES), n, p=[0.25, 0.25, 0.30, 0.20]),
    })
    complexity = df["request_type"].map(REQUEST_TYPES).to_numpy()
    for stage in STAGES:
        mean = MEAN_SERVICE[stage] * complexity
        df[f"service_{stage}"] = rng.gamma(shape=2.0, scale=mean / 2.0)
    return df


def _run_stage(ready, service, priority_rank, servers, discipline):
    """Simulate one stage with `servers` workers. Returns (start, end) arrays."""
    n = len(ready)
    order = np.argsort(ready, kind="stable")
    start = np.zeros(n)
    end = np.zeros(n)
    free = [0.0] * servers
    heapq.heapify(free)
    waiting = []
    i = 0
    done = 0
    while done < n:
        t = free[0] if waiting else max(free[0], ready[order[i]])
        while i < n and ready[order[i]] <= t:
            j = order[i]
            key = (priority_rank[j], ready[j], j) if discipline == "priority" \
                else (ready[j], j)
            heapq.heappush(waiting, (key, j))
            i += 1
        _, j = heapq.heappop(waiting)
        start[j] = t
        end[j] = t + service[j]
        heapq.heapreplace(free, end[j])
        done += 1
    return start, end


def simulate(requests, workers=None, discipline="fifo"):
    """Run the whole workflow.

    discipline: "fifo" (first come, first served) or "priority"
                (urgent requests jump the queue).
    Returns (event_log, request_summary).
    """
    workers = workers or DEFAULT_WORKERS
    rank = requests["priority"].map(PRIORITY_RANK).to_numpy()
    ready = requests["arrival"].to_numpy()
    events = []
    for stage in STAGES:
        service = requests[f"service_{stage}"].to_numpy()
        start, end = _run_stage(ready, service, rank, workers[stage], discipline)
        events.append(pd.DataFrame({
            "request_id": requests["request_id"], "stage": stage,
            "ready": ready, "start": start, "end": end,
            "wait": start - ready, "service": service}))
        ready = end
    log = pd.concat(events, ignore_index=True)

    summary = requests[["request_id", "arrival", "priority", "request_type"]].copy()
    summary["completion"] = ready
    summary["cycle_time"] = summary["completion"] - summary["arrival"]
    summary["total_wait"] = log.groupby("request_id")["wait"].sum().to_numpy()
    summary["sla"] = summary["priority"].map(SLA_MINUTES)
    summary["sla_breached"] = summary["cycle_time"] > summary["sla"]
    return log, summary
