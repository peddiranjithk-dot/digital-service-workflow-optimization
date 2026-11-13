"""Bottleneck analysis and charts for the workflow simulation."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from workflow_sim import STAGES


def stage_report(log, workers):
    """Average wait, service time and utilization per stage."""
    horizon = log["end"].max()
    rows = []
    for stage in STAGES:
        s = log[log["stage"] == stage]
        busy = s["service"].sum()
        rows.append({
            "stage": stage,
            "workers": workers[stage],
            "avg_wait_min": s["wait"].mean(),
            "p90_wait_min": s["wait"].quantile(0.9),
            "avg_service_min": s["service"].mean(),
            "utilization": busy / (workers[stage] * horizon),
        })
    return pd.DataFrame(rows)


def find_bottleneck(report):
    """The stage where requests wait the longest on average."""
    return report.sort_values("avg_wait_min", ascending=False).iloc[0]["stage"]


def metrics(summary):
    """Headline KPIs for one scenario."""
    urgent = summary[summary["priority"] == "urgent"]
    return {
        "avg_cycle_min": summary["cycle_time"].mean(),
        "p90_cycle_min": summary["cycle_time"].quantile(0.9),
        "avg_wait_min": summary["total_wait"].mean(),
        "urgent_avg_cycle_min": urgent["cycle_time"].mean(),
        "sla_breach_pct": 100 * summary["sla_breached"].mean(),
    }


def plot_stage_report(report, path):
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].bar(report["stage"], report["avg_wait_min"], color="#d1495b")
    ax[0].set_title("Average wait per stage (min)")
    ax[0].tick_params(axis="x", rotation=30)
    ax[1].bar(report["stage"], report["utilization"] * 100, color="#00798c")
    ax[1].set_title("Worker utilization (%)")
    ax[1].axhline(85, ls="--", color="gray", lw=1)
    ax[1].tick_params(axis="x", rotation=30)
    plt.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_scenarios(df, path):
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].bar(df["scenario"], df["avg_cycle_min"], color="#00798c")
    ax[0].set_title("Average cycle time (min)")
    ax[0].tick_params(axis="x", rotation=25)
    ax[1].bar(df["scenario"], df["sla_breach_pct"], color="#d1495b")
    ax[1].set_title("SLA breaches (%)")
    ax[1].tick_params(axis="x", rotation=25)
    plt.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
