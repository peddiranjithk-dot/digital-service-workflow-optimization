"""Run the full Digital Service Workflow Optimization pipeline."""
import os

import pandas as pd

from analyze import find_bottleneck, plot_scenarios, plot_stage_report, stage_report
from optimize import compare_scenarios, greedy_allocation
from workflow_sim import DEFAULT_WORKERS, generate_requests, simulate

OUT = "results"


def main():
    os.makedirs(OUT, exist_ok=True)
    pd.set_option("display.width", 160)
    pd.set_option("display.float_format", "{:.1f}".format)

    requests = generate_requests(n=2000, arrival_rate=0.25, seed=42)
    requests.to_csv(f"{OUT}/requests.csv", index=False)

    # 1. Baseline analysis
    log, summary = simulate(requests, DEFAULT_WORKERS, "fifo")
    log.to_csv(f"{OUT}/event_log.csv", index=False)
    report = stage_report(log, DEFAULT_WORKERS)
    report.to_csv(f"{OUT}/stage_report.csv", index=False)
    plot_stage_report(report, f"{OUT}/stage_report.png")
    print("=== Baseline stage report ===")
    print(report.to_string(index=False))
    print(f"\nBottleneck stage: {find_bottleneck(report)}\n")

    # 2. Scenario comparison
    comparison, _ = compare_scenarios(requests)
    comparison.to_csv(f"{OUT}/scenario_comparison.csv", index=False)
    plot_scenarios(comparison, f"{OUT}/scenario_comparison.png")
    print("=== Scenario comparison ===")
    print(comparison.to_string(index=False))

    # 3. Greedy worker allocation
    steps, final = greedy_allocation(requests, extra_workers=3)
    steps.to_csv(f"{OUT}/greedy_allocation.csv", index=False)
    print("\n=== Greedy allocation of 3 extra workers (priority queue) ===")
    print(steps[["step", "added_to", "avg_cycle_min", "sla_breach_pct"]].to_string(index=False))
    print(f"\nRecommended staffing: {final}")
    print(f"\nOutputs saved in ./{OUT}/")


if __name__ == "__main__":
    main()
