from __future__ import annotations

from .enums import WeightType
from .models import ColonyNetwork, Edge, Module


def build_adjacency_list(
    modules: dict[str, Module],
    edges: list[Edge],
) -> dict[str, list[Edge]]:
    """Build undirected adjacency list. Each edge is stored in both directions."""
    adjacency: dict[str, list[Edge]] = {module_id: [] for module_id in modules}
    for edge in edges:
        adjacency[edge.source].append(edge)
        reverse = Edge(
            source=edge.target,
            target=edge.source,
            distance_m=edge.distance_m,
            energy_cost_kw=edge.energy_cost_kw,
            latency_ms=edge.latency_ms,
            edge_type=edge.edge_type,
        )
        adjacency[edge.target].append(reverse)
    return adjacency


def get_edge_weight(edge: Edge, weight_type: WeightType) -> float:
    """Return the numeric weight for the given criterion."""
    weight_selector = {
        WeightType.DISTANCE: edge.distance_m,
        WeightType.ENERGY:   edge.energy_cost_kw,
        WeightType.LATENCY:  edge.latency_ms,
    }
    return weight_selector[weight_type]


def get_neighbors(network: ColonyNetwork, module_id: str) -> list[Edge]:
    """Return all edges leaving module_id, filtering offline neighbors."""
    return [
        edge for edge in network.adjacency_list.get(module_id, [])
        if network.modules[edge.target].status.value != "OFFLINE"
    ]


def get_active_module_ids(network: ColonyNetwork) -> list[str]:
    """All module IDs whose status is not OFFLINE, in insertion order."""
    from .enums import ModuleStatus
    return [mid for mid, m in network.modules.items() if m.status != ModuleStatus.OFFLINE]


def edge_count(network: ColonyNetwork) -> int:
    """Total number of unique edges (each undirected edge counted once)."""
    return sum(len(edges) for edges in network.adjacency_list.values()) // 2
