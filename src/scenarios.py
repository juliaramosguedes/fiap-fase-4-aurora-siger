"""
Aurora Siger colony network — reference topology for a 1,000-person Mars colony.

Scale reference:
  Musk, E. (2017). Making Humans a Multi-Planetary Species. New Space, 5(2), 46-61.
  SpaceX Starship architecture targets 1,000-person initial colony capacity.

Structure:
  10 top-level complexes (1 standalone + 9 parents)
  24 group nodes (multi-unit subsystems with numbered leaves)
   7 unique leaf nodes (single-unit direct children)
  68 numbered leaf nodes (individual physical units under group nodes)
  ─────────────────────────────────────────────────
  108 total nodes · 137 unique edges

  Naming convention:
    CTL, PWR, LSS … — unique node (no suffix when only one exists)
    SOL, WND, BAT … — group node (represents N physical units; unit_count=N)
    SOL-01, SOL-02  — individual unit leaf (physical instance under its group)

All distances, energy costs, and latencies are SIMULATED.
Colony layout: roughly circular, ~2 km diameter. Central core at 0-200 m radius,
inner ring at 200-400 m, outer zones at 400-1000 m, remote outposts up to 900 m.
"""

from __future__ import annotations

from .constants import BATTERY_BANK_COUNT, SOLAR_ARRAY_COUNT, WIND_TURBINE_COUNT
from .enums import EdgeType, ModuleStatus
from .graph import build_adjacency_list
from .models import ColonyNetwork, Edge, Module


