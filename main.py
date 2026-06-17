"""
SIGIC — Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia
Aurora Siger · Fase 4 · FIAP — Ciência da Computação · Julia Ramos (RM568988)

Execução:  python main.py
Requisito: pip install rich
"""

from src.bfs import bfs_reachable, bfs_shortest_path, bfs_traverse, is_network_connected
from src.constants import CRITICAL_PRIORITY_THRESHOLD
from src.dfs import dfs_traverse, find_bridges
from src.dijkstra import dijkstra_shortest_path
from src.display import (
    console,
    display_bfs_path,
    display_bfs_result,
    display_complex_view,
    display_connectivity_status,
    display_dfs_result,
    display_dijkstra_result,
    display_energy_manager_result,
    display_energy_path_cost,
    display_global_efficiency,
    display_group_view,
    display_main_menu,
    display_module_detail,
    display_module_index,
    display_root_view,
    display_simulation_failure,
    display_sustainability_report,
    display_welcome,
)
from src.enums import ModuleStatus, WeightType
from src.graph import (
    cascade_offline,
    cascade_restore,
    compute_shutdown_candidates,
    edge_count,
    get_active_module_ids,
    get_children,
    get_top_level_modules,
)
from src.math_model import density_status, energy_path_cost, global_efficiency, network_density
from src.models import ColonyNetwork
from src.scenarios import build_aurora_colony


# ---------------------------------------------------------------------------
# Screen helpers — keep the terminal scroll-free between commands
# ---------------------------------------------------------------------------


def _clear(network: ColonyNetwork) -> None:
    """Erase the terminal and redraw the persistent SIGIC header on top."""
    console.clear()
    display_welcome(network)


def _await(
    network: ColonyNetwork,
    message: str = "\n   [#64748b][Enter para continuar][/#64748b] ",
) -> None:
    """Pause until the user acknowledges, then clear and redraw the header."""
    console.print(message, end="")
    input()
    _clear(network)


def _prompt_module_id(network: ColonyNetwork, prompt: str = "   ID do módulo: ") -> str | None:
    module_id = input(prompt).strip().upper()
    if module_id not in network.modules:
        console.print(f"  [#ef4444]'{module_id}' não registrado na rede.[/#ef4444]")
        return None
    return module_id


# ---------------------------------------------------------------------------
# [1] Navigate — 3-level drill-down
# ---------------------------------------------------------------------------


def _handle_navigate(network: ColonyNetwork) -> None:
    """
    Navigation levels:
      0 — root: list top-level complexes
      1 — complex: list direct children (groups + unique leaves)
      2 — group view or leaf detail (terminal, press Enter to continue)
    """
    focus: str | None = None   # current complex ID at level 1

    while True:
        _clear(network)
        if focus is None:
            display_root_view(network)
            choice = input("   Complexo (ID) ou [0] menu: ").strip().upper()

            if choice == "0":
                return
            if choice not in network.modules:
                console.print(f"  [#ef4444]'{choice}' não encontrado.[/#ef4444]")
                _await(network)
                continue
            if network.modules[choice].parent_id is not None:
                console.print("  [#64748b]Digite o ID de um complexo raiz (sem pai).[/#64748b]")
                _await(network)
                continue

            focus = choice

        else:
            display_complex_view(network, focus)
            choice = input("   ID do sub-módulo, [V] voltar ou [0] menu: ").strip().upper()

            if choice == "0":
                return
            if choice in ("V", "VOLTAR", ""):
                focus = None
                continue
            if choice not in network.modules:
                console.print(f"  [#ef4444]'{choice}' não encontrado.[/#ef4444]")
                _await(network)
                continue

            direct_children = get_children(network, focus)
            if choice not in direct_children:
                console.print(f"  [#64748b]'{choice}' não é sub-módulo direto de {focus}. Digite um dos IDs listados acima.[/#64748b]")
                _await(network)
                continue

            children = get_children(network, choice)

            _clear(network)
            if children:
                # Level 2a — group node: show units, no further navigation
                display_group_view(network, choice)
            else:
                # Level 2b — unique leaf: show module detail
                display_module_detail(network, choice)
            _await(network)


