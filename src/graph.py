from __future__ import annotations

from collections import deque

from .enums import ModuleStatus, WeightType
from .models import ColonyNetwork, Edge, Module


def build_adjacency_list(
    modules: dict[str, Module],
    edges: list[Edge],
) -> dict[str, list[Edge]]:
    """Build undirected adjacency list. Each edge is stored in both directions."""
    adjacency: dict[str, list[Edge]] = {module_id: [] for module_id in modules}
    for edge in edges:
        adjacency[edge.source].append(edge)
        adjacency[edge.target].append(Edge(
            source=edge.target,
            target=edge.source,
            distance_m=edge.distance_m,
            energy_cost_kw=edge.energy_cost_kw,
            latency_ms=edge.latency_ms,
            edge_type=edge.edge_type,
        ))
    return adjacency


def get_edge_weight(edge: Edge, weight_type: WeightType) -> float:
    """Return the numeric weight for the given criterion."""
    return {
        WeightType.DISTANCE: edge.distance_m,
        WeightType.ENERGY:   edge.energy_cost_kw,
        WeightType.LATENCY:  edge.latency_ms,
    }[weight_type]


def get_neighbors(network: ColonyNetwork, module_id: str) -> list[Edge]:
    """Return all edges leaving module_id, filtering offline neighbors."""
    return [
        edge for edge in network.adjacency_list.get(module_id, [])
        if network.modules[edge.target].status != ModuleStatus.SHUTDOWN
    ]


def get_active_module_ids(network: ColonyNetwork) -> list[str]:
    """All module IDs whose status is not OFFLINE, in insertion order."""
    return [mid for mid, m in network.modules.items() if m.status != ModuleStatus.SHUTDOWN]


def edge_count(network: ColonyNetwork) -> int:
    """Total number of unique edges (each undirected edge counted once)."""
    return sum(len(edges) for edges in network.adjacency_list.values()) // 2


# ---------------------------------------------------------------------------
# Hierarchy
# ---------------------------------------------------------------------------


def get_children(network: ColonyNetwork, parent_id: str) -> list[str]:
    """Return IDs of all direct children of parent_id."""
    return [mid for mid, m in network.modules.items() if m.parent_id == parent_id]


def get_descendants(network: ColonyNetwork, root_id: str) -> list[str]:
    """Return all descendant IDs (children, grandchildren, ...) in BFS order."""
    result: list[str] = []
    queue: deque[str] = deque(get_children(network, root_id))
    while queue:
        current = queue.popleft()
        result.append(current)
        queue.extend(get_children(network, current))
    return result


def get_top_level_modules(network: ColonyNetwork) -> list[str]:
    """Return IDs of modules with no parent (standalone or root complexes)."""
    return [mid for mid, m in network.modules.items() if m.parent_id is None]


# ---------------------------------------------------------------------------
# Cascade operations
# ---------------------------------------------------------------------------


def cascade_offline(network: ColonyNetwork, module_id: str) -> list[str]:
    """Set module_id and all descendants OFFLINE. Returns IDs of affected modules."""
    targets = [module_id] + get_descendants(network, module_id)
    affected = [mid for mid in targets if network.modules[mid].status != ModuleStatus.SHUTDOWN]
    for mid in affected:
        network.modules[mid].status = ModuleStatus.SHUTDOWN
    return affected


def cascade_restore(network: ColonyNetwork, module_id: str) -> list[str]:
    """Restore module_id and all descendants to OPERATIONAL. Returns restored IDs."""
    targets = [module_id] + get_descendants(network, module_id)
    restored = [mid for mid in targets if network.modules[mid].status == ModuleStatus.SHUTDOWN]
    for mid in restored:
        network.modules[mid].status = ModuleStatus.OPERATIONAL
    return restored


def compute_shutdown_candidates(network: ColonyNetwork, budget_kw: float) -> list[str]:
    """Greedy emergency manager: suggest top-level complexes to shut down.

    Selects candidates with highest priority number first (lowest operational
    importance), then highest total energy savings. Priority 1 modules are
    never candidates. Returns IDs of complexes to shut down via cascade_offline.
    """
    def complex_energy(module_id: str) -> float:
        all_ids = [module_id] + get_descendants(network, module_id)
        return sum(
            network.modules[mid].energy_consumption_kw
            for mid in all_ids
            if network.modules[mid].status == ModuleStatus.OPERATIONAL
        )

    current_kw = sum(
        m.energy_consumption_kw
        for m in network.modules.values()
        if m.status == ModuleStatus.OPERATIONAL
    )

    if current_kw <= budget_kw:
        return []

    candidates = [
        mid for mid in get_top_level_modules(network)
        if network.modules[mid].priority > 1
        and network.modules[mid].status == ModuleStatus.OPERATIONAL
    ]
    candidates.sort(key=lambda mid: (-network.modules[mid].priority, -complex_energy(mid)))

    to_shutdown: list[str] = []
    remaining = current_kw
    for mid in candidates:
        if remaining <= budget_kw:
            break
        to_shutdown.append(mid)
        remaining -= complex_energy(mid)

    return to_shutdown
