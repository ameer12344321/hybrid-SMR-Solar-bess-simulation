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


# =============================================================================
# Category E: Solar Geometry and Site Parameters
# =============================================================================

# Symbol        : phi
# Description   : Site latitude (Kuala Lumpur)
# Unit          : degrees (North positive)
# Justification : Representative Peninsular Malaysia population center
PHI_LAT = 3.14

# Symbol        : n_0
# Description   : Day of year at simulation start (mid-April)
# Unit          : day index (1 = Jan 1)
# Justification : Annual-average insolation conditions for Malaysia
DOY_START = 105

# Symbol        : G_sc
# Description   : Solar constant (extraterrestrial irradiance at mean Earth-Sun distance)
# Unit          : W/m^2
# Justification : IAU 2015 value
G_SC = 1361.0

# Symbol        : tau
# Description   : Clear-sky atmospheric transmittance at AM=1
# Unit          : dimensionless
# Justification : Typical tropical clear-sky value; applied as tau^AM for air-mass dependence
TAU_ATM = 0.70

# Symbol        : noise_amp
# Description   : Amplitude of multiplicative cloud-noise term on G(t)
# Unit          : dimensionless
# Justification : Matches plan's +/-10% uniform noise representing cloud variability
G_NOISE = 0.10

# Symbol        : seed
# Description   : RNG seed for reproducible synthetic inputs
# Unit          : integer
# Justification : Ensures identical runs for validation across scenarios
RNG_SEED = 42


# =============================================================================
# Category F: Ambient Temperature Profile Parameters
# =============================================================================

# Symbol        : T_mean
# Description   : Mean ambient temperature (diurnal average)
# Unit          : degC
# Justification : Peninsular Malaysia annual average
T_MEAN = 28.0

# Symbol        : T_swing
# Description   : Half-amplitude of the diurnal temperature swing
# Unit          : degC
# Justification : Typical tropical diurnal range (~8 degC peak-to-trough)
T_SWING = 4.0

# Symbol        : h_peak_T
# Description   : Hour of day at which T_amb peaks (afternoon max)
# Unit          : hour of day (0-23)
# Justification : Malaysian afternoon peak around 2 PM
T_PEAK_HOUR = 14


# =============================================================================
# Category G: Load Demand Profile Parameters
# =============================================================================

# Symbol        : P_base
# Description   : Baseline load (24-hour floor)
# Unit          : MW
# Justification : Residential + always-on commercial baseload
P_BASE = 25.0

# Symbol        : P_morning
# Description   : Morning peak amplitude (above baseline)
# Unit          : MW
# Justification : Office/commercial startup around 10 AM
P_MORNING = 12.0

# Symbol        : P_evening
# Description   : Evening peak amplitude (above baseline)
# Unit          : MW
# Justification : Residential evening consumption around 8 PM
P_EVENING = 15.0

# Symbol        : h_morning
# Description   : Hour at which morning peak is centred
# Unit          : hour of day (0-23)
# Justification : Typical commercial startup
P_MORNING_HOUR = 10

# Symbol        : h_evening
# Description   : Hour at which evening peak is centred
# Unit          : hour of day (0-23)
# Justification : Typical residential evening peak
P_EVENING_HOUR = 20

# Symbol        : denom
# Description   : Denominator of Gaussian peaks exp(-(h-h_peak)^2 / LOAD_DENOM)
# Unit          : hour^2
# Justification : Yields sigma = sqrt(2) ~ 1.4 h (sharp peaks per plan)
LOAD_DENOM = 4.0

# Symbol        : weekend_reduction
# Description   : Fractional reduction of peak amplitudes on weekend days
# Unit          : dimensionless
# Justification : Lower commercial/industrial activity on weekends
WEEKEND_REDUCTION = 0.15

# Symbol        : weekend_days
# Description   : Simulation day indices (0 = first day) treated as weekend
# Unit          : tuple of day indices
# Justification : Convention: sim day 0 = Monday, so days 5-6 = Sat/Sun
WEEKEND_DAYS = (5, 6)


# =============================================================================
# Category H: SMR Availability Parameters
# =============================================================================

# Symbol        : outage_start
# Description   : Hour index at which a planned SMR outage begins
# Unit          : hour (None = no outage)
# Justification : Set to a value to run the outage-resilience scenario
SMR_OUTAGE_START = None

# Symbol        : outage_duration
# Description   : Duration of the SMR outage in hours
# Unit          : hours
# Justification : Plan suggests 12-24 hour outage test
SMR_OUTAGE_DURATION = 0
