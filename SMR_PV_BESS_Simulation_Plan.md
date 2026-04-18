# Physics-Based Simulation of a Hybrid SMR-Solar-Battery Energy System for Reliable Low-Carbon Power in Malaysia

## Full Simulation Plan and Technical Specification

---

## Table of Contents

1. Project Overview
2. Input Data Specification
3. Section 1: Simulation Framework and Power Balance
4. Section 2: Solar PV Model
5. Section 3: SMR Model
6. Section 4: Battery Energy Storage Model
7. Section 5: Net Power and Dispatch Logic
8. Section 6: Energy Quantities
9. Section 7: Ramp-Rate and Stability Analysis
10. Section 8: Performance Metrics
11. Section 9: System Efficiency
12. Section 10: Validation
13. Section 11: Simulation Scenarios
14. Simulation Flowchart
15. Output Figures Specification

---

## 1. Project Overview

This project develops a physics-based simulation of a hybrid Small Modular Reactor (SMR), Solar Photovoltaic (PV), and Battery Energy Storage System (BESS) to study how such a system could support reliable and low-carbon electricity supply under Malaysian conditions.

**System Configuration:** Isolated standalone microgrid (no grid import/export). This is justified by framing the system as a remote Malaysian grid segment (e.g., Sabah or rural Sarawak) to stress-test the hybrid system under the most demanding conditions.

**Simulation Type:** Hourly time-step energy balance simulation.

**Core Question:** Can this hybrid system provide stable, efficient, and reliable low-carbon power under Malaysian operating conditions?

---

## 2. Input Data Specification

All input data is synthetic, generated using physically-based equations calibrated to Malaysian climatological conditions.

### 2.1 Fixed Parameters

#### Category A: Solar PV Parameters

| Symbol | Description | Value | Unit | Source/Justification |
|--------|-------------|-------|------|---------------------|
| η_ref | Reference PV efficiency at STC | 0.20 | dimensionless | Modern crystalline silicon panels |
| β | Temperature coefficient | 0.004 | /°C | Typical for c-Si panels |
| T_ref | Reference temperature (STC) | 25 | °C | Standard test condition |
| k | Ross coefficient (cell heating) | 0.03 | °C·m²/W | Rack-mounted, well-ventilated |
| A_PV | Total PV panel area | 50,000 | m² | Gives ~10 MW rated capacity |
| η_inv | Inverter efficiency | 0.96 | dimensionless | Typical grid-tied inverter |

#### Category B: SMR Parameters

| Symbol | Description | Value | Unit | Source/Justification |
|--------|-------------|-------|------|---------------------|
| P_th | Thermal power output | 100 | MW | Reference SMR scale |
| η_th | Thermal-to-electrical efficiency | 0.32 | dimensionless | Typical light-water SMR |
| P_SMR,rated | Electrical output (η_th × P_th) | 32 | MW | Derived |
| P_aux | Auxiliary/house load (0.05 × P_SMR,rated) | 1.6 | MW | Typical nuclear plant |
| a_SMR(t) | Availability factor | 1 or 0 | binary | 1 = operating, 0 = outage |

**Note:** The SMR operates as constant baseload. Malaysia does not currently operate any SMR, so the reactor is represented as a constant low-carbon generation source characterised by rated output and thermal efficiency. No neutron transport, reactor kinetics, or load-following is modelled.

#### Category C: Battery Parameters

| Symbol | Description | Value | Unit | Source/Justification |
|--------|-------------|-------|------|---------------------|
| E_bat,max | Maximum battery capacity | 100 | MWh | Utility-scale Li-ion |
| P_ch,max | Maximum charging power | 50 | MW | 0.5C rate |
| P_dis,max | Maximum discharging power | 50 | MW | 0.5C rate (symmetric) |
| η_ch | Charging efficiency | 0.95 | dimensionless | Li-ion typical |
| η_dis | Discharging efficiency | 0.95 | dimensionless | Li-ion typical |
| η_rt | Round-trip efficiency (η_ch × η_dis) | 0.9025 | dimensionless | Derived |
| SOC_min | Minimum state of charge | 0.10 | dimensionless | Protect battery life |
| SOC_max | Maximum state of charge | 0.90 | dimensionless | Protect battery life |
| SOC_0 | Initial state of charge | 0.50 | dimensionless | Neutral starting point |

