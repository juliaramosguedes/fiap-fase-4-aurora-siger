from __future__ import annotations

from .enums import EdgeType, ModuleStatus
from .graph import build_adjacency_list
from .models import ColonyNetwork, Edge, Module


def _build_modules() -> dict[str, Module]:
    """Thirteen colony modules keyed by ID. Priority 1 = life-critical; 5 = research."""
    # Energy consumption: SIMULATED — proportional to criticality and operational scope
    # Storage capacity: SIMULATED — based on module function
    # Communication priority: 1 = critical real-time link; 5 = periodic data transfer
    entries = [
        Module("CTL-01", "Centro de Controle",        1, 8.0,  50.0,  1),
        Module("ENE-01", "Armazenamento de Energia",  1, 4.0, 500.0,  2),
        Module("OXY-01", "Produção de Oxigênio",      1, 12.0,  80.0, 1),
        Module("HAB-01", "Habitação",                 2, 7.0, 200.0,  2),
        Module("MED-01", "Suporte Médico",            2, 5.0,  60.0,  1),
        Module("CEN-01", "Centro Médico",             2, 9.0, 120.0,  1),
        Module("COM-01", "Comunicação",               3, 3.0,  20.0,  1),
        Module("TOR-01", "Torre de Comunicação",      3, 4.0,  15.0,  1),
        Module("AGR-01", "Agricultura",               4, 6.0, 800.0,  3),
        Module("REC-01", "Processamento de Recursos", 4, 10.0, 400.0, 3),
        Module("LAB-01", "Laboratório Científico",    5, 5.0,  90.0,  4),
        Module("PES-01", "Centro de Pesquisa",        5, 6.0, 100.0,  4),
        Module("ATM-01", "Laboratório Atmosférico",   5, 4.0,  70.0,  5),
    ]
    return {m.module_id: m for m in entries}


def _build_edges() -> list[Edge]:
    """Twenty-two colony connections. All distances/costs/latencies are SIMULATED.

    Topology design:
    - CTL-01 is the hub (6 direct connections) — matches its role as command center
    - Life-critical modules (ENE, OXY, MED) are close to CTL (short tunnels)
    - Research cluster (LAB, PES, ATM) is further out, interconnected
    - AGR and REC are on the colony periphery
    """
    T = EdgeType.PRESSURIZED_TUNNEL
    S = EdgeType.SURFACE_PATH
    W = EdgeType.WIRELESS

    return [
        # CTL-01 hub connections
        Edge("CTL-01", "HAB-01", 120.0, 0.5, 2.0, T),
        Edge("CTL-01", "ENE-01",  80.0, 0.3, 1.0, T),
        Edge("CTL-01", "OXY-01", 100.0, 0.4, 2.0, T),
        Edge("CTL-01", "COM-01", 150.0, 0.6, 3.0, S),
        Edge("CTL-01", "TOR-01", 200.0, 0.8, 4.0, S),
        Edge("CTL-01", "MED-01", 130.0, 0.5, 2.0, T),
        # Habitat cluster
        Edge("HAB-01", "MED-01",  90.0, 0.4, 2.0, T),
        Edge("HAB-01", "AGR-01", 200.0, 0.7, 4.0, S),
        Edge("HAB-01", "OXY-01", 110.0, 0.4, 2.0, T),
        Edge("HAB-01", "CEN-01", 100.0, 0.4, 2.0, T),
        # Energy cluster
        Edge("ENE-01", "OXY-01",  60.0, 0.2, 1.0, T),
        Edge("ENE-01", "REC-01", 180.0, 0.7, 3.0, S),
        # Medical cluster
        Edge("OXY-01", "MED-01",  95.0, 0.4, 2.0, T),
        Edge("MED-01", "CEN-01",  70.0, 0.3, 1.0, T),
        # Research cluster
        Edge("CEN-01", "LAB-01", 140.0, 0.5, 3.0, S),
        Edge("CEN-01", "ATM-01", 160.0, 0.6, 3.0, S),
        Edge("LAB-01", "PES-01",  80.0, 0.3, 1.0, T),
        Edge("LAB-01", "ATM-01",  90.0, 0.3, 2.0, T),
        Edge("ATM-01", "PES-01",  50.0, 0.2, 1.0, T),
        # Agriculture / resource periphery
        Edge("AGR-01", "REC-01", 150.0, 0.6, 3.0, S),
        # Communications backbone
        Edge("COM-01", "TOR-01", 250.0, 0.9, 5.0, W),
        Edge("PES-01", "TOR-01", 200.0, 0.7, 4.0, S),
    ]


def build_aurora_colony() -> ColonyNetwork:
    """Build the complete Aurora Siger colony network — fixed reference topology."""
    modules = _build_modules()
    edges = _build_edges()
    adjacency = build_adjacency_list(modules, edges)
    return ColonyNetwork(modules=modules, adjacency_list=adjacency)