def _build_colony_data() -> tuple[dict[str, Module], list[Edge]]:
    """
    Returns all colony modules and edges.

    Energy split: group node = 10% of total energy (coordination overhead).
                  each leaf  = 90% / unit_count (proportional to its unit).
    """
    nodes: list[Module] = []
    edges: list[Edge] = []

    S = EdgeType.SURFACE_PATH
    T = EdgeType.PRESSURIZED_TUNNEL
    W = EdgeType.WIRELESS

    def add(module_id: str, name: str, priority: int,
            energy: float, storage: float, comm: int, parent: str | None = None) -> None:
        nodes.append(Module(module_id, name, priority, energy, storage, comm, parent_id=parent))

    def expand(base_id: str, name: str, priority: int,
               energy: float, storage: float, comm: int,
               parent: str, count: int,
               edge_type: EdgeType = T, dist: float = 50.0,
               physical_count: int | None = None) -> None:
        """Create group node + leaf nodes + internal edges for a multi-unit subsystem.

        count          — number of zone leaf nodes in the graph (topology).
        physical_count — actual physical units represented (defaults to count).
                         Use when one zone leaf represents many physical devices,
                         e.g., a wind turbine zone leaf may represent 13 turbines.
        """
        actual_units = physical_count if physical_count is not None else count
        nodes.append(Module(base_id, name, priority,
                            round(energy * 0.10, 2), round(storage * 0.10),
                            comm, parent_id=parent, unit_count=actual_units))
        leaf_energy  = round(energy  * 0.90 / count, 2)
        leaf_storage = round(storage * 0.90 / count)
        for i in range(1, count + 1):
            nodes.append(Module(f"{base_id}-{i:02d}", name, priority,
                                leaf_energy, leaf_storage, comm, parent_id=base_id))
            edges.append(Edge(base_id, f"{base_id}-{i:02d}", dist, 0.1, 0.5, edge_type))

    # ------------------------------------------------------------------
    # Standalone — command hub
    # ------------------------------------------------------------------
    add("CTL", "Centro de Controle", 1, 15.0, 300.0, 1)

    # ------------------------------------------------------------------
    # PWR — power generation and distribution
    # ------------------------------------------------------------------
    add("PWR", "Complexo de Energia", 1, 5.0, 100.0, 1)
    expand("SOL", "Campo Solar Fotovoltaico",       1,  2.0, 5000.0, 2, "PWR", 3, S, 300.0, physical_count=SOLAR_ARRAY_COUNT)
    expand("WND", "Parque de Turbinas Eólicas",     1,  2.0, 3000.0, 3, "PWR", 2, S, 375.0, physical_count=WIND_TURBINE_COUNT)
    expand("BAT", "Bancos de Baterias",             1,  8.0,  800.0, 2, "PWR", 4, T,  10.0, physical_count=BATTERY_BANK_COUNT)
    add("DST", "Rede de Distribuição Elétrica",     1, 10.0,  200.0, 1, "PWR")

    # ------------------------------------------------------------------
    # LSS — life support
    # ------------------------------------------------------------------
    add("LSS", "Sistema de Suporte de Vida", 1, 5.0, 150.0, 1)
    expand("ATM", "Controle Atmosférico",  1, 300.0, 6000.0, 1, "LSS", 3, T, 40.0)
    expand("WAT", "Reciclagem de Água",    1, 200.0, 8000.0, 1, "LSS", 3, T, 50.0)

    # ------------------------------------------------------------------
    # HAB — habitat and residential
    # ------------------------------------------------------------------
    add("HAB", "Complexo Habitacional", 2, 5.0, 500.0, 2)
    expand("QRT", "Módulos Residenciais",          2, 30.0, 8000.0, 3, "HAB", 8, T, 60.0)
    expand("REC", "Hub de Recreação",              4, 15.0, 2000.0, 5, "HAB", 2, T, 80.0)
    expand("DIN", "Refeitório e Cozinha",          3, 25.0, 1500.0, 4, "HAB", 3, T, 70.0)
    add("EDU", "Centro Educacional",               4, 10.0, 1200.0, 5, "HAB")

    # ------------------------------------------------------------------
    # MED — medical complex
    # ------------------------------------------------------------------
    add("MED", "Complexo Médico", 2, 5.0, 200.0, 1)
    add("EMG", "Pronto-Socorro",               2, 20.0,  500.0, 1, "MED")
    expand("SRG", "Centro Cirúrgico",          2, 25.0,  400.0, 2, "MED", 2, T, 50.0)
    add("ICU", "UTI",                          2, 30.0,  300.0, 1, "MED")
    expand("CLN", "Clínicas Gerais",           3, 12.0,  600.0, 3, "MED", 3, T, 60.0)
    expand("DEN", "Clínica Odontológica",      4,  8.0,  200.0, 4, "MED", 2, T, 70.0)
    expand("PSY", "Centro de Saúde Mental",    4,  6.0,  250.0, 4, "MED", 2, T, 80.0)

    # ------------------------------------------------------------------
    # COM — communications
    # ------------------------------------------------------------------
    add("COM", "Sistema de Comunicação", 3, 5.0, 100.0, 1)
    expand("INT", "Hub de Rede Interna",              3,  8.0, 150.0, 1, "COM", 2, T,  30.0)
    expand("EXT", "Array de Comunicação com a Terra", 3, 20.0, 500.0, 2, "COM", 2, S,  60.0)
    expand("TOR", "Torres de Transmissão",            3, 12.0, 300.0, 2, "COM", 3, S, 100.0)

    # ------------------------------------------------------------------
    # AGR — agriculture
    # ------------------------------------------------------------------
    add("AGR", "Complexo de Agricultura", 3, 5.0, 200.0, 3)
    expand("GRH", "Complexo de Estufas",        3, 40.0, 5000.0, 3, "AGR", 5, T,  60.0)
    expand("FPR", "Processamento de Alimentos", 4, 18.0, 1000.0, 4, "AGR", 2, T,  50.0)

    # ------------------------------------------------------------------
    # LOG — logistics and transport
    # ------------------------------------------------------------------
    add("LOG", "Complexo de Logística", 4, 5.0, 200.0, 3)
    expand("TRN", "Depósito de Veículos",              4, 15.0, 1500.0, 3, "LOG", 2, T,  80.0)
    expand("WRH", "Armazém Central",                   4, 10.0, 3000.0, 4, "LOG", 3, T,  40.0)
    expand("EVA", "Câmara de Atividade Extravehicular", 3, 20.0, 800.0, 2, "LOG", 2, T, 100.0)

    # ------------------------------------------------------------------
    # MIN — ISRU mining operations
    # ------------------------------------------------------------------
    add("MIN", "Complexo de Mineração ISRU", 4, 5.0, 200.0, 4)
    expand("DRL", "Operações de Perfuração",             4, 45.0, 500.0, 4, "MIN", 2, S, 150.0)
    expand("REF", "Refinaria de Regolito",               4, 35.0, 600.0, 4, "MIN", 2, S,  75.0)
    expand("RST", "Armazenamento de Recursos Minerados", 5,  8.0, 1500.0, 5, "MIN", 3, T,  20.0)

    # ------------------------------------------------------------------
    # RES — scientific research
    # ------------------------------------------------------------------
    add("RES", "Centro de Pesquisa Científica", 5, 5.0, 200.0, 4)
    add("GEO", "Laboratório de Geologia Planetária", 5,  8.0, 300.0, 5, "RES")
    add("AGT", "Laboratório de Pesquisa Agrícola",   5, 10.0, 400.0, 5, "RES")
    add("BIO", "Laboratório de Biologia e Ciências", 5, 12.0, 350.0, 4, "RES")
    expand("ENV", "Monitoramento Ambiental",          4,  6.0, 200.0, 4, "RES", 2, S, 100.0)

    # ------------------------------------------------------------------
    # Backbone edges — inter-complex connections (22 edges)
    # ------------------------------------------------------------------
    backbone: list[Edge] = [
        Edge("CTL", "COM",  80.0, 0.3,  1.5, T),
        Edge("CTL", "LSS", 120.0, 0.4,  1.0, T),
        Edge("CTL", "PWR", 150.0, 0.5,  1.5, T),
        Edge("CTL", "HAB", 250.0, 0.8,  3.0, T),
        Edge("CTL", "MED", 220.0, 0.7,  2.5, T),
        Edge("CTL", "LOG", 350.0, 1.2,  5.0, S),
        Edge("PWR", "LSS", 100.0, 0.3,  1.0, T),
        Edge("PWR", "HAB", 200.0, 0.6,  2.0, T),
        Edge("PWR", "AGR", 500.0, 1.8,  7.0, S),
        Edge("PWR", "MIN", 800.0, 3.0, 12.0, S),
        Edge("LSS", "HAB", 150.0, 0.5,  2.0, T),
        Edge("LSS", "AGR", 400.0, 1.4,  6.0, S),
        Edge("HAB", "MED", 150.0, 0.5,  2.0, T),
        Edge("HAB", "AGR", 400.0, 1.4,  6.0, S),
        Edge("HAB", "LOG", 300.0, 1.0,  5.0, S),
        Edge("MED", "RES", 250.0, 0.8,  3.0, T),
        Edge("COM", "RES", 350.0, 0.5,  8.0, W),
        Edge("AGR", "LOG", 200.0, 0.7,  4.0, S),
        Edge("MIN", "LOG", 400.0, 1.4,  6.0, S),
        Edge("MIN", "RES", 300.0, 1.0,  5.0, S),
        Edge("RES", "AGR", 250.0, 0.8,  5.0, S),
        Edge("COM", "HAB", 200.0, 0.6,  2.5, T),
    ]

    # ------------------------------------------------------------------
    # Parent-to-child: complex → direct children (31 edges)
    # ------------------------------------------------------------------
    parent_child: list[Edge] = [
        # PWR internals
        Edge("PWR", "SOL", 900.0, 3.5, 15.0, S),
        Edge("PWR", "WND", 750.0, 2.8, 12.0, S),
        Edge("PWR", "BAT",  40.0, 0.1,  1.0, T),
        Edge("PWR", "DST",  30.0, 0.1,  0.5, T),
        # LSS internals
        Edge("LSS", "ATM",  40.0, 0.1,  0.5, T),
        Edge("LSS", "WAT",  50.0, 0.2,  1.0, T),
        # HAB internals
        Edge("HAB", "QRT",  60.0, 0.2,  1.5, T),
        Edge("HAB", "REC",  80.0, 0.3,  2.0, T),
        Edge("HAB", "DIN",  70.0, 0.2,  1.5, T),
        Edge("HAB", "EDU",  90.0, 0.3,  2.0, T),
        # MED internals
        Edge("MED", "EMG",  30.0, 0.1,  0.5, T),
        Edge("MED", "SRG",  50.0, 0.2,  1.0, T),
        Edge("MED", "ICU",  45.0, 0.1,  1.0, T),
        Edge("MED", "CLN",  60.0, 0.2,  1.5, T),
        Edge("MED", "DEN",  70.0, 0.2,  1.5, T),
        Edge("MED", "PSY",  80.0, 0.3,  2.0, T),
        # COM internals
        Edge("COM", "INT",  30.0, 0.1,  0.5, T),
        Edge("COM", "EXT", 120.0, 0.5,  3.0, S),
        Edge("COM", "TOR", 200.0, 0.8,  5.0, S),
        # AGR internals
        Edge("AGR", "GRH",  60.0, 0.2,  1.5, T),
        Edge("AGR", "FPR",  50.0, 0.2,  1.0, T),
        # LOG internals
        Edge("LOG", "TRN",  80.0, 0.3,  2.0, T),
        Edge("LOG", "WRH",  40.0, 0.1,  1.0, T),
        Edge("LOG", "EVA", 100.0, 0.4,  2.5, T),
        # MIN internals
        Edge("MIN", "DRL", 300.0, 1.2,  8.0, S),
        Edge("MIN", "REF", 150.0, 0.6,  5.0, S),
        Edge("MIN", "RST",  60.0, 0.2,  1.5, T),
        # RES internals
        Edge("RES", "GEO",  60.0, 0.2,  1.5, T),
        Edge("RES", "AGT",  80.0, 0.3,  2.0, T),
        Edge("RES", "BIO",  70.0, 0.2,  1.5, T),
        Edge("RES", "ENV", 100.0, 0.4,  3.0, S),
    ]

    # ------------------------------------------------------------------
    # Cross-complex: child-to-child operational flows (17 edges)
    # ------------------------------------------------------------------
    cross: list[Edge] = [
        Edge("BAT", "DST",   35.0, 0.1,  0.5, T),  # battery → distribution (bypass parent)
        Edge("DST", "ATM",   80.0, 0.3,  1.0, T),  # power line → atmospheric control
        Edge("WAT", "GRH",  360.0, 1.2,  5.0, T),  # water recycling → greenhouses
        Edge("GRH", "FPR",   40.0, 0.1,  1.0, T),  # harvest → food processing
        Edge("FPR", "WRH",  250.0, 0.8,  4.0, T),  # processed food → warehouse
        Edge("DRL", "REF",  100.0, 0.4,  4.0, S),  # drilling → refinery
        Edge("REF", "RST",   50.0, 0.2,  1.5, T),  # refinery → resource storage
        Edge("RST", "WRH",  400.0, 1.5,  7.0, S),  # mined resources → central warehouse
        Edge("GEO", "DRL",  450.0, 1.8,  8.0, S),  # geology informs drilling
        Edge("AGT", "GRH",  300.0, 1.0,  5.0, T),  # ag research → greenhouses
        Edge("INT", "CTL",   70.0, 0.2,  1.0, T),  # network hub → control center
        Edge("EMG", "QRT",  180.0, 0.6,  3.0, T),  # emergency → quarters (evacuation)
        Edge("EMG", "SRG",   25.0, 0.1,  0.5, T),  # emergency → surgery
        Edge("SRG", "ICU",   30.0, 0.1,  0.5, T),  # surgery → ICU
        Edge("ICU", "CLN",   40.0, 0.1,  1.0, T),  # ICU → clinics
        Edge("EVA", "TRN",   80.0, 0.3,  2.0, T),  # EVA bay → transport depot
        Edge("TOR", "EXT",  150.0, 0.3,  4.0, W),  # towers relay → external array
    ]

    edges.extend(backbone + parent_child + cross)
    return {m.module_id: m for m in nodes}, edges


def build_aurora_colony() -> ColonyNetwork:
    """Build the complete Aurora Siger colony network — 108 nodes, 137 edges."""
    modules, edges = _build_colony_data()
    adjacency = build_adjacency_list(modules, edges)
    return ColonyNetwork(modules=modules, adjacency_list=adjacency)