#### Category D: Simulation Control Parameters

| Symbol | Description | Value | Unit |
|--------|-------------|-------|------|
| Δt | Time step | 1 | hour |
| N | Total time steps (7 days) | 168 | hours |
| t_start | Simulation start | 0 | hour (midnight, day 1) |

### 2.2 Time-Varying Inputs (Synthetic Profiles)

These are arrays with one value per hour, generated using the equations below.

#### Solar Irradiance G(t)

Computed from solar geometry plus a Beer-Lambert air-mass transmittance, so sunrise,
sunset, and the shape of the daily curve emerge from physics rather than a hard-coded
sine window.

```
For each hour t:
  n = DOY_START + t // 24          # day of year
  h = t mod 24                     # hour of day (solar time)

  # 1. Declination (Cooper's equation)
  δ = 23.45° × sin(2π × (284 + n) / 365)

  # 2. Hour angle (sun's position around solar noon)
  ω = 15° × (h - 12)

  # 3. Solar elevation angle
  sin(α) = sin(φ)·sin(δ) + cos(φ)·cos(δ)·cos(ω)

  if sin(α) > 0:
    # 4. Beer-Lambert with air mass
    AM = 1 / sin(α)
    G_clear(t) = G_sc × sin(α) × τ^AM

    # 5. Cloud noise (multiplicative)
    G(t) = max(G_clear(t) × (1 + noise), 0)    where noise ~ Uniform(-0.10, +0.10)
  else:
    G(t) = 0
```

Parameters: φ = 3.14° N (Kuala Lumpur), n₀ = DOY_START = 105 (mid-April annual-average),
G_sc = 1361 W/m² (solar constant), τ = 0.70 (clear-sky transmittance at AM = 1).

Expected noon peak ≈ 900–950 W/m² clear sky; daily total ≈ 5.5–6.5 kWh/m²/day clear
sky, converging toward the Malaysian annual average of 4.5–5.0 kWh/m²/day once realistic
cloud variability is included. Sunrise/sunset occur naturally at sin(α) = 0 (~6 AM and
~6 PM at this latitude).

For cloudy day scenario: reduce τ toward ~0.35–0.45, or draw k_t from a low-value
distribution for selected days (upgraded cloud model is a later iteration).

#### Ambient Temperature T_amb(t)

```
For each hour t:
  hour_of_day = t mod 24
  T_amb(t) = T_mean + T_swing × cos(2π × (hour_of_day - h_peak_T) / 24)
```

Parameters: T_mean = 28°C, T_swing = 4°C, h_peak_T = 14 (peak at 2 PM).

Range: 24°C at 02:00 (pre-dawn) to 32°C at 14:00 (afternoon). Consistent with Peninsular Malaysia.

(Note: an earlier draft used `sin((h − 14)/24)`, which numerically peaks at h = 20,
contradicting the stated "peak at 2 PM". The cos form above is the corrected version.)

#### Load Demand P_load(t)

```
For each hour t:
  hour_of_day = t mod 24
  P_load(t) = P_base + P_morning × exp(-(hour_of_day - h_morning)² / LOAD_DENOM)
                     + P_evening × exp(-(hour_of_day - h_evening)² / LOAD_DENOM)
```

Parameters: P_base = 25 MW, P_morning = 12 MW, P_evening = 15 MW,
h_morning = 10, h_evening = 20, LOAD_DENOM = 4 h² (σ ≈ 1.4 h, narrow peaks).

Tropical double-peak profile: morning commercial peak ~37 MW at 10 AM and
residential evening peak ~40 MW at 8 PM, falling back to the 25 MW baseload
overnight.

Weekend handling: days 5 and 6 of the simulation (Saturday, Sunday by convention
with sim day 0 = Monday) reduce both P_morning and P_evening by 15%. Controlled
by WEEKEND_DAYS and WEEKEND_REDUCTION in config.py.

---

## 3. Section 1: Simulation Framework and Power Balance

### 3.1 Governing Equation

The core physics of the simulation is conservation of energy applied at each time step. For an isolated standalone system:

```
P_SMR(t) + P_PV,use(t) + P_bat,dis(t) = P_load(t) + P_bat,ch(t) + P_curtail(t) + P_unmet(t)
```

