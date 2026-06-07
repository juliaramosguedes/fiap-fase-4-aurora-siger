from __future__ import annotations

from .models import ColonyNetwork
from .graph import get_neighbors, get_active_module_ids


def dfs_traverse(network: ColonyNetwork, start_id: str) -> list[str]:
    """Iterative DFS traversal from start_id. Returns visit order. O(V+E)."""
    visited: set[str] = set()
    stack: list[str] = [start_id]
    visit_order: list[str] = []

    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        visit_order.append(current)
        # push neighbors in reverse so leftmost neighbor is processed first
        for edge in reversed(get_neighbors(network, current)):
            if edge.target not in visited:
                stack.append(edge.target)

    return visit_order


def find_bridges(network: ColonyNetwork) -> list[tuple[str, str]]:
    """Tarjan's bridge-finding algorithm. Returns list of (u, v) critical edges. O(V+E).

    A bridge is an edge whose removal disconnects the graph — a single point of failure.
    Uses discovery time and low-link values to identify bridges without re-running BFS/DFS
    for each edge removal.
    """
    active = get_active_module_ids(network)
    if not active:
        return []

    discovery_time: dict[str, int] = {}
    low_link: dict[str, int] = {}   # min discovery time reachable via back edges
    bridges: list[tuple[str, str]] = []
    timer: list[int] = [0]          # mutable counter — Python closure workaround

    def _dfs(node: str, parent: str | None) -> None:
        discovery_time[node] = low_link[node] = timer[0]
        timer[0] += 1

        for edge in get_neighbors(network, node):
            neighbor = edge.target
            if neighbor not in discovery_time:
                _dfs(neighbor, node)
                low_link[node] = min(low_link[node], low_link[neighbor])
                # if low_link[neighbor] > discovery[node], no back edge bypasses this edge
                if low_link[neighbor] > discovery_time[node]:
                    bridges.append((node, neighbor))
            elif neighbor != parent:
                # back edge — update low_link to ancestor's discovery time
                low_link[node] = min(low_link[node], discovery_time[neighbor])

    for module_id in active:
        if module_id not in discovery_time:
            _dfs(module_id, None)

    return bridges
