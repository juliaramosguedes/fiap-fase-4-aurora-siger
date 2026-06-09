from __future__ import annotations

from collections import deque

from .models import ColonyNetwork
from .graph import get_neighbors


def bfs_traverse(network: ColonyNetwork, start_id: str) -> list[str]:
    """BFS traversal from start_id. Returns visit order. O(V+E)."""
    visited: set[str] = {start_id}
    queue: deque[str] = deque([start_id])
    visit_order: list[str] = []

    while queue:
        current = queue.popleft()
        visit_order.append(current)
        for edge in get_neighbors(network, current):
            if edge.target not in visited:
                visited.add(edge.target)
                queue.append(edge.target)

    return visit_order


def bfs_shortest_path(
    network: ColonyNetwork,
    start_id: str,
    end_id: str,
) -> list[str] | None:
    """BFS shortest path by hop count (unweighted). Returns node list or None."""
    if start_id == end_id:
        return [start_id]

    visited: set[str] = {start_id}
    # store full path to each node — memory trade-off justified for V≤108
    queue: deque[list[str]] = deque([[start_id]])

    while queue:
        path = queue.popleft()
        current = path[-1]
        for edge in get_neighbors(network, current):
            if edge.target == end_id:
                return path + [end_id]
            if edge.target not in visited:
                visited.add(edge.target)
                queue.append(path + [edge.target])

    return None


def bfs_reachable(network: ColonyNetwork, start_id: str) -> set[str]:
    """Return all module IDs reachable from start_id via active connections."""
    return set(bfs_traverse(network, start_id))


def is_network_connected(network: ColonyNetwork) -> bool:
    """True if all active modules are reachable from the first active module."""
    from .graph import get_active_module_ids
    active = get_active_module_ids(network)
    if not active:
        return True
    reachable = bfs_reachable(network, active[0])
    return set(active) == reachable
