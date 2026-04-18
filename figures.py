"""
Figure generators for the Hybrid SMR-Solar-BESS simulation.

Implements the 10 priority figures listed in plan Section 15 (Figure 8 is
the workflow diagram already embedded in the plan document, so no PNG is
produced for it here). Each function saves a PNG into the target
directory and returns the saved path.
"""

import os
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")  # headless backend: no display required
import matplotlib.pyplot as plt
import numpy as np

import config as C
import metrics as M
import validation as V


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

SCENARIO_LABELS = {
    "solar_only": "Solar only",
    "solar_battery": "Solar + Battery",
    "smr_solar": "SMR + Solar",
    "full_hybrid": "Full hybrid",
}
SCENARIO_ORDER = ["solar_only", "solar_battery", "smr_solar", "full_hybrid"]


def _save(fig: plt.Figure, out_dir: str, name: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _hours_axis(n: int) -> np.ndarray:
    return np.arange(n)


# ---------------------------------------------------------------------------
# Figure 1: Stacked generation vs load (full hybrid)
# ---------------------------------------------------------------------------

def fig1_stacked_generation(r: Dict[str, np.ndarray], out_dir: str) -> str:
    t = _hours_axis(C.N)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.stackplot(
        t,
        r["P_SMR_actual"],
        r["P_PV_use"],
        r["P_bat_dis"],
        labels=["SMR", "PV (post-inverter)", "Battery discharge"],
        colors=["#6a4c93", "#f4a261", "#2a9d8f"],
        alpha=0.85,
    )
    ax.plot(t, r["P_load"], color="black", lw=1.8, label="Load")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Power (MW)")
    ax.set_title("Figure 1 -- Generation stack vs load (full hybrid)")
    ax.legend(loc="upper left", ncol=2)
    ax.grid(alpha=0.25)
    ax.set_xlim(0, C.N)
    return _save(fig, out_dir, "fig01_stacked_generation.png")


# ---------------------------------------------------------------------------
# Figure 2: Battery SOC over time (full hybrid)
# ---------------------------------------------------------------------------

def fig2_soc(r: Dict[str, np.ndarray], out_dir: str) -> str:
    t = np.arange(C.N + 1)
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(t, r["SOC"], color="#264653", lw=1.6)
    ax.axhline(C.SOC_MIN, ls="--", color="grey", label=f"SOC_min = {C.SOC_MIN}")
    ax.axhline(C.SOC_MAX, ls="--", color="grey", label=f"SOC_max = {C.SOC_MAX}")
    ax.set_xlabel("Hour")
    ax.set_ylabel("State of charge")
    ax.set_ylim(0, 1)
    ax.set_title("Figure 2 -- Battery SOC (full hybrid)")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.25)
    ax.set_xlim(0, C.N)
    return _save(fig, out_dir, "fig02_soc.png")


# ---------------------------------------------------------------------------
# Figure 3: f_served across scenarios
# ---------------------------------------------------------------------------

def fig3_f_served(scenarios: Dict[str, dict], out_dir: str) -> str:
    labels = [SCENARIO_LABELS[k] for k in SCENARIO_ORDER]
    values = []
    for k in SCENARIO_ORDER:
        r = scenarios[k]
        E = M.energy_totals(r)
        values.append(M.performance_metrics(r, E)["f_served"])

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=["#e76f51", "#f4a261", "#2a9d8f", "#264653"])
    ax.set_ylabel("f_served")
    ax.set_ylim(0, 1.05)
    ax.set_title("Figure 3 -- Load served fraction by scenario")
    ax.grid(axis="y", alpha=0.25)
    for bar, v in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{v:.3f}",
            ha="center",
            fontsize=10,
        )
    return _save(fig, out_dir, "fig03_f_served.png")


# ---------------------------------------------------------------------------
# Figure 4: Average ramp rate bar chart
# ---------------------------------------------------------------------------

def fig4_ramp_rate(scenarios: Dict[str, dict], out_dir: str) -> str:
    labels = [SCENARIO_LABELS[k] for k in SCENARIO_ORDER]
    values = [M.ramp_stats(scenarios[k])["R_mean_abs"] for k in SCENARIO_ORDER]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=["#e76f51", "#f4a261", "#2a9d8f", "#264653"])
    ax.set_ylabel("Mean |ramp| (MW/hr)")
    ax.set_title("Figure 4 -- Average ramp rate by scenario")
    ax.grid(axis="y", alpha=0.25)
    for bar, v in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            f"{v:.2f}",
            ha="center",
            fontsize=10,
        )
    return _save(fig, out_dir, "fig04_ramp_rate.png")


# ---------------------------------------------------------------------------
# Figure 5: Energy-balance error epsilon(t)
# ---------------------------------------------------------------------------

def fig5_energy_balance_error(r: Dict[str, np.ndarray], out_dir: str) -> str:
    t = _hours_axis(C.N)
    eps = V.energy_balance_error(r)
    fig, ax = plt.subplots(figsize=(11, 3.5))
    ax.plot(t, eps, color="#d62828", lw=1.0)
    ax.axhline(0, color="black", lw=0.5)
    ax.set_xlabel("Hour")
    ax.set_ylabel(r"$\varepsilon(t)$ (MW)")
    ax.set_title(
        f"Figure 5 -- Energy-balance error (max |eps| = {np.max(np.abs(eps)):.2e} MW)"
    )
    ax.grid(alpha=0.25)
    ax.set_xlim(0, C.N)
    # Pad the y-axis so zero-line is visible even when eps is tiny.
    pad = max(1e-12, 5 * np.max(np.abs(eps)))
    ax.set_ylim(-pad, pad)
    return _save(fig, out_dir, "fig05_energy_balance_error.png")


