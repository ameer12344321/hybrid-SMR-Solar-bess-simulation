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
    """TODO: implement per plan Section 2.2 (diurnal sine, peak at 2 PM)."""
    raise NotImplementedError


def load_demand(t: int, weekend: bool = False) -> float:
    """TODO: implement per plan Section 2.2 (double-Gaussian peaks)."""
    raise NotImplementedError


def availability_factor(t: int) -> int:
    """TODO: implement per plan Section 2.1 Category B (binary 1/0, default 1)."""
    return 1


def generate_inputs(n_steps: int = C.N, seed: int = C.RNG_SEED) -> dict:
    """
    Build all time-varying input arrays for a full simulation run.

    Currently populates only G(t); other fields are zero-filled placeholders
    until their generator functions are implemented.
    """
    rng = np.random.default_rng(seed)
    g = np.array([solar_irradiance(t, rng) for t in range(n_steps)])
    return {
        "G": g,
        "T_amb": np.zeros(n_steps),
        "P_load": np.zeros(n_steps),
        "a_SMR": np.ones(n_steps, dtype=int),
    }
