from __future__ import annotations

import math

# -- Colony configuration --

COLONY_CREW_SIZE: int = 1000
# SpaceX Starship architecture — initial colony target capacity.
# Source: Musk, E. (2017). Making Humans a Multi-Planetary Species. New Space, 5(2), 46-61.

_FASE3_CREW_SIZE: int = 6
# NASA DRA 5.0 reference crew (Fase 3 baseline — Drake, 2009).

SCALE_EXPONENT: float = 0.5
# Economy-of-scale exponent for non-LSS shared infrastructure.
# 0.5 (square-root law) applies to systems with large sharing benefits
# (communications, power distribution, research, logistics).

LSS_SCALE_EXPONENT: float = 0.7
# Life support scales closer to linear because air and water processing
# volumes are proportional to crew count; sharing benefits are limited.
# Sources: NASA CELSS NIH (2019); ECLSS design rationale (NASA NTRS).

SCALE_FACTOR: float = (COLONY_CREW_SIZE / _FASE3_CREW_SIZE) ** SCALE_EXPONENT
# ≈ 12.91 — non-LSS modules scale by this factor.

LSS_SCALE_FACTOR: float = (COLONY_CREW_SIZE / _FASE3_CREW_SIZE) ** LSS_SCALE_EXPONENT
# ≈ 35.93 — life-support modules (ATM, WAT) scale by this factor.

# -- Energy consumption baseline (mixed exponent — derived from Fase 3) --
# Fase 3: LSS=14 kW, other modules=32 kW, total=46 kW for 6 people.
# Fase 4: LSS×0.7 = 14×35.93 = 503 kW; other×0.5 = 32×12.91 = 413 kW; total ≈ 916 kW.
# Colony graph totals 1,030 kW (scenarios calibrated to round values above baseline).
# Source anchor: Hartwick et al., Nature Astronomy (2023); NASA CELSS NIH (2019).

_LSS_FASE3_KW: float = 14.0
_OTHER_FASE3_KW: float = 32.0
TOTAL_CONSUMPTION_BASELINE_KW: float = round(
    _LSS_FASE3_KW * LSS_SCALE_FACTOR + _OTHER_FASE3_KW * SCALE_FACTOR, 1
)
# ≈ 916 kW — reference for energy budget validation (mixed 0.5/0.7 exponents).

# -- Energy generation: solar (scaled from Fase 3) --
# Fase 3: 1 field × 1,000 m² (arXiv:2410.00066). Scale: 3 large fields × 2,900 m².

SOLAR_ARRAY_COUNT: int = 3
# SIMULATED — 3 large solar array fields in scenarios graph.
# Physical scale: 3 × 2,900 m² = 8,700 m² total vs 1,000 m² in Fase 3.
# Each field ≈ 4.3 Fase 3 arrays; 3 fields ≈ 13 Fase 3 arrays ≈ SCALE_FACTOR × 1.

SOLAR_PANEL_AREA_M2: float = 2900.0
# m² per field; 1,000 m² (Fase 3) × SCALE_FACTOR ≈ 2,910 → rounded to 2,900 m².
# Source: arXiv:2410.00066 — reference array sizing.

SOLAR_PANEL_EFFICIENCY: float = 0.29
# Unchanged from Fase 3 — high-efficiency cells; McMillon-Brown et al. (2020).

MARS_SURFACE_IRRADIANCE_WM2: float = 500.0
# Unchanged from Fase 3 — SIMULATED (590 W/m² top-of-atm minus ~15% absorption).

SOLAR_PEAK_POWER_KW: float = round(MARS_SURFACE_IRRADIANCE_WM2 * SOLAR_PANEL_AREA_M2 * SOLAR_PANEL_EFFICIENCY / 1000.0, 1)
# ≈ 420.5 kW peak per field (daytime only).

SOLAR_DAY_FRACTION: float = 12.0 / 24.6
# Daytime fraction of Martian sol; source: NASA Mars Fact Sheet.

SOLAR_AVERAGE_POWER_KW: float = round(SOLAR_PEAK_POWER_KW * SOLAR_DAY_FRACTION * SOLAR_ARRAY_COUNT, 1)
# ≈ 614.6 kW average 24h from all 3 fields combined — nearly exactly covers baseline.

# -- Energy generation: wind (scaled from Fase 3) --
# Fase 3: 2 E33 turbines (1 reference + 1 redundant), 24 kW/turbine avg (best sites).
# Source: Hartwick et al., Nature Astronomy (2023); arXiv:2410.00066.

WIND_TURBINE_COUNT: int = 26
# Physical turbines in colony — Fase 3 count (2) × SCALE_FACTOR ≈ 25.8, rounded to 26.
# Graph has 2 WND zone nodes (each representing ~13 physical turbines).
# Each turbine: ~24 kW average at top-3 wind sites (Hartwick et al., 2023).

