"""
SIGIC — Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia
Aurora Siger · Fase 4 · FIAP — Ciência da Computação · Julia Ramos (RM568988)

Arquivo principal de execução: python main.py
Navegação: menu interativo no terminal.
Algoritmos implementados: BFS, DFS (Tarjan bridges), Dijkstra.
"""

from src.bfs import bfs_reachable, bfs_shortest_path, bfs_traverse, is_network_connected
from src.constants import SEPARATOR
from src.dfs import dfs_traverse, find_bridges
from src.dijkstra import dijkstra_shortest_path
from src.display import (
    display_adjacency_matrix,
    display_algorithms_submenu,
    display_bfs_path,
    display_bfs_result,
    display_connectivity_status,
    display_dfs_result,
    display_dijkstra_result,
    display_dijkstra_weight_submenu,
    display_edge_list,
    display_energy_path_cost,
    display_global_efficiency,
    display_main_menu,
    display_math_submenu,
    display_module_detail,
    display_module_list,
    display_simulation_failure,
    display_simulations_submenu,
    display_sustainability_report,
    display_view_submenu,
)
from src.enums import ModuleStatus, WeightType
from src.graph import edge_count, get_active_module_ids
from src.math_model import density_status, energy_path_cost, global_efficiency, network_density
from src.models import ColonyNetwork
from src.scenarios import build_aurora_colony


def _prompt_module_id(network: ColonyNetwork, prompt: str = "   ID do módulo: ") -> str | None:
    """Ask user for a module ID and validate it exists. Returns None if invalid."""
    module_id = input(prompt).strip().upper()
    if module_id not in network.modules:
        print(f"   Anomalia detectada. '{module_id}' não registrado na rede.")
        return None
    return module_id


# ---------------------------------------------------------------------------
# [1] View network
# ---------------------------------------------------------------------------


def _handle_view_network(network: ColonyNetwork) -> None:
    while True:
        display_view_submenu()
        choice = input("   Opção: ").strip()
        VIEW_HANDLERS = {
            "1": lambda: display_module_list(network),
            "2": lambda: display_edge_list(network),
            "3": lambda: display_adjacency_matrix(network),
        }
        if choice == "0":
            break
        handler = VIEW_HANDLERS.get(choice)
        if handler:
            handler()
        else:
            print("   Opção inválida.")


# ---------------------------------------------------------------------------
# [2] Query module
# ---------------------------------------------------------------------------


def _handle_query_module(network: ColonyNetwork) -> None:
    display_module_list(network)
    module_id = _prompt_module_id(network)
    if module_id:
        display_module_detail(network, module_id)


# ---------------------------------------------------------------------------
# [3] Algorithms
# ---------------------------------------------------------------------------


def _handle_bfs(network: ColonyNetwork) -> None:
    print()
    print("   BFS — Exploração por largura")
    display_module_list(network)
    start_id = _prompt_module_id(network, "   ID do módulo de partida: ")
    if not start_id:
        return
    visit_order = bfs_traverse(network, start_id)
    display_bfs_result(network, start_id, visit_order)

    print("   Calcular caminho mínimo (por saltos) até outro módulo? [s/n]")
    if input("   ").strip().lower() == "s":
        end_id = _prompt_module_id(network, "   ID do módulo de destino: ")
        if end_id:
            path = bfs_shortest_path(network, start_id, end_id)
            display_bfs_path(network, start_id, end_id, path)


def _handle_dfs(network: ColonyNetwork) -> None:
    print()
    print("   DFS — Exploração por profundidade")
    display_module_list(network)
    start_id = _prompt_module_id(network, "   ID do módulo de partida: ")
    if not start_id:
        return
    visit_order = dfs_traverse(network, start_id)
    bridges = find_bridges(network)
    display_dfs_result(network, start_id, visit_order, bridges)


def _handle_dijkstra(network: ColonyNetwork) -> None:
    print()
    print("   Dijkstra — Caminho mínimo ponderado")
    display_module_list(network)
    start_id = _prompt_module_id(network, "   ID do módulo de origem: ")
    if not start_id:
        return
    end_id = _prompt_module_id(network, "   ID do módulo de destino: ")
    if not end_id:
        return

    display_dijkstra_weight_submenu()
    weight_choice = input("   Critério de peso [1/2/3]: ").strip()
    WEIGHT_MAP = {
        "1": WeightType.DISTANCE,
        "2": WeightType.ENERGY,
        "3": WeightType.LATENCY,
    }
    weight_type = WEIGHT_MAP.get(weight_choice)
    if not weight_type:
        print("   Opção inválida.")
        return

    path, total_cost = dijkstra_shortest_path(network, start_id, end_id, weight_type)
    display_dijkstra_result(network, start_id, end_id, path, total_cost, weight_type)


def _handle_algorithms(network: ColonyNetwork) -> None:
    while True:
        display_algorithms_submenu()
        choice = input("   Opção: ").strip()
        ALGO_HANDLERS = {
            "1": lambda: _handle_bfs(network),
            "2": lambda: _handle_dfs(network),
            "3": lambda: _handle_dijkstra(network),
        }
        if choice == "0":
            break
        handler = ALGO_HANDLERS.get(choice)
        if handler:
            handler()
        else:
            print("   Opção inválida.")


# ---------------------------------------------------------------------------
# [4] Simulations
# ---------------------------------------------------------------------------


