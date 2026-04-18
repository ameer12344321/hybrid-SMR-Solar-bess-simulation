"""
Core time-step simulation engine for the Hybrid SMR-Solar-BESS system.

Implements Sections 2-5 and the hourly loop in Section 14.1 of
SMR_PV_BESS_Simulation_Plan.md. The `simulate()` function returns
raw time-series arrays; energy totals, performance metrics, and
validation live in separate modules added later.

Scenario selection is by two boolean flags, matching plan Section 13:

    Scenario 1 (Solar only)     : smr_on=False, battery_on=False
    Scenario 2 (Solar+Battery)  : smr_on=False, battery_on=True
    Scenario 3 (SMR+Solar)      : smr_on=True,  battery_on=False
    Scenario 4 (Full hybrid)    : smr_on=True,  battery_on=True
"""

from typing import Optional

import numpy as np

import config as C
import inputs as I


# Conversion factor: PV output from watts to megawatts.
# G is in W/m^2 and A_PV in m^2, so eta_PV * A_PV * G is in watts,
# while every other quantity in the power balance (load, SMR, battery)
# is in MW.
_W_TO_MW = 1.0e-6


def _pv_step(G_t: float, T_amb_t: float):
    """
    PV physics for a single hour (plan Sections 4.1-4.5).

    Returns
    -------
    (T_cell, eta_PV, P_PV_MW, P_PV_use_MW)
        T_cell in degC, eta_PV dimensionless, powers in MW.
        All four are zero when G_t <= 0 (night-time constraint, Sec 4.5),
        except T_cell which equals T_amb_t.
    """
    if G_t <= 0.0:
        return T_amb_t, 0.0, 0.0, 0.0

    T_cell = T_amb_t + C.K_ROSS * G_t
    eta_PV = C.ETA_REF * (1.0 - C.BETA * (T_cell - C.T_REF))
    P_PV_W = eta_PV * C.A_PV * G_t
    P_PV_use_W = C.ETA_INV * P_PV_W
    return T_cell, eta_PV, P_PV_W * _W_TO_MW, P_PV_use_W * _W_TO_MW


def _smr_step(a_SMR_t: int, smr_on: bool) -> float:
    """
    SMR electrical output after auxiliary load, in MW (plan Sec 5.1-5.3).

    P_SMR_NET = ETA_TH * P_TH - P_AUX is precomputed in config.py.
    When smr_on is False the reactor is removed from the power balance
    (Scenarios 1 and 2).
    """
    if not smr_on:
        return 0.0
    return a_SMR_t * C.P_SMR_NET


def _dispatch_step(P_net: float, SOC: float, battery_on: bool):
    """
    Reactive battery dispatch for a single hour (plan Sec 7.1-7.6).

    Returns
    -------
    (P_ch, P_dis, P_curtail, P_unmet, SOC_next)
        All powers in MW. The complementarity constraint
        P_ch * P_dis = 0 is satisfied because the surplus and deficit
        branches are mutually exclusive.
    """
    P_ch = 0.0
    P_dis = 0.0
    P_curtail = 0.0
    P_unmet = 0.0

    if P_net > 0.0:
        # Surplus: charge battery first, curtail the remainder.
        if battery_on:
            headroom = (C.SOC_MAX - SOC) * C.E_BAT_MAX / (C.ETA_CH * C.DT)
            P_ch = min(P_net, C.P_CH_MAX, max(headroom, 0.0))
        P_curtail = P_net - P_ch
    elif P_net < 0.0:
        # Deficit: discharge battery first, leave the remainder unmet.
        P_def = -P_net
        if battery_on:
            reserve = (SOC - C.SOC_MIN) * C.E_BAT_MAX * C.ETA_DIS / C.DT
            P_dis = min(P_def, C.P_DIS_MAX, max(reserve, 0.0))
        P_unmet = P_def - P_dis

    SOC_next = (
        SOC
        + (C.ETA_CH * P_ch * C.DT) / C.E_BAT_MAX
        - (P_dis * C.DT) / (C.ETA_DIS * C.E_BAT_MAX)
    )
    return P_ch, P_dis, P_curtail, P_unmet, SOC_next


def simulate(
    smr_on: bool = True,
    battery_on: bool = True,
    inputs: Optional[dict] = None,
    soc_0: float = C.SOC_0,
) -> dict:
    """
    Run the N-hour hybrid simulation.

    Parameters
    ----------
    smr_on : bool
        Include SMR generation. False zeros P_SMR_actual at every step.
    battery_on : bool
        Allow the battery to charge/discharge. False forces both to zero,
        so surplus becomes pure curtailment and deficit pure unmet demand.
    inputs : dict, optional
        Pre-generated input arrays (shape returned by inputs.generate_inputs).
        If None, a fresh deterministic set is generated using config.RNG_SEED.
    soc_0 : float
        Starting state of charge. Defaults to config.SOC_0.

    Returns
    -------
    dict of numpy.ndarray
        Length N arrays: G, T_amb, P_load, a_SMR (echoed from inputs);
        T_cell, eta_PV, P_PV, P_PV_use, P_SMR_actual, P_net,
        P_bat_ch, P_bat_dis, P_curtail, P_unmet.
        Length N+1 array: SOC (includes the final post-step value).
        Powers in MW, SOC dimensionless, T in degC, G in W/m^2.
    """
    if inputs is None:
        inputs = I.generate_inputs()

    N = C.N
    G = inputs["G"]
    T_amb = inputs["T_amb"]
    P_load = inputs["P_load"]
    a_SMR = inputs["a_SMR"]

    T_cell = np.zeros(N)
    eta_PV = np.zeros(N)
    P_PV = np.zeros(N)
    P_PV_use = np.zeros(N)
    P_SMR_actual = np.zeros(N)
    P_net = np.zeros(N)
    P_bat_ch = np.zeros(N)
    P_bat_dis = np.zeros(N)
    P_curtail = np.zeros(N)
    P_unmet = np.zeros(N)
    SOC = np.zeros(N + 1)
    SOC[0] = soc_0

    for t in range(N):
        # Step 1: PV block (Sec 4)
        Tc, eta, p_pv_mw, p_pv_use_mw = _pv_step(G[t], T_amb[t])
        T_cell[t] = Tc
        eta_PV[t] = eta
        P_PV[t] = p_pv_mw
        P_PV_use[t] = p_pv_use_mw

        # Step 2: SMR block (Sec 5)
        P_SMR_actual[t] = _smr_step(int(a_SMR[t]), smr_on)

        # Step 3: net power (Sec 7.2)
        P_net[t] = P_SMR_actual[t] + P_PV_use[t] - P_load[t]

        # Step 4-5: dispatch + SOC update (Sec 7.3-7.6)
        p_ch, p_dis, p_cur, p_unm, soc_next = _dispatch_step(
            P_net[t], SOC[t], battery_on
        )
        P_bat_ch[t] = p_ch
        P_bat_dis[t] = p_dis
        P_curtail[t] = p_cur
        P_unmet[t] = p_unm
        SOC[t + 1] = soc_next

    return {
        "G": G,
        "T_amb": T_amb,
        "P_load": P_load,
        "a_SMR": a_SMR,
        "T_cell": T_cell,
        "eta_PV": eta_PV,
        "P_PV": P_PV,
        "P_PV_use": P_PV_use,
        "P_SMR_actual": P_SMR_actual,
        "P_net": P_net,
        "P_bat_ch": P_bat_ch,
        "P_bat_dis": P_bat_dis,
        "P_curtail": P_curtail,
        "P_unmet": P_unmet,
        "SOC": SOC,
    }