# ---------------------------------------------------------------------------
# [2] Algorithms
# ---------------------------------------------------------------------------


def _handle_bfs(network: ColonyNetwork) -> None:
    _clear(network)
    console.print("\n  [bold]BFS — Exploração por Largura[/bold]")
    display_module_index(network)
    start_id = _prompt_module_id(network, "   Módulo de partida: ")
    if not start_id:
        _await(network)
        return

    visit_order = bfs_traverse(network, start_id)
    _clear(network)
    display_bfs_result(network, start_id, visit_order)

    ans = input("\n   Calcular caminho mínimo (saltos) até outro módulo? [s/n] ").strip().lower()
    if ans == "s":
        end_id = _prompt_module_id(network, "   Módulo de destino: ")
        if end_id:
            path = bfs_shortest_path(network, start_id, end_id)
            _clear(network)
            display_bfs_path(network, start_id, end_id, path)
    _await(network)


def _handle_dfs(network: ColonyNetwork) -> None:
    _clear(network)
    console.print("\n  [bold]DFS — Exploração por Profundidade[/bold]")
    display_module_index(network)
    start_id = _prompt_module_id(network, "   Módulo de partida: ")
    if not start_id:
        _await(network)
        return

    visit_order = dfs_traverse(network, start_id)
    bridges     = find_bridges(network)
    _clear(network)
    display_dfs_result(network, start_id, visit_order, bridges)
    _await(network)


def _handle_dijkstra(network: ColonyNetwork) -> None:
    _clear(network)
    console.print("\n  [bold]Dijkstra — Caminho Mínimo Ponderado[/bold]")
    display_module_index(network)
    start_id = _prompt_module_id(network, "   Módulo de origem: ")
    if not start_id:
        _await(network)
        return
    end_id = _prompt_module_id(network, "   Módulo de destino: ")
    if not end_id:
        _await(network)
        return

    console.print()
    console.print("  Critério de peso:")
    console.print("    [1] Distância (m)")
    console.print("    [2] Energia (kW)")
    console.print("    [3] Latência (ms)")
    console.print()
    weight_choice = input("   Critério [1/2/3]: ").strip()
    weight_type = {
        "1": WeightType.DISTANCE,
        "2": WeightType.ENERGY,
        "3": WeightType.LATENCY,
    }.get(weight_choice)
    if not weight_type:
        console.print("  [#ef4444]Opção inválida.[/#ef4444]")
        _await(network)
        return

    path, total_cost = dijkstra_shortest_path(network, start_id, end_id, weight_type)
    _clear(network)
    display_dijkstra_result(network, start_id, end_id, path, total_cost, weight_type)
    _await(network)


def _handle_algorithms(network: ColonyNetwork) -> None:
    while True:
        _clear(network)
        console.print()
        console.print("  [bold]Algoritmos de Grafo[/bold]")
        console.print("    [1] BFS — exploração por largura")
        console.print("    [2] DFS — exploração por profundidade + pontes")
        console.print("    [3] Dijkstra — caminho mínimo ponderado")
        console.print("    [0] Voltar")
        console.print()
        choice = input("   Opção: ").strip()
        handler = {"1": _handle_bfs, "2": _handle_dfs, "3": _handle_dijkstra}.get(choice)
        if choice == "0":
            return
        if handler:
            handler(network)
        else:
            console.print("  [#ef4444]Opção inválida.[/#ef4444]")
            _await(network)


# ---------------------------------------------------------------------------
# [3] Simulations
# ---------------------------------------------------------------------------


