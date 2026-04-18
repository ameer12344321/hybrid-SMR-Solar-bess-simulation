"""
Scenario drivers for the Hybrid SMR-Solar-BESS simulation (plan Section 13).

Four required scenarios plus one optional, all using the same simulation
engine with different component flags:

    1. Solar only      smr_on=False, battery_on=False
    2. Solar+Battery   smr_on=False, battery_on=True
    3. SMR+Solar       smr_on=True,  battery_on=False
    4. Full hybrid     smr_on=True,  battery_on=True
    5. SMR only        smr_on=True,  battery_on=False, PV forced to 0

Also exposes a battery-size sweep used by Figure 6.
"""

from typing import Dict, List, Tuple

import numpy as np

import config as C
import inputs as I
import simulation as S


SCENARIOS: List[Tuple[str, str, bool, bool]] = [
    ("solar_only", "Solar only", False, False),
    ("solar_battery", "Solar + Battery", False, True),
    ("smr_solar", "SMR + Solar", True, False),
    ("full_hybrid", "Full hybrid", True, True),
]


def run_all(inputs: Dict[str, np.ndarray] = None) -> Dict[str, dict]:
    """
    Run all four scenarios on a shared input dataset so they are directly
    comparable. Returns a dict keyed by scenario id with each simulate()
    result.
    """
    if inputs is None:
        inputs = I.generate_inputs()
    return {
        key: S.simulate(smr_on=smr, battery_on=batt, inputs=inputs)
        for key, _, smr, batt in SCENARIOS
    }


def run_smr_only(inputs: Dict[str, np.ndarray] = None) -> Dict[str, np.ndarray]:
    """Optional Scenario 5: SMR alone, with PV zeroed and battery disabled."""
    if inputs is None:
        inputs = I.generate_inputs()
    zeroed = dict(inputs)
    zeroed["G"] = np.zeros_like(inputs["G"])
    return S.simulate(smr_on=True, battery_on=False, inputs=zeroed)


def battery_size_sweep(
    sizes_mwh: List[float], inputs: Dict[str, np.ndarray] = None
) -> List[Dict[str, object]]:
    """
    Re-run the full-hybrid scenario across a list of battery capacities
    and report f_served for each. Used by Figure 6.

    A size of 0 MWh is emulated by disabling the battery, which produces
    the same behaviour (all surplus curtailed, all deficit unmet).
    """
    if inputs is None:
        inputs = I.generate_inputs()

    # Imported here to avoid a circular import at module load time.
    import metrics as M

    results = []
    original = C.E_BAT_MAX
    try:
        for size in sizes_mwh:
            if size <= 0:
                r = S.simulate(smr_on=True, battery_on=False, inputs=inputs)
            else:
                C.E_BAT_MAX = float(size)
                r = S.simulate(smr_on=True, battery_on=True, inputs=inputs)
            E = M.energy_totals(r)
            perf = M.performance_metrics(r, E)
            results.append(
                {
                    "E_bat_max": size,
                    "f_served": perf["f_served"],
                    "LPSP": perf["LPSP"],
                    "E_curtail": E["E_curtail"],
                    "N_cycles": perf["N_cycles"],
                }
            )
    finally:
        C.E_BAT_MAX = original
    return results
