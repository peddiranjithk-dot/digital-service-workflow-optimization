# Digital Service Workflow Optimization

A simple base project that simulates a digital service desk workflow, finds the
bottleneck, and tests ways to speed it up.

Each request flows through: **intake -> verification -> processing -> approval -> delivery**.
Every stage has a limited number of workers, so requests queue up. The project:

1. **Simulates** 2,000 requests through the pipeline (discrete-event simulation, no extra libraries)
2. **Analyzes** wait time and worker utilization per stage to find the bottleneck
3. **Compares scenarios**: FIFO vs priority queue, and adding a worker at the bottleneck
4. **Optimizes staffing** by greedily adding extra workers where they help most

## Files

| File | Purpose |
|------|---------|
| `workflow_sim.py` | Request generator and workflow simulation engine |
| `analyze.py` | Stage report, bottleneck detection, KPIs, charts |
| `optimize.py` | Scenario comparison and greedy worker allocation |
| `main.py` | Runs everything and saves outputs to `results/` |
| `requirements.txt` | Dependencies |

## Run

```bash
pip install -r requirements.txt
python main.py
```

Outputs in `results/`: `requests.csv`, `event_log.csv`, `stage_report.csv/.png`,
`scenario_comparison.csv/.png`, `greedy_allocation.csv`.

## Customize

Edit the constants at the top of `workflow_sim.py`:
`MEAN_SERVICE` (handling times), `DEFAULT_WORKERS` (staffing), `SLA_MINUTES`
(targets per priority). Change `arrival_rate` in `main.py` to test heavier or
lighter demand. To use real data, replace `generate_requests()` with a loader
that returns the same columns.

## KPIs

- **avg / p90 cycle time**: minutes from arrival to completion
- **avg wait**: total time spent queuing
- **SLA breach %**: share of requests that finished later than the target for their priority
