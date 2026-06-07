from __future__ import annotations

from .constants import (
    DIJKSTRA_INFINITE_COST,
    ENERGY_ATTENUATION_COEFFICIENT,
    NETWORK_DENSITY_IDEAL_MAX,
    NETWORK_DENSITY_IDEAL_MIN,
)
from .dijkstra import dijkstra_all_distances
from .enums import WeightType
from .graph import edge_count, get_active_module_ids
from .models import ColonyNetwork, Edge


def energy_path_cost(edges: list[Edge]) -> float:
    """P_rota = sum_e [ P_e * (1 + alpha * d_e / 1000) ].

    Models resistive cable losses: longer connections dissipate more energy.
    alpha = ENERGY_ATTENUATION_COEFFICIENT (kW/km). Source: NASA ICES-2023-311.
    """
    return sum(
        edge.energy_cost_kw * (1.0 + ENERGY_ATTENUATION_COEFFICIENT * edge.distance_m / 1000.0)
        for edge in edges
    )


def global_efficiency(network: ColonyNetwork) -> float:
    """GE = (1 / n*(n-1)) * sum_{i!=j} [1 / d(i,j)] using shortest distance (m).

    GE in [0, 1]. 1 = perfect connectivity; 0 = fully disconnected.
    Source: Latora & Marchiori, Physical Review Letters, 2001.
    """
    active = get_active_module_ids(network)
    n = len(active)
    if n < 2:
        return 0.0

    total_inverse_distance: float = 0.0
    for source in active:
        distances = dijkstra_all_distances(network, source, WeightType.DISTANCE)
        for target in active:
            if target != source:
                dist = distances[target]
                if dist > 0.0 and dist < DIJKSTRA_INFINITE_COST:
                    total_inverse_distance += 1.0 / dist

    return total_inverse_distance / (n * (n - 1))


def network_density(network: ColonyNetwork) -> float:
    """delta = 2|E| / (|V| * (|V|-1)) for undirected graphs.

    1.0 = complete graph; 0.0 = no edges.
    """
    n = len(network.modules)
    if n < 2:
        return 0.0
    e = edge_count(network)
    return (2 * e) / (n * (n - 1))


def density_status(density: float) -> str:
    """Classify network density against ESG thresholds."""
    status_map = [
        (density < NETWORK_DENSITY_IDEAL_MIN,  "ABAIXO DO IDEAL — risco de isolamento"),
        (density > NETWORK_DENSITY_IDEAL_MAX,  "ACIMA DO IDEAL — sobrecarga de infraestrutura"),
    ]
    return next((msg for condition, msg in status_map if condition), "IDEAL — redundância adequada")