def _handle_fail_module(network: ColonyNetwork) -> None:
    display_module_list(network)
    module_id = _prompt_module_id(network, "   ID do módulo a simular falha: ")
    if not module_id:
        return

    module = network.modules[module_id]
    if module.status == ModuleStatus.OFFLINE:
        print(f"   {module_id} já está OFFLINE.")
        return

    module.status = ModuleStatus.OFFLINE

    active = get_active_module_ids(network)
    connected = is_network_connected(network)
    unreachable: list[str] = []
    if active and not connected:
        reachable = bfs_reachable(network, active[0])
        unreachable = [mid for mid in active if mid not in reachable]

    display_simulation_failure(network, module_id, connected, unreachable)


def _handle_restore_module(network: ColonyNetwork) -> None:
    offline = [m for m in network.modules.values() if m.status == ModuleStatus.OFFLINE]
    if not offline:
        print()
        print("   Nenhum módulo offline. Rede totalmente operacional.")
        return

    print()
    print("   Módulos offline:")
    for m in offline:
        print(f"   ○ {m.module_id} — {m.name}")

    module_id = input("   ID do módulo a restaurar: ").strip().upper()
    if module_id not in network.modules:
        print("   Módulo não encontrado.")
        return
    if network.modules[module_id].status != ModuleStatus.OFFLINE:
        print(f"   {module_id} não está offline.")
        return

    network.modules[module_id].status = ModuleStatus.OPERATIONAL
    print(f"   ✔ {module_id} restaurado. Status: OPERACIONAL.")
    print()


def _handle_check_connectivity(network: ColonyNetwork) -> None:
    connected = is_network_connected(network)
    display_connectivity_status(network, connected)


def _handle_simulations(network: ColonyNetwork) -> None:
    while True:
        display_simulations_submenu()
        choice = input("   Opção: ").strip()
        SIM_HANDLERS = {
            "1": lambda: _handle_fail_module(network),
            "2": lambda: _handle_restore_module(network),
            "3": lambda: _handle_check_connectivity(network),
        }
        if choice == "0":
            break
        handler = SIM_HANDLERS.get(choice)
        if handler:
            handler()
        else:
            print("   Opção inválida.")


# ---------------------------------------------------------------------------
# [5] Mathematical model
# ---------------------------------------------------------------------------


def _handle_energy_path_cost(network: ColonyNetwork) -> None:
    print()
    print("   Custo energético de transmissão com atenuação")
    print("   Informe a rota como IDs separados por vírgula.")
    print("   Exemplo: CTL-01,HAB-01,MED-01")
    raw = input("   Rota: ").strip().upper()
    path = [segment.strip() for segment in raw.split(",")]

    for mid in path:
        if mid not in network.modules:
            print(f"   Módulo não encontrado: {mid}")
            return

    path_edges = []
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        edge = next(
            (e for e in network.adjacency_list.get(u, []) if e.target == v),
            None,
        )
        if edge is None:
            print(f"   Sem conexão direta entre {u} e {v}.")
            return
        path_edges.append(edge)

    base_cost = sum(e.energy_cost_kw for e in path_edges)
    attenuated = energy_path_cost(path_edges)
    display_energy_path_cost(network, path, base_cost, attenuated)


def _handle_global_efficiency(network: ColonyNetwork) -> None:
    print()
    print("   Calculando eficiência global da rede...")
    ge = global_efficiency(network)
    display_global_efficiency(network, ge)


def _handle_math_model(network: ColonyNetwork) -> None:
    while True:
        display_math_submenu()
        choice = input("   Opção: ").strip()
        MATH_HANDLERS = {
            "1": lambda: _handle_energy_path_cost(network),
            "2": lambda: _handle_global_efficiency(network),
        }
        if choice == "0":
            break
        handler = MATH_HANDLERS.get(choice)
        if handler:
            handler()
        else:
            print("   Opção inválida.")


# ---------------------------------------------------------------------------
# [6] Sustainability
# ---------------------------------------------------------------------------


def _handle_sustainability(network: ColonyNetwork) -> None:
    bridges = find_bridges(network)
    density = network_density(network)
    density_status_label = density_status(density)
    ge = global_efficiency(network)
    total_energy = sum(
        m.energy_consumption_kw
        for m in network.modules.values()
        if m.status != ModuleStatus.OFFLINE
    )
    display_sustainability_report(
        network, bridges, density, density_status_label, ge, total_energy,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    network = build_aurora_colony()

    print()
    print(SEPARATOR)
    print("⭐ SIGIC — SISTEMA INTELIGENTE DE GERENCIAMENTO")
    print("   INFRAESTRUTURA DA COLÔNIA AURORA SIGER")
    print(SEPARATOR)
    print()
    print("   SIGIC inicializado. Rede da colônia mapeada.")
    print(f"   Módulos registrados: {len(network.modules)}")
    print(f"   Conexões ativas:     {edge_count(network)}")
    print()

    MAIN_MENU_HANDLERS = {
        "1": _handle_view_network,
        "2": _handle_query_module,
        "3": _handle_algorithms,
        "4": _handle_simulations,
        "5": _handle_math_model,
        "6": _handle_sustainability,
    }

    while True:
        display_main_menu()
        choice = input("   Opção: ").strip()

        if choice == "0":
            print()
            print(SEPARATOR)
            print("🖖  Vida longa e próspera.")
            print("   Missão encerrada. Aurora Siger persiste.")
            print(SEPARATOR)
            print()
            break

        handler = MAIN_MENU_HANDLERS.get(choice)
        if handler:
            handler(network)
        else:
            print("   Opção inválida. Tente novamente.")
