"""
Configuration file for the Hybrid SMR-Solar-BESS simulation.

All fixed parameters are defined here, matching Section 2.1 of
SMR_PV_BESS_Simulation_Plan.md. Every parameter is labelled with:
  - Symbol        : name used in the plan's equations
  - Description   : what it represents physically
  - Unit          : SI / engineering unit
  - Justification : why this value was chosen
"""

# =============================================================================
# Category A: Solar PV Parameters
# =============================================================================

# Symbol        : eta_ref
# Description   : Reference PV panel efficiency at Standard Test Conditions (STC)
# Unit          : dimensionless
# Justification : Typical for modern crystalline-silicon panels
ETA_REF = 0.20

# Symbol        : beta
# Description   : Temperature coefficient for PV efficiency derating
# Unit          : 1/degC
# Justification : Typical value for c-Si panels
BETA = 0.004

# Symbol        : T_ref
# Description   : Reference cell temperature (Standard Test Conditions)
# Unit          : degC
# Justification : Standard test condition benchmark (STC)
T_REF = 25.0

# Symbol        : k
# Description   : Ross coefficient that links irradiance to cell-heating above T_amb
# Unit          : degC * m^2 / W
# Justification : Rack-mounted, well-ventilated panels
K_ROSS = 0.03

# Symbol        : A_PV
# Description   : Total PV panel area of the solar farm
# Unit          : m^2
# Justification : Sized to give roughly 10 MW rated capacity at STC
A_PV = 50_000.0

# Symbol        : eta_inv
# Description   : DC-to-AC inverter efficiency applied to raw PV output
# Unit          : dimensionless
# Justification : Typical grid-tied string/central inverter
ETA_INV = 0.96


# =============================================================================
# Category B: SMR (Small Modular Reactor) Parameters
# =============================================================================

# Symbol        : P_th
# Description   : Reactor thermal power output (heat produced in the core)
# Unit          : MW (thermal)
# Justification : Reference scale for a Small Modular Reactor
P_TH = 100.0

# Symbol        : eta_th
# Description   : Thermal-to-electrical conversion efficiency of the steam cycle
# Unit          : dimensionless
# Justification : Typical for a light-water SMR
ETA_TH = 0.32

# Symbol        : P_SMR_rated
# Description   : Gross electrical output of the SMR (eta_th * P_th)
# Unit          : MW (electrical)
# Justification : Derived quantity
P_SMR_RATED = ETA_TH * P_TH  # 32 MW

# Symbol        : P_aux
# Description   : Auxiliary / house load (coolant pumps, controls, ventilation)
# Unit          : MW
# Justification : Taken as 5% of rated electrical output (typical nuclear plant)
P_AUX = 0.05 * P_SMR_RATED  # 1.6 MW

# Symbol        : P_SMR_net
# Description   : Net electrical output delivered to the grid (P_SMR_rated - P_aux)
# Unit          : MW
# Justification : Derived quantity used in the dispatch calculation
P_SMR_NET = P_SMR_RATED - P_AUX  # 30.4 MW

# Symbol        : a_SMR(t)
# Description   : Binary availability factor (1 = operating, 0 = outage)
# Unit          : dimensionless (binary)
# Justification : Generated per time step by inputs.availability_factor()


# =============================================================================
# Category C: Battery (BESS) Parameters
# =============================================================================

# Symbol        : E_bat_max
# Description   : Maximum usable battery capacity
# Unit          : MWh
# Justification : Utility-scale lithium-ion storage system
E_BAT_MAX = 100.0

# Symbol        : P_ch_max
# Description   : Maximum charging power
# Unit          : MW
# Justification : 0.5C charge rate
P_CH_MAX = 50.0

# Symbol        : P_dis_max
# Description   : Maximum discharging power
# Unit          : MW
# Justification : 0.5C discharge rate (symmetric with charging)
P_DIS_MAX = 50.0

# Symbol        : eta_ch
# Description   : Charging efficiency (fraction of input energy stored)
# Unit          : dimensionless
# Justification : Typical Li-ion system value
ETA_CH = 0.95

# Symbol        : eta_dis
# Description   : Discharging efficiency (fraction of stored energy delivered)
# Unit          : dimensionless
# Justification : Typical Li-ion system value
ETA_DIS = 0.95

# Symbol        : eta_rt
# Description   : Round-trip efficiency (eta_ch * eta_dis)
# Unit          : dimensionless
# Justification : Derived quantity
ETA_RT = ETA_CH * ETA_DIS  # 0.9025

# Symbol        : SOC_min
# Description   : Minimum allowed state of charge
# Unit          : dimensionless (fraction of E_bat_max)
# Justification : Lower bound to protect cycle life
SOC_MIN = 0.10

# Symbol        : SOC_max
# Description   : Maximum allowed state of charge
# Unit          : dimensionless (fraction of E_bat_max)
# Justification : Upper bound to protect cycle life
SOC_MAX = 0.90

# Symbol        : SOC_0
# Description   : Initial state of charge at t = 0
# Unit          : dimensionless (fraction of E_bat_max)
# Justification : Neutral starting point halfway between SOC_min and SOC_max
SOC_0 = 0.50


# =============================================================================
# Category D: Simulation Control Parameters
# =============================================================================

# Symbol        : delta_t
# Description   : Simulation time step
# Unit          : hour
# Justification : Hourly resolution is standard for energy-balance studies
DT = 1.0

# Symbol        : N
# Description   : Total number of time steps (7 days x 24 hours)
# Unit          : hours
# Justification : One-week horizon captures weekday/weekend dynamics
N = 168

# Symbol        : t_start
# Description   : Simulation start hour (midnight of day 1)
# Unit          : hour index
# Justification : Conventional start-of-day anchor
T_START = 0
