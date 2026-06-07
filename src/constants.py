from __future__ import annotations

# -- Display --

SEPARATOR: str = "=" * 65
SEPARATOR_THIN: str = "-" * 65

# -- Graph algorithm --

DIJKSTRA_INFINITE_COST: float = float("inf")
# sentinel for unreachable nodes in Dijkstra distance table

# -- Mathematical model --

ENERGY_ATTENUATION_COEFFICIENT: float = 0.05
# kW per km of cable — SIMULATED; models resistive losses in pressurized tunnels
# Reference: NASA ICES-2023-311 — cable sizing for lunar/Mars surface systems

# -- ESG thresholds --

NETWORK_DENSITY_IDEAL_MIN: float = 0.25
# SIMULATED — minimum edge density for acceptable redundancy in a colony network
# Below this: too many single points of failure

NETWORK_DENSITY_IDEAL_MAX: float = 0.60
# SIMULATED — above this: over-connected, excessive infrastructure cost

GLOBAL_EFFICIENCY_ALERT_THRESHOLD: float = 0.003
# SIMULATED — GE below this signals poor inter-module communication.
# Scale note: with inter-module distances in meters (50–1000 m), GE is typically in
# the range 0.001–0.010. A threshold of 0.003 corresponds to an effective average
# path length > 333 m, indicating poor connectivity for a compact colony.

CRITICAL_PRIORITY_THRESHOLD: int = 2
# Modules with priority <= this are classified as critical (life-supporting)

BRIDGE_REDUNDANCY_RECOMMENDATION: int = 2
# SIMULATED — if bridge count exceeds this, ESG recommends adding redundant connections

# -- Module energy thresholds --

HIGH_CONSUMPTION_KW: float = 10.0
# SIMULATED — modules above this are flagged for energy review in ESG analysis