WIND_AVERAGE_POWER_KW_PER_TURBINE: float = 24.0
# kW/turbine diurnal avg at best sites — Hartwick et al., Nature Astronomy (2023).

WIND_TOTAL_AVERAGE_KW: float = WIND_TURBINE_COUNT * WIND_AVERAGE_POWER_KW_PER_TURBINE
# ≈ 624 kW from wind alone — provides full colony redundancy against solar failure.

# -- Energy generation: combined budget --

TOTAL_GENERATION_AVERAGE_KW: float = SOLAR_AVERAGE_POWER_KW + WIND_TOTAL_AVERAGE_KW
# ≈ 1,239 kW average — satisfies dual-source requirement
# (solar + wind as project requirement, despite NASA nuclear preference).
# Safety margin: 1239 / 1030 ≈ 1.20× (daytime surplus charges batteries for calm nights).

# -- Energy storage: batteries (scaled from Fase 3) --
# Fase 3: 3 × 312 kWh = 936 kWh (arXiv:2410.00066).

BATTERY_BANK_COUNT: int = 52
# SIMULATED — sized for worst-case calm night (no wind, full 1,030 kW load).
# Design rule (same as Fase 3): usable ≥ peak_consumption × 12.6 h.
# 52 × 312 × 0.8 = 12,979 kWh usable ≥ 1,030 × 12.6 = 12,978 kWh required.
# With night wind (624 kW): battery draw reduces to 406 × 12.6 = 5,116 kWh — 2.5× margin.
# Graph: 4 BAT zone nodes (each representing 13 physical banks).

BATTERY_CAPACITY_KWH: float = 312.0
# kWh per bank — unchanged from Fase 3 (arXiv:2410.00066).

BATTERY_TOTAL_CAPACITY_KWH: float = BATTERY_BANK_COUNT * BATTERY_CAPACITY_KWH
# 52 × 312 = 16,224 kWh total storage.

BATTERY_MIN_PCT: float = 20.0
# Safety reserve — unchanged from Fase 3 (SIMULATED).

BATTERY_MIN_KWH: float = BATTERY_TOTAL_CAPACITY_KWH * (BATTERY_MIN_PCT / 100)
# 3,244.8 kWh unusable reserve.

BATTERY_USABLE_KWH: float = BATTERY_TOTAL_CAPACITY_KWH - BATTERY_MIN_KWH
# 12,979.2 kWh usable.

BATTERY_NIGHT_REQUIREMENT_KWH: float = round(1030.0 * 12.6, 1)
# 12,978 kWh — worst-case Martian night (12.6 h, 1,030 kW, no wind contribution).
# 12,979 kWh usable ≥ 12,978 kWh — satisfies design margin (same method as Fase 3).

# -- Graph algorithm --

DIJKSTRA_INFINITE_COST: float = float("inf")

# -- Mathematical model --

ENERGY_ATTENUATION_COEFFICIENT: float = 0.05
# kW per km of cable — SIMULATED; models resistive losses in pressurized tunnels.
# Reference: NASA ICES-2023-311 — cable sizing for lunar/Mars surface systems.

# -- ESG thresholds --

NETWORK_DENSITY_IDEAL_MIN: float = 0.015
# SIMULATED — lower bound for a 108-node colonial infrastructure graph.
# Infrastructure graphs grow sparser with scale; at 108 nodes, density ~2-4% is
# structurally normal. Below 1.5%: insufficient path redundancy for a colony.

NETWORK_DENSITY_IDEAL_MAX: float = 0.08
# SIMULATED — upper bound at 108-node scale. Above 8%: over-engineered topology
# that increases construction and maintenance costs unnecessarily.

GLOBAL_EFFICIENCY_ALERT_THRESHOLD: float = 0.002
# SIMULATED — GE below this signals poor inter-module communication.
# Scale note: with 108 nodes and inter-module distances in meters (10–900 m), GE is
# typically 0.002–0.005. Threshold of 0.002 corresponds to effective average
# path length > 500 m, indicating poor connectivity for a compact colony.

CRITICAL_PRIORITY_THRESHOLD: int = 1
# Modules with priority <= this are inviolable — the emergency energy manager
# will never include them in shutdown candidates.

BRIDGE_REDUNDANCY_RECOMMENDATION: int = 40
# SIMULATED — if bridge count exceeds this, ESG recommends redundant connections.
# Scale note: 108-node hierarchical graph. 68 numbered leaf nodes each have only
# their parent edge — structurally unavoidable bridges. ~40 is the expected
# minimum (inter-complex + unique-leaf bridges). Above this = modelling concern.

HIGH_CONSUMPTION_KW: float = 20.0
# SIMULATED — modules above this are flagged for energy review in ESG analysis.
# Threshold = ~3.5× average node consumption (615 kW / 108 nodes ≈ 5.7 kW avg).
# At 30 kW only ICU triggered; 20 kW captures DRL leaves, EMG, ICU, SRG leaves.