**Left side:** all sources of power (SMR generation, usable solar output after inverter, battery discharge).

**Right side:** all sinks of power (load demand, battery charging, curtailed excess, unmet demand).

All losses are handled internally by subsystem efficiencies (η_th, η_PV, η_inv, η_ch, η_dis). No separate P_loss term is needed.

### 3.2 Design Decision

The system is modelled as isolated (no P_grid,in or P_grid,out). This is justified as a stress-test for a remote Malaysian grid segment. In an isolated system, unmet demand and curtailment are real consequences, making the scenario comparison more meaningful.

---

## 4. Section 2: Solar PV Model

### 4.1 PV Power Output

```
P_PV(t) = η_PV(t) × A_PV × G(t)
```

Where:
- P_PV(t) = solar PV electrical power output [W]
- η_PV(t) = effective PV efficiency [dimensionless]
- A_PV = total PV panel area [m²]
- G(t) = solar irradiance at time t [W/m²]

### 4.2 Temperature-Dependent Efficiency

```
η_PV(t) = η_ref × [1 − β × (T_cell(t) − T_ref)]
```

Where:
- η_ref = 0.20 (reference efficiency at STC)
- β = 0.004 /°C (temperature coefficient)
- T_ref = 25°C (reference temperature)
- T_cell(t) = PV cell temperature [°C]

This equation is the key physics feature of the PV model. Under Malaysian conditions (T_cell regularly 50–70°C), this produces a 5–15% efficiency reduction.

### 4.3 Cell Temperature (Simplified Ross Model)

```
T_cell(t) = T_amb(t) + k × G(t)
```

Where:
- T_amb(t) = ambient temperature [°C]
- k = 0.03 °C·m²/W (Ross coefficient)

### 4.4 Post-Inverter Usable Output

```
P_PV,use(t) = η_inv × P_PV(t)
```

Where η_inv = 0.96. This is the power that actually enters the system power balance.

### 4.5 Night-Time Constraint

```
If G(t) ≤ 0: P_PV(t) = 0, P_PV,use(t) = 0
```

---

## 5. Section 3: SMR Model

### 5.1 Thermal-to-Electrical Conversion

```
P_SMR(t) = η_th × P_th
```

Where:
- η_th = 0.32 (thermal efficiency)
- P_th = 100 MW (thermal power)
- P_SMR(t) = 32 MW (constant electrical output)

This is computed once and used at every time step. The SMR operates as constant baseload.

### 5.2 Net SMR Output (After Auxiliary Load)

```
P_SMR,net(t) = P_SMR(t) − P_aux
```

Where P_aux = 0.05 × P_SMR,rated = 1.6 MW. This accounts for coolant pumps, control systems, and ventilation.

Effective SMR output to the grid: P_SMR,net = 32 − 1.6 = 30.4 MW.

### 5.3 Availability Factor

```
P_SMR,actual(t) = a_SMR(t) × P_SMR,net(t)
```

Where a_SMR(t) = 1 (operating) or 0 (outage). Binary only.

Base case: a_SMR = 1 for all time steps.
Outage test: set a_SMR = 0 for a 12–24 hour period to test system resilience.

### 5.4 Justification for Constant Baseload

Since Malaysia does not currently operate any SMR, and because SMR designs are still in the licensing and development phase internationally, the SMR is represented as a constant baseload source. This is consistent with typical nuclear plant operation at full rated power for maximum economic return. The constant output creates a clear contrast with variable solar generation, isolating the dynamic physics of interest.

---

## 6. Section 4: Battery Energy Storage Model

### 6.1 State of Charge Update

```
SOC(t + Δt) = SOC(t) + [η_ch × P_bat,ch(t) × Δt / E_bat,max] − [P_bat,dis(t) × Δt / (η_dis × E_bat,max)]
```

Where:
- SOC(t) = state of charge at time t [dimensionless, 0 to 1]
- η_ch = 0.95 (charging efficiency, multiplied — some input power lost as heat)
- η_dis = 0.95 (discharging efficiency, divided — battery depletes more than load receives)
- P_bat,ch(t) = charging power [MW]
- P_bat,dis(t) = discharging power [MW]
- E_bat,max = 100 MWh (maximum capacity)