def _handle_fail_module(network: ColonyNetwork) -> None:
    _clear(network)
    display_module_index(network)
    module_id = _prompt_module_id(network, "   ID do módulo a simular falha: ")
    if not module_id:
        _await(network)
        return

    module = network.modules[module_id]
    if module.status == ModuleStatus.SHUTDOWN:
        console.print(f"  [#fbbf24]{module_id} já está OFFLINE.[/#fbbf24]")
        _await(network)
        return

    if module.priority <= CRITICAL_PRIORITY_THRESHOLD:
        console.print(
            f"\n  [bold #ef4444]⚠ ATENÇÃO:[/bold #ef4444] {module_id} é prioridade 1 — inviolável.\n"
            f"  O gestor de emergência nunca desliga módulos P1.\n"
            f"  Esta é uma simulação de força-maior. Confirmar? [s/n] ",
            end="",
        )
        if input().strip().lower() != "s":
            return

    cascade_ids = cascade_offline(network, module_id)

    active = get_active_module_ids(network)
    connected = is_network_connected(network)
    unreachable: list[str] = []
    if active and not connected:
        reachable   = bfs_reachable(network, active[0])
        unreachable = [mid for mid in active if mid not in reachable]

    _clear(network)
    display_simulation_failure(network, module_id, cascade_ids, connected, unreachable)
    _await(network)


def _handle_restore_module(network: ColonyNetwork) -> None:
    _clear(network)
    offline = [m for m in network.modules.values() if m.status == ModuleStatus.SHUTDOWN]
    if not offline:
        console.print("\n  [#10b981]Nenhum módulo offline. Rede totalmente operacional.[/#10b981]")
        _await(network)
        return

    console.print()
    console.print("  [bold]Módulos offline:[/bold]")
    for m in offline:
        parent_info = f"  [#64748b](filho de {m.parent_id})[/#64748b]" if m.parent_id else ""
        console.print(f"    [#ef4444]○[/#ef4444] [#60a5fa]{m.module_id}[/#60a5fa] — {m.name}{parent_info}")
    console.print()

    module_id = input("   ID do módulo a restaurar: ").strip().upper()
    if module_id not in network.modules:
        console.print("  [#ef4444]Módulo não encontrado.[/#ef4444]")
        _await(network)
        return
    if network.modules[module_id].status != ModuleStatus.SHUTDOWN:
        console.print(f"  [#fbbf24]{module_id} não está offline.[/#fbbf24]")
        _await(network)
        return

    restored = cascade_restore(network, module_id)
    console.print(f"\n  [#10b981]✔ Restaurados: {', '.join(restored)}[/#10b981]")
    _await(network)


def _handle_check_connectivity(network: ColonyNetwork) -> None:
    _clear(network)
    connected = is_network_connected(network)
    display_connectivity_status(network, connected)
    _await(network)


def _handle_energy_manager(network: ColonyNetwork) -> None:
    _clear(network)
    active_energy = sum(
        m.energy_consumption_kw
        for m in network.modules.values()
        if m.status == ModuleStatus.OPERATIONAL
    )
    console.print(f"\n  Consumo atual: [bold]{active_energy:.1f} kW[/bold]")
    console.print("  Informe o orçamento energético disponível (kW).")
    console.print()
    try:
        budget = float(input("   Orçamento (kW): ").strip())
    except ValueError:
        console.print("  [#ef4444]Valor inválido.[/#ef4444]")
        _await(network)
        return

    candidates = compute_shutdown_candidates(network, budget)
    _clear(network)
    display_energy_manager_result(network, budget, active_energy, candidates)
    _await(network)


def _handle_simulations(network: ColonyNetwork) -> None:
    while True:
        _clear(network)
        console.print()
        console.print("  [bold]Simulações Operacionais[/bold]")
        console.print("    [1] Simular falha de módulo  [#64748b](com cascata)[/#64748b]")
        console.print("    [2] Restaurar módulo")
        console.print("    [3] Verificar conectividade")
        console.print("    [4] Gestor de energia de emergência")
        console.print("    [0] Voltar")
        console.print()
        choice = input("   Opção: ").strip()
        handler = {
            "1": _handle_fail_module,
            "2": _handle_restore_module,
            "3": _handle_check_connectivity,
            "4": _handle_energy_manager,
        }.get(choice)
        if choice == "0":
            return
        if handler:
            handler(network)
        else:
            console.print("  [#ef4444]Opção inválida.[/#ef4444]")
            _await(network)


