from __future__ import annotations

from dataclasses import dataclass, field

from .enums import EdgeType, ModuleStatus


@dataclass
class Module:
    """A colony subsystem — vertex in the infrastructure graph."""

    module_id: str                      # e.g. "CTL-01"
    name: str                           # display name
    priority: int                       # 1 = inviolável; higher = shutdown first
    energy_consumption_kw: float        # kW nominal — 24h operation
    storage_capacity_m3: float          # m³ — SIMULATED
    communication_priority: int         # 1 = high comm need; 5 = low
    status: ModuleStatus = ModuleStatus.OPERATIONAL


@dataclass(frozen=True)
class Edge:
    """Bidirectional connection between two colony modules — edge in the graph."""

    source: str             # module_id
    target: str             # module_id
    distance_m: float       # physical distance in meters — SIMULATED
    energy_cost_kw: float   # kW to maintain this link — SIMULATED
    latency_ms: float       # communication latency in ms — SIMULATED
    edge_type: EdgeType


@dataclass
class ColonyNetwork:
    """Complete colony infrastructure: modules as vertices, edges as connections."""

    modules: dict[str, Module]
    adjacency_list: dict[str, list[Edge]] = field(default_factory=dict)