### 6.2 SOC Operational Constraints

```
SOC_min ≤ SOC(t) ≤ SOC_max
0.10 ≤ SOC(t) ≤ 0.90
```

### 6.3 Power Limits

```
0 ≤ P_bat,ch(t) ≤ P_ch,max = 50 MW
0 ≤ P_bat,dis(t) ≤ P_dis,max = 50 MW
```

### 6.4 Complementarity Constraint

```
P_bat,ch(t) × P_bat,dis(t) = 0    for all t
```

The battery cannot simultaneously charge and discharge. This is enforced by the dispatch logic in Section 5 (surplus and deficit are mutually exclusive).

### 6.5 Stored Energy

```
E_bat(t) = SOC(t) × E_bat,max
```

### 6.6 Round-Trip Efficiency

```
η_rt = η_ch × η_dis = 0.95 × 0.95 = 0.9025
```

### 6.7 Acknowledged but Neglected Effects

- **Self-discharge:** ~0.01–0.05%/hr for Li-ion. Negligible over a 7-day simulation compared to charge/discharge losses.
- **Degradation:** Capacity fades with cycling. Not modelled because the simulation period (7–30 days) is too short for significant degradation.

---

## 7. Section 5: Net Power and Dispatch Logic

### 7.1 Initialisation at Each Time Step

At the start of each time step, set all action variables to zero:

```
P_bat,ch(t) = 0
P_bat,dis(t) = 0
P_curtail(t) = 0
P_unmet(t) = 0
```

This guarantees the complementarity constraint and ensures every variable has a defined value.

### 7.2 Net Power Calculation

```
P_net(t) = P_SMR,actual(t) + P_PV,use(t) − P_load(t)
```

Note: P_PV,use (post-inverter) is used, not P_PV.

### 7.3 Surplus Case (P_net > 0)

If there is surplus power, charge the battery:

```
P_bat,ch(t) = min(P_net(t), P_ch,max, [SOC_max − SOC(t)] × E_bat,max / (η_ch × Δt))
```

The three terms ensure: (1) don't charge more than surplus, (2) don't exceed max charge rate, (3) don't overfill the battery.

Curtailment is the remaining surplus:

```
P_curtail(t) = P_net(t) − P_bat,ch(t)
```

### 7.4 Deficit Case (P_net < 0)

If there is deficit power, discharge the battery:

```
P_def(t) = P_load(t) − P_SMR,actual(t) − P_PV,use(t)

P_bat,dis(t) = min(P_def(t), P_dis,max, [SOC(t) − SOC_min] × E_bat,max × η_dis / Δt)
```

The three terms ensure: (1) don't discharge more than needed, (2) don't exceed max discharge rate, (3) don't drain below SOC_min.

Unmet demand is the remaining deficit:

```
P_unmet(t) = P_def(t) − P_bat,dis(t)
```

### 7.5 Balanced Case (P_net = 0)

All action variables remain at zero. Battery is idle, no curtailment, no unmet demand.

### 7.6 SOC Update

After determining charge/discharge power, update SOC using Section 4 Equation 6.1.

### 7.7 Known Limitation

This simulation uses a reactive dispatch strategy. The battery responds only to the current time step and has no knowledge of future demand. A predictive dispatch using load forecasting could improve battery utilisation but is beyond the physics scope of this study.

---

## 8. Section 6: Energy Quantities

Cumulative energy totals computed after the simulation loop completes.

### 8.1 Generation Energy

```
E_SMR = Σ P_SMR,actual(t) × Δt       (total SMR electrical energy)
E_PV,gross = Σ P_PV(t) × Δt          (total PV energy before inverter)
E_PV,net = Σ P_PV,use(t) × Δt        (total PV energy after inverter)
E_bat,dis = Σ P_bat,dis(t) × Δt      (total battery discharge energy)
E_bat,ch = Σ P_bat,ch(t) × Δt        (total battery charge energy)
```

### 8.2 Load and Unmet Energy

```
E_load = Σ P_load(t) × Δt            (total load demand)
E_served = Σ [P_load(t) − P_unmet(t)] × Δt    (total load served)
E_unmet = Σ P_unmet(t) × Δt          (total unmet demand)
```

### 8.3 Curtailed Energy