# ---------------------------------------------------------------------------
# [4] Mathematical model
# ---------------------------------------------------------------------------


def _handle_energy_path_cost(network: ColonyNetwork) -> None:
    _clear(network)
    console.print()
    console.print("  Informe a rota como IDs separados por vírgula.")
    console.print("  [#64748b]Exemplo: CTL,HAB,MED[/#64748b]")
    console.print()
    raw  = input("   Rota: ").strip().upper()
    path = [seg.strip() for seg in raw.split(",")]

    for mid in path:
        if mid not in network.modules:
            console.print(f"  [#ef4444]Módulo não encontrado: {mid}[/#ef4444]")
            _await(network)
            return

    path_edges = []
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        edge = next((e for e in network.adjacency_list.get(u, []) if e.target == v), None)
        if edge is None:
            console.print(f"  [#ef4444]Sem conexão direta entre {u} e {v}.[/#ef4444]")
            _await(network)
            return
        path_edges.append(edge)

    base_cost  = sum(e.energy_cost_kw for e in path_edges)
    attenuated = energy_path_cost(path_edges)
    _clear(network)
    display_energy_path_cost(network, path, base_cost, attenuated)
    _await(network)


def _handle_global_efficiency(network: ColonyNetwork) -> None:
    _clear(network)
    console.print("\n  [#64748b]Calculando eficiência global (Dijkstra para todos os pares)...[/#64748b]")
    ge = global_efficiency(network)
    _clear(network)
    display_global_efficiency(network, ge)
    _await(network)


def _handle_math_model(network: ColonyNetwork) -> None:
    while True:
        _clear(network)
        console.print()
        console.print("  [bold]Modelo Matemático[/bold]")
        console.print("    [1] Custo energético de transmissão em rota")
        console.print("    [2] Eficiência global da rede (GE)")
        console.print("    [0] Voltar")
        console.print()
        choice = input("   Opção: ").strip()
        handler = {"1": _handle_energy_path_cost, "2": _handle_global_efficiency}.get(choice)
        if choice == "0":
            return
        if handler:
            handler(network)
        else:
            console.print("  [#ef4444]Opção inválida.[/#ef4444]")
            _await(network)


# ---------------------------------------------------------------------------
# [5] ESG
# ---------------------------------------------------------------------------


def _handle_sustainability(network: ColonyNetwork) -> None:
    _clear(network)
    console.print("\n  [#64748b]Calculando métricas ESG...[/#64748b]")
    bridges      = find_bridges(network)
    density      = network_density(network)
    density_label = density_status(density)
    ge           = global_efficiency(network)
    total_energy = sum(
        m.energy_consumption_kw
        for m in network.modules.values()
        if m.status != ModuleStatus.SHUTDOWN
    )
    _clear(network)
    display_sustainability_report(network, bridges, density, density_label, ge, total_energy)
    _await(network)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    network = build_aurora_colony()

    MAIN_HANDLERS = {
        "1": _handle_navigate,
        "2": _handle_algorithms,
        "3": _handle_simulations,
        "4": _handle_math_model,
        "5": _handle_sustainability,
    }

    while True:
        _clear(network)
        display_main_menu()
        choice = input("   Opção: ").strip()

        if choice == "0":
            _clear(network)
            console.print()
            console.print("  [#a78bfa]🖖  Vida longa e próspera.[/#a78bfa]")
            console.print("  [#64748b]Missão encerrada. Aurora Siger persiste.[/#64748b]")
            console.print()
            break

        handler = MAIN_HANDLERS.get(choice)
        if handler:
            handler(network)
        else:
            console.print("  [#ef4444]Opção inválida.[/#ef4444]")
            _await(network)
