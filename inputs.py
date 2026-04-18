"""
Time-varying synthetic inputs for the Hybrid SMR-Solar-BESS simulation.

All profiles are generated from physically motivated equations calibrated to
Malaysian conditions. Hourly time step, indexed by t = 0, 1, ..., N-1.

Current scope:
  - solar_irradiance(t): physics-based G(t) using solar geometry + Beer-Lambert.
  - Stubs for ambient_temperature, load_demand, availability_factor (TODO).
"""

import math
from typing import Optional

import numpy as np

import config as C


def solar_irradiance(t: int, rng: Optional[np.random.Generator] = None) -> float:
    """
    Global horizontal irradiance G(t) at hour t.

    Physics steps (Duffie & Beckman, "Solar Engineering of Thermal Processes"):
      1. Day of year n and hour of day h derived from t.
      2. Declination delta     : Cooper's equation.
      3. Hour angle omega      : 15 deg per hour from solar noon.
      4. Solar elevation alpha : sin(alpha) = sin(phi)sin(delta) + cos(phi)cos(delta)cos(omega).
      5. Clear-sky irradiance  : G_clear = G_sc * sin(alpha) * tau^AM,  AM = 1/sin(alpha).
      6. Cloud noise           : G = max(G_clear * (1 + U(-0.1, +0.1)), 0).

    Parameters
    ----------
    t : int
        Hour index from simulation start (0 <= t < N).
    rng : numpy.random.Generator, optional
        RNG for reproducible noise. If None, no noise is applied.

    Returns
    -------
    float
        Global horizontal irradiance in W/m^2. Zero when sun is below horizon.
    """
    # Step 1: day of year and hour of day
    n = C.DOY_START + t // 24
    h = t % 24

    # Step 2: declination (Cooper)
    delta = math.radians(23.45) * math.sin(2.0 * math.pi * (284 + n) / 365.0)

    # Step 3: hour angle (radians per hour away from solar noon)
    omega = math.radians(15.0) * (h - 12.0)

    # Step 4: solar elevation
    phi = math.radians(C.PHI_LAT)
    sin_alpha = (math.sin(phi) * math.sin(delta)
                 + math.cos(phi) * math.cos(delta) * math.cos(omega))

    # Sun below horizon -> no direct beam
    if sin_alpha <= 0.0:
        return 0.0

    # Step 5: Beer-Lambert with air mass
    air_mass = 1.0 / sin_alpha
    g_clear = C.G_SC * sin_alpha * (C.TAU_ATM ** air_mass)

    # Step 6: multiplicative cloud noise
    if rng is not None:
        noise = rng.uniform(-C.G_NOISE, +C.G_NOISE)
        g = g_clear * (1.0 + noise)
    else:
        g = g_clear

    return max(g, 0.0)


def ambient_temperature(t: int) -> float:
    """
    Ambient air temperature T_amb(t) at hour t.

    Diurnal cosine profile centred on T_MEAN with half-amplitude T_SWING and
    peak at hour T_PEAK_HOUR:

        T_amb(t) = T_mean + T_swing * cos(2*pi * (h - h_peak) / 24)

    Note: the plan document states the formula with sin((h-14)/24), but that
    expression actually peaks at h=20, contradicting its own "peak at 2 PM"
    annotation. The cos form above matches the stated physics (max at 14,
    min 12 h later at 02:00) and the stated range ~24 degC to ~32 degC.

    Parameters
    ----------
    t : int
        Hour index from simulation start.

    Returns
    -------
    float
        Ambient temperature in degC.
    """
    h = t % 24
    return C.T_MEAN + C.T_SWING * math.cos(
        2.0 * math.pi * (h - C.T_PEAK_HOUR) / 24.0
    )


def is_weekend(t: int) -> bool:
    """Return True if hour t falls on a simulation-weekend day.

    Convention: simulation day 0 is Monday, so day indices 5 and 6 are the
    weekend by default (see config.WEEKEND_DAYS).
    """
    day_index = (t // 24) % 7
    return day_index in C.WEEKEND_DAYS


def load_demand(t: int, weekend: Optional[bool] = None) -> float:
    """
    Electrical load demand P_load(t) at hour t.

    Tropical double-peak profile: baseline plus two narrow Gaussians at the
    morning and evening peak hours (plan Section 2.2):

        P_load(t) = P_base + P_morning * exp(-(h - h_morning)^2 / LOAD_DENOM)
                           + P_evening * exp(-(h - h_evening)^2 / LOAD_DENOM)

    On weekend days both peak amplitudes are reduced by WEEKEND_REDUCTION.

    Parameters
    ----------
    t : int
        Hour index from simulation start.
    weekend : bool, optional
        Override weekend flag. If None, determined from t via is_weekend().

    Returns
    -------
    float
        Load demand in MW.
    """
    h = t % 24
    is_we = is_weekend(t) if weekend is None else weekend

    scale = (1.0 - C.WEEKEND_REDUCTION) if is_we else 1.0
    p_morning = C.P_MORNING * scale
    p_evening = C.P_EVENING * scale

    return (
        C.P_BASE
        + p_morning * math.exp(-((h - C.P_MORNING_HOUR) ** 2) / C.LOAD_DENOM)
        + p_evening * math.exp(-((h - C.P_EVENING_HOUR) ** 2) / C.LOAD_DENOM)
    )


def availability_factor(t: int) -> int:
    """
    Binary SMR availability a_SMR(t): 1 when operating, 0 during outage.

    Outage window is defined by config.SMR_OUTAGE_START (hour at which the
    outage begins) and config.SMR_OUTAGE_DURATION (hours). If SMR_OUTAGE_START
    is None the reactor is modelled as always available.
    """
    start = C.SMR_OUTAGE_START
    if start is None:
        return 1
    end = start + C.SMR_OUTAGE_DURATION
    return 0 if start <= t < end else 1


def generate_inputs(n_steps: int = C.N, seed: int = C.RNG_SEED) -> dict:
    """
    Build all time-varying input arrays for a full simulation run.

    Returns a dict with numpy arrays of length n_steps:
      G      : global horizontal irradiance [W/m^2]
      T_amb  : ambient temperature [degC]
      P_load : load demand [MW]
      a_SMR  : binary availability factor
    """
    rng = np.random.default_rng(seed)
    g = np.array([solar_irradiance(t, rng) for t in range(n_steps)])
    t_amb = np.array([ambient_temperature(t) for t in range(n_steps)])
    p_load = np.array([load_demand(t) for t in range(n_steps)])
    a_smr = np.array([availability_factor(t) for t in range(n_steps)], dtype=int)
    return {
        "G": g,
        "T_amb": t_amb,
        "P_load": p_load,
        "a_SMR": a_smr,
    }