```
E_curtail = Σ P_curtail(t) × Δt      (total curtailed energy)
```

### 8.4 Inverter Loss

```
E_inv_loss = E_PV,gross − E_PV,net    (total inverter losses)
```

### 8.5 Net Battery Energy

```
E_bat,net = E_bat,dis − E_bat,ch
```

If negative: battery stored more than released (SOC increased over simulation). If positive: battery drained. Over a long simulation, this should be close to zero for sustainable operation.

---

## 9. Section 7: Ramp-Rate and Stability Analysis

### 9.1 Net Delivered Power

```
P_del(t) = P_SMR,actual(t) + P_PV,use(t) + P_bat,dis(t) − P_bat,ch(t)
```

This is what the load side actually receives at each time step.

### 9.2 Ramp Rate

```
R(t) = [P_del(t + Δt) − P_del(t)] / Δt
```

Unit: MW/hr. Measures how quickly power supply changes from one hour to the next.

### 9.3 Maximum Absolute Ramp

```
R_max = max |R(t)| over all t
```

Captures the worst-case single-hour fluctuation.

### 9.4 Average Absolute Ramp

```
R̄ = (1 / (N − 1)) × Σ |R(t)|
```

Captures overall smoothness across the simulation.

### 9.5 Standard Deviation of Ramp Rate

```
σ_R = sqrt[(1 / (N − 1)) × Σ (R(t) − R̄_signed)²]
```

Where R̄_signed is the mean of R(t) without absolute value. Statistical measure of ramp volatility.

### 9.6 Ramp Reduction Index

```
Ramp Reduction = (R̄_base − R̄_hybrid) / R̄_base × 100%
```

Compute for multiple scenario pairs:
- Solar only → Solar + Battery (battery smoothing effect)
- Solar only → SMR + Solar (baseload stabilisation effect)
- Solar only → SMR + Solar + Battery (full hybrid benefit)

---

## 10. Section 8: Performance Metrics

### 10.1 Load Served Fraction

```
f_served = E_served / E_load
```

Primary reliability metric. Value of 1.0 means all demand was met.

### 10.2 Loss of Power Supply Probability

```
LPSP = E_unmet / E_load
```

Lower value = better reliability. Mathematically equal to 1 − f_served.

### 10.3 Renewable Penetration

```
f_RE = E_PV,net / E_served
```

Use E_PV,net (post-inverter). Note: slightly undercounts renewable contribution since some battery discharge energy originated from solar surplus.

### 10.4 SMR Contribution Fraction

```
f_SMR = E_SMR / E_served
```

### 10.5 Generation Mix Fractions

```
f_RE,gen = E_PV,net / (E_PV,net + E_SMR)
f_SMR,gen = E_SMR / (E_PV,net + E_SMR)
```

These always sum to 1.0 and show the fraction of total generation from each source.

### 10.6 Curtailment Fraction

```
f_curtail = E_curtail / (E_PV,net + E_SMR)
```

### 10.7 Battery Cycle Count

```
N_cycles = E_bat,dis / E_bat,max
```

For context: Li-ion batteries are rated for 3000–6000 cycles. If simulation shows 1 cycle/day, estimated lifetime is 8–16 years.

### 10.8 Peak Unmet Demand

```
P_unmet,max = max P_unmet(t) over all t
```

Worst-case single-hour shortage. Useful for system sizing discussions.

---

## 11. Section 9: System Efficiency

### 11.1 Overall System Efficiency

```
η_sys = E_served / (E_SMR,in + E_solar,in)
```

Where:

```
E_solar,in = Σ A_PV × G(t) × Δt    (total solar radiation hitting panels)
E_SMR,in = Σ P_th(t) × Δt           (total reactor thermal energy)
```

Expected value: 10–20%. This is normal because solar panels convert only ~20% of incident radiation and SMR converts ~32% of thermal energy.

### 11.2 Subsystem Efficiency Breakdown

```
η_PV,system = E_PV,net / E_solar,in     (PV system efficiency including temperature and inverter losses)
η_SMR,system = E_SMR / E_SMR,in          (equals η_th = 0.32)
η_dispatch = E_served / (E_PV,net + E_SMR)  (dispatch efficiency accounting for curtailment and battery losses)
```

