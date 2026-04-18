"""
End-to-end driver for the Hybrid SMR-Solar-BESS simulation.

Runs the four required scenarios (plan Section 13) on a shared input
dataset, computes all metrics (Sections 8-11), executes validation
(Section 12), generates the 10 priority figures (Section 15), and
prints a summary table.

Usage:
    python main.py
"""

import os

import numpy as np

import config as C
import inputs as I
import metrics as M
import validation as V
import scenarios as SC
import figures as F


FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")


def _fmt_row(name: str, vals: list[str]) -> str:
    cols = [f"{name:<22s}"] + [f"{v:>14s}" for v in vals]
    return " ".join(cols)


def print_summary(scenarios: dict) -> None:
    """Compact Sec 15 Figure 15 style comparison table."""
    header_vals = [F.SCENARIO_LABELS[k] for k in F.SCENARIO_ORDER]
    print("\n=== Scenario comparison ===")
    print(_fmt_row("Metric", header_vals))
    print("-" * (22 + 15 * len(header_vals)))

    rows = [
        ("E_load (MWh)", "energy", "E_load"),
        ("E_served (MWh)", "energy", "E_served"),
        ("E_unmet (MWh)", "energy", "E_unmet"),
        ("E_curtail (MWh)", "energy", "E_curtail"),
        ("E_SMR (MWh)", "energy", "E_SMR"),
        ("E_PV_net (MWh)", "energy", "E_PV_net"),
        ("E_bat_dis (MWh)", "energy", "E_bat_dis"),
        ("f_served", "performance", "f_served"),
        ("LPSP", "performance", "LPSP"),
        ("f_RE", "performance", "f_RE"),
        ("f_SMR", "performance", "f_SMR"),
        ("f_curtail", "performance", "f_curtail"),
        ("N_cycles", "performance", "N_cycles"),
        ("P_unmet_max (MW)", "performance", "P_unmet_max"),
        ("R_mean_abs (MW/hr)", "ramp", "R_mean_abs"),
        ("R_max (MW/hr)", "ramp", "R_max"),
        ("R_std (MW/hr)", "ramp", "R_std"),
        ("eta_sys", "efficiency", "eta_sys"),
        ("eta_PV_sys", "efficiency", "eta_PV_sys"),
        ("eta_SMR_sys", "efficiency", "eta_SMR_sys"),
        ("eta_dispatch", "efficiency", "eta_dispatch"),
    ]

    summaries = {k: M.summarize(scenarios[k]) for k in F.SCENARIO_ORDER}

    for label, group, key in rows:
        vals = []
        for k in F.SCENARIO_ORDER:
            v = summaries[k][group][key]
            if isinstance(v, float) and not np.isnan(v):
                vals.append(f"{v:.3f}" if abs(v) < 100 else f"{v:.1f}")
            else:
                vals.append("n/a")
        print(_fmt_row(label, vals))


def print_validation(scenarios: dict) -> None:
    print("\n=== Validation (Section 12) ===")

    # 12.1 Energy-balance error across all scenarios
    print("\n12.1  Energy-balance error epsilon(t)")
    for k in F.SCENARIO_ORDER:
        eps = V.energy_balance_error(scenarios[k])
        print(
            f"  {F.SCENARIO_LABELS[k]:<20s}  max|eps| = {np.max(np.abs(eps)):.2e} MW"
            f"   mean|eps| = {V.avg_abs_error(eps):.2e} MW"
        )

    # 12.2 Boundary checks on the full-hybrid run
    print("\n12.2  Boundary-condition checks (full hybrid)")
    for chk in V.boundary_checks(scenarios["full_hybrid"]):
        status = "PASS" if chk["pass"] else "FAIL"
        print(f"  [{status}] {chk['condition']}")

    # 12.3 Trend checks
    print("\n12.3  Expected-trend checks (+20% perturbation, full hybrid)")
    for chk in V.trend_checks():
        status = "PASS" if chk["pass"] else "FAIL"
        print(
            f"  [{status}] {chk['check']:<55s}  "
            f"delta = {chk['delta']:+.3f} (expected sign {chk['expected_sign']:+d})"
        )

    # 12.4 Scenario ordering
    print("\n12.4  Scenario-ordering checks")
    for cond, ok in V.scenario_ordering(scenarios).items():
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {cond}")


def main() -> None:
    inputs = I.generate_inputs()
    print(f"Generated inputs: N = {C.N} hours, seed = {C.RNG_SEED}")

    scenarios = SC.run_all(inputs=inputs)
    for k in F.SCENARIO_ORDER:
        print(f"  ran scenario: {F.SCENARIO_LABELS[k]}")

    print_summary(scenarios)
    print_validation(scenarios)

    # Figure 6 battery-size sensitivity sweep
    sizes = [0, 50, 100, 150, 200, 250]
    print(f"\nRunning battery-size sweep: {sizes} MWh")
    sweep = SC.battery_size_sweep(sizes, inputs=inputs)
    for row in sweep:
        print(
            f"  E_bat_max = {row['E_bat_max']:6.1f} MWh   "
            f"f_served = {row['f_served']:.4f}   "
            f"LPSP = {row['LPSP']:.4f}   "
            f"N_cycles = {row['N_cycles']:.2f}"
        )

    print(f"\nGenerating figures into {FIG_DIR}")
    paths = F.generate_all(scenarios, sweep, FIG_DIR)
    for p in paths:
        print(f"  {os.path.basename(p)}")

    print("\nDone.")


if __name__ == "__main__":
    main()
