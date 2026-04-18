"""
Post-processing metrics for the Hybrid SMR-Solar-BESS simulation.

Turns the raw time-series arrays returned by simulation.simulate()
into energy totals, reliability/efficiency fractions, and ramp-rate
statistics, per plan Sections 8, 9, 10, 11.

All energies in MWh, all powers in MW, all ramps in MW/hr, all
fractions dimensionless.
"""

from typing import Dict

import numpy as np

import config as C


def energy_totals(r: Dict[str, np.ndarray]) -> Dict[str, float]:
    """Section 8: cumulative energy quantities.

    r is the dict returned by simulation.simulate().
    """
    dt = C.DT
    E_SMR = float(np.sum(r["P_SMR_actual"]) * dt)
    E_PV_gross = float(np.sum(r["P_PV"]) * dt)
    E_PV_net = float(np.sum(r["P_PV_use"]) * dt)
    E_bat_dis = float(np.sum(r["P_bat_dis"]) * dt)
    E_bat_ch = float(np.sum(r["P_bat_ch"]) * dt)
    E_load = float(np.sum(r["P_load"]) * dt)
    E_unmet = float(np.sum(r["P_unmet"]) * dt)
    E_served = E_load - E_unmet
    E_curtail = float(np.sum(r["P_curtail"]) * dt)
    E_inv_loss = E_PV_gross - E_PV_net
    E_bat_net = E_bat_dis - E_bat_ch

    # System-efficiency inputs (Sec 11.1)
    E_solar_in = float(np.sum(C.A_PV * r["G"]) * dt) * 1e-6  # W -> MW
    E_SMR_in = float(np.sum((r["a_SMR"] * C.P_TH)) * dt)

    return {
        "E_SMR": E_SMR,
        "E_PV_gross": E_PV_gross,
        "E_PV_net": E_PV_net,
        "E_bat_dis": E_bat_dis,
        "E_bat_ch": E_bat_ch,
        "E_load": E_load,
        "E_served": E_served,
        "E_unmet": E_unmet,
        "E_curtail": E_curtail,
        "E_inv_loss": E_inv_loss,
        "E_bat_net": E_bat_net,
        "E_solar_in": E_solar_in,
        "E_SMR_in": E_SMR_in,
    }


def ramp_stats(r: Dict[str, np.ndarray]) -> Dict[str, float]:
    """Section 9: ramp-rate statistics of the delivered-power signal."""
    P_del = (
        r["P_SMR_actual"]
        + r["P_PV_use"]
        + r["P_bat_dis"]
        - r["P_bat_ch"]
    )
    R = np.diff(P_del) / C.DT  # length N-1
    abs_R = np.abs(R)
    R_max = float(abs_R.max()) if R.size else 0.0
    R_mean_abs = float(abs_R.mean()) if R.size else 0.0
    R_std = float(R.std(ddof=1)) if R.size > 1 else 0.0
    return {
        "P_del": P_del,
        "R": R,
        "R_max": R_max,
        "R_mean_abs": R_mean_abs,
        "R_std": R_std,
    }


def performance_metrics(
    r: Dict[str, np.ndarray], energies: Dict[str, float]
) -> Dict[str, float]:
    """Section 10: reliability, generation mix, curtailment, cycles."""
    E_load = energies["E_load"]
    E_served = energies["E_served"]
    E_unmet = energies["E_unmet"]
    E_PV_net = energies["E_PV_net"]
    E_SMR = energies["E_SMR"]
    E_curtail = energies["E_curtail"]
    E_bat_dis = energies["E_bat_dis"]

    f_served = E_served / E_load if E_load > 0 else float("nan")
    LPSP = E_unmet / E_load if E_load > 0 else float("nan")
    f_RE = E_PV_net / E_served if E_served > 0 else float("nan")
    f_SMR = E_SMR / E_served if E_served > 0 else float("nan")
    gen_total = E_PV_net + E_SMR
    f_RE_gen = E_PV_net / gen_total if gen_total > 0 else float("nan")
    f_SMR_gen = E_SMR / gen_total if gen_total > 0 else float("nan")
    f_curtail = E_curtail / gen_total if gen_total > 0 else float("nan")
    N_cycles = E_bat_dis / C.E_BAT_MAX
    P_unmet_max = float(r["P_unmet"].max())

    return {
        "f_served": f_served,
        "LPSP": LPSP,
        "f_RE": f_RE,
        "f_SMR": f_SMR,
        "f_RE_gen": f_RE_gen,
        "f_SMR_gen": f_SMR_gen,
        "f_curtail": f_curtail,
        "N_cycles": N_cycles,
        "P_unmet_max": P_unmet_max,
    }


def efficiencies(energies: Dict[str, float]) -> Dict[str, float]:
    """Section 11: overall and subsystem efficiencies."""
    E_solar_in = energies["E_solar_in"]
    E_SMR_in = energies["E_SMR_in"]
    E_PV_net = energies["E_PV_net"]
    E_SMR = energies["E_SMR"]
    E_served = energies["E_served"]
    gen_total = E_PV_net + E_SMR
    total_in = E_solar_in + E_SMR_in

    eta_sys = E_served / total_in if total_in > 0 else float("nan")
    eta_PV_sys = E_PV_net / E_solar_in if E_solar_in > 0 else float("nan")
    eta_SMR_sys = E_SMR / E_SMR_in if E_SMR_in > 0 else float("nan")
    eta_dispatch = E_served / gen_total if gen_total > 0 else float("nan")

    return {
        "eta_sys": eta_sys,
        "eta_PV_sys": eta_PV_sys,
        "eta_SMR_sys": eta_SMR_sys,
        "eta_dispatch": eta_dispatch,
    }


def ramp_reduction(R_mean_abs_base: float, R_mean_abs_hybrid: float) -> float:
    """Section 9.6: percentage reduction of mean absolute ramp."""
    if R_mean_abs_base <= 0:
        return float("nan")
    return (R_mean_abs_base - R_mean_abs_hybrid) / R_mean_abs_base * 100.0


def summarize(r: Dict[str, np.ndarray]) -> Dict[str, Dict[str, float]]:
    """Convenience wrapper: compute all four metric groups for one run."""
    E = energy_totals(r)
    R = ramp_stats(r)
    P = performance_metrics(r, E)
    H = efficiencies(E)
    return {"energy": E, "ramp": R, "performance": P, "efficiency": H}