Report both overall η_sys and subsystem breakdown for detailed analysis.

---

## 12. Section 10: Validation

### 12.1 Energy Balance Error

At each time step:

```
ε(t) = [P_SMR,actual(t) + P_PV,use(t) + P_bat,dis(t)] − [P_load(t) + P_bat,ch(t) + P_curtail(t) + P_unmet(t)]
```

**Expected result: ε(t) = 0 exactly at every time step.** This checks code correctness, not data accuracy. It works with any data including synthetic data.

Global error metric:

```
ε_avg = (1/N) × Σ |ε(t)|
```

### 12.2 Boundary Condition Checks

| Condition | Expected Behaviour | Pass/Fail |
|-----------|-------------------|-----------|
| G(t) = 0 (nighttime) | P_PV(t) = 0 | |
| SOC(t) = SOC_max | P_bat,ch(t) = 0 | |
| SOC(t) = SOC_min | P_bat,dis(t) = 0 | |
| P_net > 0, battery full | P_curtail > 0 | |
| P_net < 0, battery empty | P_unmet > 0 | |

### 12.3 Expected Physical Trend Checks

Run simulation twice with one parameter changed (+20%), verify output moves in expected direction.

| Parameter Changed | Output Checked | Expected Trend | Observed |
|-------------------|---------------|----------------|----------|
| G (irradiance) ↑ | P_PV ↑ | ∂P_PV/∂G > 0 | |
| T_cell ↑ | η_PV ↓ | ∂η_PV/∂T_cell < 0 | |
| E_bat,max ↑ | E_unmet ↓ | ∂E_unmet/∂E_bat,max < 0 | |
| P_SMR,rated ↑ | E_unmet ↓ | ∂E_unmet/∂P_SMR,rated < 0 | |
| E_bat,max ↑ | E_curtail ↓ | ∂E_curtail/∂E_bat,max < 0 | |
| A_PV ↑ | E_unmet ↓ | ∂E_unmet/∂A_PV < 0 | |
| E_bat,max ↑ | R̄ ↓ | ∂R̄/∂E_bat,max < 0 | |

### 12.4 Scenario Comparison Validation

Expected progression across scenarios:

| Metric | Solar Only | Solar+Batt | SMR+Solar | Full Hybrid |
|--------|-----------|------------|-----------|-------------|
| f_served | Lowest | Higher | Higher | Highest |
| LPSP | Highest | Lower | Lower | Lowest |
| R̄ | Highest | Lower | Lower | Lowest |

If results don't follow this pattern, recheck the model.

---

## 13. Section 11: Simulation Scenarios

### 13.1 Scenario Definitions

All four scenarios use the same simulation code with different configuration flags.

**Scenario 1: Solar Only**
```
P_SMR,actual(t) = 0 for all t
P_bat,ch(t) = P_bat,dis(t) = 0 for all t (battery disabled)
```
Purpose: establish baseline. Shows how bad solar alone is.

**Scenario 2: Solar + Battery**
```
P_SMR,actual(t) = 0 for all t
Battery equations active
```
Purpose: show whether battery alone can fix solar variability.

**Scenario 3: SMR + Solar**
```
P_bat,ch(t) = P_bat,dis(t) = 0 for all t (battery disabled)
SMR active at constant baseload
```
Purpose: show the value of stable baseload without storage.

**Scenario 4: SMR + Solar + Battery (Full Hybrid)**
```
All components active
```
Purpose: demonstrate the full hybrid system. Should show best performance.

### 13.2 Optional Scenario 5: SMR Only

```
P_PV,use(t) = 0 for all t
P_bat,ch(t) = P_bat,dis(t) = 0 for all t
SMR active at constant baseload
```
Purpose: test if SMR alone is sufficient, or if solar and battery add value.

### 13.3 Implementation

One simulation function, called once per scenario. The scenario flag determines which components are active by setting their power to zero.

---

## 14. Simulation Flowchart

### 14.1 Overall Simulation Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                      SIMULATION INPUTS                          │
├────────────┬────────────┬──────────────┬────────────────────────┤
│ Solar Data │  SMR Data  │ Battery Data │      Load Data         │
│ G(t),T(t)  │ P_th, η_th │ E_max,η_ch   │      P_load(t)        │
└─────┬──────┴─────┬──────┴──────┬───────┴──────────┬────────────┘
      │            │             │                  │
      ▼            ▼             ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              FOR EACH TIME STEP t = 1 to N                      │
