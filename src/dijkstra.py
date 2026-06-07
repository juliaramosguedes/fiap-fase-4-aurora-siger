from __future__ import annotations

import heapq

from .constants import DIJKSTRA_INFINITE_COST
from .enums import WeightType
from .graph import get_edge_weight, get_neighbors
from .models import ColonyNetwork


def dijkstra_shortest_path(
    network: ColonyNetwork,
    start_id: str,
    end_id: str,
    weight_type: WeightType,
) -> tuple[list[str], float]:
    """Dijkstra's algorithm. Returns (path, total_cost). Path is [] if unreachable.

    Uses a min-heap (heapq) for O((V+E)logV) time. Suitable for sparse graphs.
    """
    distances: dict[str, float] = {mid: DIJKSTRA_INFINITE_COST for mid in network.modules}
    distances[start_id] = 0.0
    predecessors: dict[str, str | None] = {mid: None for mid in network.modules}

    # heap entries: (cumulative_cost, module_id)
    heap: list[tuple[float, str]] = [(0.0, start_id)]

    while heap:
        current_cost, current = heapq.heappop(heap)

        if current_cost > distances[current]:
            continue  # stale entry

        if current == end_id:
            break

        for edge in get_neighbors(network, current):
            weight = get_edge_weight(edge, weight_type)
            new_cost = current_cost + weight
            if new_cost < distances[edge.target]:
                distances[edge.target] = new_cost
                predecessors[edge.target] = current
                heapq.heappush(heap, (new_cost, edge.target))

    if distances[end_id] == DIJKSTRA_INFINITE_COST:
        return [], DIJKSTRA_INFINITE_COST

    return _reconstruct_path(predecessors, start_id, end_id), distances[end_id]


def dijkstra_all_distances(
    network: ColonyNetwork,
    start_id: str,
    weight_type: WeightType,
) -> dict[str, float]:
    """Dijkstra from start_id to all reachable nodes. Used for global efficiency calculation."""
    distances: dict[str, float] = {mid: DIJKSTRA_INFINITE_COST for mid in network.modules}
    distances[start_id] = 0.0
    heap: list[tuple[float, str]] = [(0.0, start_id)]

    while heap:
        current_cost, current = heapq.heappop(heap)
        if current_cost > distances[current]:
            continue
        for edge in get_neighbors(network, current):
            weight = get_edge_weight(edge, weight_type)
            new_cost = current_cost + weight
            if new_cost < distances[edge.target]:
                distances[edge.target] = new_cost
                heapq.heappush(heap, (new_cost, edge.target))

    return distances


def _reconstruct_path(
    predecessors: dict[str, str | None],
    start_id: str,
    end_id: str,
) -> list[str]:
    """Walk predecessor chain from end to start and reverse."""
    path: list[str] = []
    current: str | None = end_id
    while current is not None:
        path.append(current)
        current = predecessors[current]
    path.reverse()
    return path if path[0] == start_id else []
