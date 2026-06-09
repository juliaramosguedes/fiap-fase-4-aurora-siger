from __future__ import annotations

from dataclasses import dataclass, field

from .enums import EdgeType, ModuleStatus


@dataclass
class Module:
    """A colony subsystem — vertex in the infrastructure graph."""

    module_id: str
    name: str
    priority: int                    # 1 = inviolable; higher = shutdown first
    energy_consumption_kw: float     # kW nominal — 24h operation (SIMULATED)
    storage_capacity_m3: float       # m³ operational footprint (SIMULATED)
    communication_priority: int      # 1 = critical real-time; 5 = periodic
    status: ModuleStatus = ModuleStatus.OPERATIONAL
    parent_id: str | None = None     # None = top-level complex or standalone
    unit_count: int = 1              # physical units represented by this node


@dataclass(frozen=True)
class Edge:
    """Bidirectional connection between two colony modules — edge in the graph."""

    source: str
    target: str
    distance_m: float       # physical distance in meters (SIMULATED)
    energy_cost_kw: float   # kW to maintain this link (SIMULATED)
    latency_ms: float       # communication latency in ms (SIMULATED)
    edge_type: EdgeType


@dataclass
class ColonyNetwork:
    """Complete colony infrastructure: modules as vertices, edges as connections."""

    modules: dict[str, Module]
    adjacency_list: dict[str, list[Edge]] = field(default_factory=dict)