│                                                                 │
│  Step 1: Calculate P_PV,use(t)                                  │
│          T_cell → η_PV → P_PV → P_PV,use                       │
│                                                                 │
│  Step 2: Set P_SMR,actual(t) = a_SMR × (η_th × P_th − P_aux)   │
│                                                                 │
│  Step 3: Compute P_net = P_SMR + P_PV,use − P_load              │
│                                                                 │
│  Step 4: Dispatch Decision                                      │
│          ┌──────────────────┐                                   │
│          │   P_net > 0 ?    │                                   │
│          └────┬────────┬────┘                                   │
│          YES  │        │  NO                                    │
│          ▼    │        │    ▼                                   │
│     ┌─────────┴─┐   ┌──┴──────────┐                            │
│     │  SURPLUS   │   │   DEFICIT    │                           │
│     │ Charge bat │   │ Discharge   │                            │
│     │ Curtail    │   │ Unmet demand│                            │
│     └─────┬──────┘   └──────┬──────┘                            │
│           │                 │                                   │
│           ▼                 ▼                                   │
│  Step 5: Update SOC(t+Δt)                                       │
│                                                                 │
│  Step 6: Store all results for time t                           │
│                                                                 │
│  ──────────── Loop back to next t ────────────                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    POST-PROCESSING                              │
├──────────────────┬──────────────────┬───────────────────────────┤
│  Energy Totals   │   Performance    │       Stability           │
│ E_SMR, E_PV,     │ f_served, LPSP,  │    R̄, R_max,             │
│ E_load           │ f_RE             │    ramp reduction         │
└──────────────────┴──────────────────┴───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     VALIDATION                                  │
│           ε(t) = 0, trend checks, boundary checks               │
└─────────────────────────────────────────────────────────────────┘
```

### 14.2 Scenario Comparison Workflow

```
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────────┐
│ Scenario 1│ │ Scenario 2│ │ Scenario 3│ │  Scenario 4   │
│Solar only │ │Solar+Batt │ │SMR+Solar  │ │SMR+Solar+Batt │
└─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └──────┬────────┘
      │             │             │               │
      └─────────────┴──────┬──────┴───────────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │  Same simulation    │
                │  engine, run 4×     │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │  Collect results    │
                │  per scenario       │
                └──────────┬──────────┘
                           │
                           ▼
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│Summary table │ │ Time-series  │ │ Ramp reduction    │
│Metrics × 4   │ │ plots        │ │ bar chart         │
└──────────────┘ └──────────────┘ └──────────────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │ CONCLUSION            │
               │ Which config is most  │
               │ stable, and why       │
               └───────────────────────┘