# ---------------------------------------------------------------------------
# Figure 6: f_served vs battery size sensitivity
# ---------------------------------------------------------------------------

def fig6_battery_sensitivity(sweep: List[Dict[str, object]], out_dir: str) -> str:
    sizes = [s["E_bat_max"] for s in sweep]
    served = [s["f_served"] for s in sweep]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(sizes, served, marker="o", color="#264653", lw=2)
    ax.set_xlabel("E_bat,max (MWh)")
    ax.set_ylabel("f_served")
    ax.set_ylim(0, 1.05)
    ax.set_title("Figure 6 -- Reliability vs battery size (full hybrid)")
    ax.grid(alpha=0.25)
    for s, f in zip(sizes, served):
        ax.text(s, f + 0.015, f"{f:.3f}", ha="center", fontsize=9)
    return _save(fig, out_dir, "fig06_battery_sensitivity.png")


# ---------------------------------------------------------------------------
# Figure 7: Energy contribution pie
# ---------------------------------------------------------------------------

def fig7_energy_pie(r: Dict[str, np.ndarray], out_dir: str) -> str:
    E = M.energy_totals(r)
    sizes = [E["E_SMR"], E["E_PV_net"], E["E_bat_dis"]]
    labels = ["SMR", "PV (post-inverter)", "Battery discharge"]
    colors = ["#6a4c93", "#f4a261", "#2a9d8f"]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"edgecolor": "white"},
    )
    ax.set_title("Figure 7 -- Energy contribution (full hybrid)")
    return _save(fig, out_dir, "fig07_energy_pie.png")


# ---------------------------------------------------------------------------
# Figure 9: Unmet demand timelines (subplot per scenario)
# ---------------------------------------------------------------------------

def fig9_unmet(scenarios: Dict[str, dict], out_dir: str) -> str:
    t = _hours_axis(C.N)
    fig, axes = plt.subplots(
        len(SCENARIO_ORDER), 1, figsize=(11, 8), sharex=True, sharey=True
    )
    y_max = max(scenarios[k]["P_unmet"].max() for k in SCENARIO_ORDER)
    if y_max <= 0:
        y_max = 1.0
    for ax, key in zip(axes, SCENARIO_ORDER):
        ax.fill_between(
            t, scenarios[key]["P_unmet"], step="pre", color="#d62828", alpha=0.8
        )
        ax.set_ylabel("P_unmet (MW)")
        ax.set_title(SCENARIO_LABELS[key])
        ax.grid(alpha=0.25)
        ax.set_ylim(0, y_max * 1.1)
    axes[-1].set_xlabel("Hour")
    fig.suptitle("Figure 9 -- Unmet demand by scenario")
    fig.tight_layout()
    return _save(fig, out_dir, "fig09_unmet.png")


# ---------------------------------------------------------------------------
# Figure 10: Ramp-reduction index
# ---------------------------------------------------------------------------

def fig10_ramp_reduction(scenarios: Dict[str, dict], out_dir: str) -> str:
    base = M.ramp_stats(scenarios["solar_only"])["R_mean_abs"]
    pairs = [
        ("Solar -> Solar+Batt", scenarios["solar_battery"]),
        ("Solar -> SMR+Solar", scenarios["smr_solar"]),
        ("Solar -> Full hybrid", scenarios["full_hybrid"]),
    ]
    labels = [p[0] for p in pairs]
    values = [
        M.ramp_reduction(base, M.ramp_stats(p[1])["R_mean_abs"]) for p in pairs
    ]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(labels, values, color=["#f4a261", "#2a9d8f", "#264653"])
    ax.set_xlabel("Ramp reduction (%)")
    ax.set_title("Figure 10 -- Ramp reduction vs solar-only baseline")
    ax.grid(axis="x", alpha=0.25)
    for bar, v in zip(bars, values):
        ax.text(
            bar.get_width() + 1.0,
            bar.get_y() + bar.get_height() / 2,
            f"{v:.1f}%",
            va="center",
            fontsize=10,
        )
    ax.set_xlim(0, max(values) * 1.15 + 5)
    return _save(fig, out_dir, "fig10_ramp_reduction.png")


# ---------------------------------------------------------------------------
# Top-level driver
# ---------------------------------------------------------------------------

def generate_all(
    scenarios: Dict[str, dict],
    battery_sweep: List[Dict[str, object]],
    out_dir: str,
) -> List[str]:
    """Produce all 10 priority figures. Figure 8 is the workflow
    diagram in the plan document and is not regenerated here."""
    full = scenarios["full_hybrid"]
    paths = [
        fig1_stacked_generation(full, out_dir),
        fig2_soc(full, out_dir),
        fig3_f_served(scenarios, out_dir),
        fig4_ramp_rate(scenarios, out_dir),
        fig5_energy_balance_error(full, out_dir),
        fig6_battery_sensitivity(battery_sweep, out_dir),
        fig7_energy_pie(full, out_dir),
        fig9_unmet(scenarios, out_dir),
        fig10_ramp_reduction(scenarios, out_dir),
    ]
    return paths