```

---

## 15. Output Figures Specification

### Priority Figures (Top 10 — recommended for presentation)

#### Figure 1: Stacked Generation Plot
- **Type:** Stacked area chart with line overlay
- **X-axis:** Time (hours)
- **Y-axis:** Power (MW)
- **Data:** P_SMR,actual(t) stacked + P_PV,use(t) stacked + P_bat,dis(t) stacked, with P_load(t) as a black line overlay
- **Source equations:** Section 3 (P_SMR), Section 2 (P_PV,use), Section 5 (P_bat,dis), Input (P_load)
- **Purpose:** Hero figure — shows how all sources combine to meet demand

#### Figure 2: Battery SOC vs Time
- **Type:** Line chart
- **X-axis:** Time (hours)
- **Y-axis:** SOC (0 to 1)
- **Data:** SOC(t) with horizontal dashed lines at SOC_min (0.10) and SOC_max (0.90)
- **Source equation:** Section 4, Eq 6.1 (SOC update)
- **Purpose:** Shows battery cycling behaviour, depth of discharge, and utilisation

#### Figure 3: f_served Bar Chart Across Scenarios
- **Type:** Grouped bar chart
- **X-axis:** Scenarios 1–4
- **Y-axis:** f_served (0 to 1)
- **Data:** f_served for each scenario
- **Source equation:** Section 8, Eq 10.1
- **Purpose:** Most impactful comparison — directly shows reliability improvement

#### Figure 4: Average Ramp Rate Bar Chart
- **Type:** Grouped bar chart
- **X-axis:** Scenarios 1–4
- **Y-axis:** R̄ (MW/hr)
- **Data:** R̄ for each scenario
- **Source equation:** Section 7, Eq 9.4
- **Purpose:** Shows stability improvement from each added component

#### Figure 5: Energy Balance Error
- **Type:** Line chart
- **X-axis:** Time (hours)
- **Y-axis:** ε(t) (MW)
- **Data:** ε(t) at every time step (should be flat zero)
- **Source equation:** Section 10, Eq 12.1
- **Purpose:** Validation proof — confirms conservation of energy is satisfied

#### Figure 6: f_served vs Battery Size (Sensitivity)
- **Type:** Line chart with markers
- **X-axis:** E_bat,max (MWh) — values: 0, 50, 100, 150, 200, 250
- **Y-axis:** f_served (0 to 1)
- **Data:** Run full hybrid scenario 6 times with different E_bat,max values
- **Source equations:** Section 8 Eq 10.1, varied Section 4 E_bat,max
- **Purpose:** Shows how battery sizing affects reliability

#### Figure 7: Energy Contribution Pie Chart
- **Type:** Pie chart or donut chart
- **Slices:** E_SMR, E_PV,net, E_bat,dis (for full hybrid scenario)
- **Source equations:** Section 6, Eqs 8.1
- **Purpose:** Shows generation mix at a glance

#### Figure 8: Simulation Workflow Flowchart
- **Type:** Diagram (already created as interactive SVG above)
- **Purpose:** Explains simulation structure to judges

#### Figure 9: Unmet Demand vs Time
- **Type:** Bar chart or area chart
- **X-axis:** Time (hours)
- **Y-axis:** P_unmet(t) (MW)
- **Data:** P_unmet(t) for each scenario (overlaid or subplots)
- **Source equation:** Section 5, Eq 7.4 (P_unmet)
- **Purpose:** Shows when and how severely the system fails to meet demand

#### Figure 10: Ramp Reduction Index
- **Type:** Horizontal or vertical bar chart
- **X-axis:** Scenario pairs
- **Y-axis:** Ramp reduction (%)
- **Data:** Three bars: Solar→Solar+Batt, Solar→SMR+Solar, Solar→Full Hybrid
- **Source equation:** Section 7, Eq 9.6
- **Purpose:** Single-number quantification of stability improvement

### Additional Figures (if time permits)

#### Figure 11: Solar Irradiance and Temperature Profile
- **Type:** Dual-axis line chart
- **Data:** G(t) on left axis, T_amb(t) on right axis
- **Purpose:** Shows input data patterns

#### Figure 12: PV Efficiency Over Time
- **Type:** Line chart
- **Data:** η_PV(t)
- **Purpose:** Shows temperature derating effect under Malaysian conditions

#### Figure 13: Battery Charge/Discharge Power
- **Type:** Positive/negative bar chart
- **Data:** P_bat,ch(t) as positive, P_bat,dis(t) as negative
- **Purpose:** Shows battery activity pattern

#### Figure 14: Curtailment vs Time
- **Type:** Area chart
- **Data:** P_curtail(t) across scenarios
- **Purpose:** Shows wasted energy

#### Figure 15: Scenario Comparison Summary Table
- **Type:** Table (can be rendered as figure)
- **Data:** All metrics (f_served, LPSP, E_curtail, R̄, N_cycles, f_RE, f_SMR) × 4 scenarios
- **Purpose:** Single comprehensive comparison

#### Figure 16: Sensitivity Spider Chart
- **Type:** Radar/spider chart
- **Data:** Normalised sensitivity of f_served to: E_bat,max, A_PV, P_SMR,rated, G_peak
- **Purpose:** Shows which parameters most strongly affect reliability

#### Figure 17: Energy Disposition Pie Chart
- **Type:** Pie chart
- **Slices:** E_served, E_curtail, E_inv_loss, E_battery_loss
- **Purpose:** Shows where all generated energy went

---

## End of Simulation Plan

This document contains all equations, parameters, logic, and specifications needed to implement the complete simulation. All 10 priority figures can be generated directly from the equations defined in Sections 1–11 with no additional physics required.
