"""
Terminal display layer — Rich-powered, Aurora Siger visual identity.

Palette (space-themed):
  Cosmic blue  #60a5fa — module IDs, highlights
  Stellar lilac #a78bfa — section headers, titles
  Deep violet  #7c3aed — panel borders, rules
  Aurora pink  #ec4899 — special accents, P1 critical
  Neon green   #10b981 — operational status
  Amber        #fbbf24 — degraded status
  Crimson      #ef4444 — offline / error
"""

from __future__ import annotations

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from .constants import (
    BRIDGE_REDUNDANCY_RECOMMENDATION,
    CRITICAL_PRIORITY_THRESHOLD,
    GLOBAL_EFFICIENCY_ALERT_THRESHOLD,
    HIGH_CONSUMPTION_KW,
)
from .enums import EdgeType, ModuleStatus, WeightType
from .graph import (
    edge_count,
    get_active_module_ids,
    get_children,
    get_descendants,
    get_top_level_modules,
)
from .models import ColonyNetwork

console = Console()

# ---------------------------------------------------------------------------
# Aurora palette helpers
# ---------------------------------------------------------------------------

_ID    = "#60a5fa"   # cosmic blue
_HDR   = "#a78bfa"   # stellar lilac
_BDR   = "#7c3aed"   # deep violet
_PINK  = "#ec4899"   # aurora pink
_OK    = "#10b981"   # neon green
_WARN  = "#fbbf24"   # amber
_ERR   = "#ef4444"   # crimson
_DIM   = "#64748b"   # cool slate


def _status_dot(status: ModuleStatus) -> str:
    return {
        ModuleStatus.OPERATIONAL: f"[{_OK}]●[/{_OK}]",
        ModuleStatus.DEGRADED:    f"[{_WARN}]◑[/{_WARN}]",
        ModuleStatus.SURVIVAL:    f"[{_WARN}]◐[/{_WARN}]",
        ModuleStatus.SHUTDOWN:    f"[{_ERR}]○[/{_ERR}]",
    }[status]


def _status_badge(status: ModuleStatus) -> str:
    return {
        ModuleStatus.OPERATIONAL: f"[{_OK}]● OPERACIONAL[/{_OK}]",
        ModuleStatus.DEGRADED:    f"[{_WARN}]◑ DEGRADADO[/{_WARN}]",
        ModuleStatus.SURVIVAL:    f"[{_WARN}]◐ SOBREVIVÊNCIA[/{_WARN}]",
        ModuleStatus.SHUTDOWN:    f"[{_ERR}]○ DESLIGADO[/{_ERR}]",
    }[status]


def _priority_badge(priority: int) -> str:
    return {
        1: f"[bold {_PINK}]■ P1 CRÍTICO[/bold {_PINK}]",
        2: f"[{_ERR}]■ P2 ALTO[/{_ERR}]",
        3: f"[{_WARN}]■ P3 MÉDIO[/{_WARN}]",
        4: f"[{_ID}]■ P4 BAIXO[/{_ID}]",
        5: f"[{_DIM}]■ P5 PESQUISA[/{_DIM}]",
    }.get(priority, f"P{priority}")


def _edge_type_label(edge_type: EdgeType) -> str:
    return {
        EdgeType.PRESSURIZED_TUNNEL: "Túnel Pressurizado",
        EdgeType.SURFACE_PATH:       "Caminho de Superfície",
        EdgeType.WIRELESS:           "Sem Fio",
    }[edge_type]


def _weight_unit(weight_type: WeightType) -> str:
    return {
        WeightType.DISTANCE: "m",
        WeightType.ENERGY:   "kW",
        WeightType.LATENCY:  "ms",
    }[weight_type]


# ---------------------------------------------------------------------------
# Welcome and main menu
# ---------------------------------------------------------------------------


def display_welcome(network: ColonyNetwork) -> None:
    active = len(get_active_module_ids(network))
    total  = len(network.modules)
    top    = len(get_top_level_modules(network))
    conns  = edge_count(network)

    console.print()
    console.print(Panel(
        f"[bold {_HDR}]⭐  SIGIC — Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia[/bold {_HDR}]\n"
        f"[{_DIM}]Aurora Siger · Fase 4 · FIAP — Ciência da Computação · Julia Ramos RM568988[/{_DIM}]\n\n"
        f"  [{_OK}]●[/{_OK}] Rede inicializada  ·  "
        f"[bold]{total}[/bold] módulos [{_DIM}]({top} complexos)[/{_DIM}]  ·  "
        f"[bold]{conns}[/bold] conexões  ·  "
        f"[bold {_OK}]{active}[/bold {_OK}] ativos",
        border_style=_BDR,
        padding=(0, 2),
    ))
    console.print()


def display_main_menu() -> None:
    console.print(Rule(
        f"[bold {_HDR}]⭐  SIGIC — Aurora Siger · Missão em curso[/bold {_HDR}]",
        style=_BDR,
    ))
    console.print()
    console.print(f"  [{_HDR}][1][/{_HDR}]  Navegar infraestrutura    [{_DIM}]— explorar complexos e módulos[/{_DIM}]")
    console.print(f"  [{_HDR}][2][/{_HDR}]  Algoritmos de grafo       [{_DIM}]— BFS, DFS, Dijkstra[/{_DIM}]")
    console.print(f"  [{_HDR}][3][/{_HDR}]  Simulações operacionais   [{_DIM}]— falha, cascata, energia[/{_DIM}]")
    console.print(f"  [{_HDR}][4][/{_HDR}]  Modelo matemático         [{_DIM}]— eficiência global, atenuação[/{_DIM}]")
    console.print(f"  [{_HDR}][5][/{_HDR}]  Relatório ESG             [{_DIM}]— sustentabilidade e governança[/{_DIM}]")
    console.print()
    console.print(f"  [{_DIM}][0]  Encerrar missão[/{_DIM}]")
    console.print()


# ---------------------------------------------------------------------------
# Drill-down navigation
# ---------------------------------------------------------------------------


def display_root_view(network: ColonyNetwork) -> None:
    """Root view: all top-level complexes."""
    table = Table(
        title=f"[bold {_HDR}]Aurora Siger — Infraestrutura da Colônia[/bold {_HDR}]  "
              f"[{_DIM}]1.000 habitantes · Marte[/{_DIM}]",
        box=box.ROUNDED,
        border_style=_BDR,
        header_style=f"bold {_HDR}",
        title_style="",
        show_lines=False,
        padding=(0, 1),
    )
    table.add_column("ID",          style=f"bold {_ID}", width=6)
    table.add_column("Complexo",    min_width=36)
    table.add_column("Prioridade",  justify="center", width=15)
    table.add_column("Status",      justify="center", width=16)
    table.add_column("Sub-módulos", justify="center", width=13)
    table.add_column("Energia",     justify="right",  width=11)

    for mid in get_top_level_modules(network):
        module   = network.modules[mid]
        children = get_children(network, mid)
        child_str = f"{len(children)} módulos" if children else f"[{_DIM}]— standalone[/{_DIM}]"
        table.add_row(
            mid,
            module.name,
            _priority_badge(module.priority),
            _status_badge(module.status),
            child_str,
            f"{module.energy_consumption_kw:.1f} kW",
        )

    console.print()
    console.print(table)
    console.print()
    console.print(f"  [{_DIM}]Digite o ID de um complexo para entrar · [0] voltar ao menu[/{_DIM}]")
    console.print()


def display_complex_view(network: ColonyNetwork, complex_id: str) -> None:
    """Complex drill-down: parent + direct children (groups shown with unit count)."""
    module       = network.modules[complex_id]
    children_ids = get_children(network, complex_id)

    header = (
        f"[bold {_ID}]{complex_id}[/bold {_ID}] — {module.name}  "
        f"{_priority_badge(module.priority)}  {_status_badge(module.status)}  "
        f"[{_DIM}]{module.energy_consumption_kw:.1f} kW[/{_DIM}]"
    )

    tree = Tree(header)
    for cid in children_ids:
        child        = network.modules[cid]
        grandchildren = get_children(network, cid)
        if grandchildren:
            # group node — show unit count + leaf IDs as hint
            leaf_ids  = "  ".join(f"[{_DIM}]{gid}[/{_DIM}]" for gid in grandchildren)
            unit_badge = f" [bold {_PINK}]×{child.unit_count}[/bold {_PINK}]"
            child_label = (
                f"[{_ID}]{cid}[/{_ID}]{unit_badge}  {child.name}  "
                f"{_status_dot(child.status)}  [{_DIM}]{child.energy_consumption_kw:.1f} kW[/{_DIM}]\n"
                f"    [{_DIM}]↳ {leaf_ids}[/{_DIM}]"
            )
        else:
            # unique leaf — no sub-units
            child_label = (
                f"[{_ID}]{cid}[/{_ID}]  {child.name}  "
                f"{_status_dot(child.status)}  [{_DIM}]{child.energy_consumption_kw:.1f} kW[/{_DIM}]"
            )
        tree.add(child_label)

    neighbors     = network.adjacency_list.get(complex_id, [])
    other_ids     = [
        e.target for e in neighbors
        if network.modules[e.target].parent_id is None and e.target != complex_id
    ]
    conn_str = "  ".join(f"[{_ID}]{mid}[/{_ID}]" for mid in other_ids) or f"[{_DIM}]nenhum[/{_DIM}]"

    console.print()
    console.print(Panel(
        tree,
        subtitle=f"[{_DIM}]conexões externas: {', '.join(other_ids) if other_ids else '—'}[/{_DIM}]",
        border_style=_BDR,
        padding=(0, 1),
    ))
    console.print()
    console.print(f"  [{_DIM}]Digite ID de um sub-módulo para detalhar · \\[V] voltar · \\[0] sair[/{_DIM}]")
    console.print()


def display_group_view(network: ColonyNetwork, group_id: str) -> None:
    """Group node view: header info + list of all physical unit leaves. Terminal navigation."""
    group    = network.modules[group_id]
    leaves   = get_children(network, group_id)
    parent   = network.modules[group.parent_id] if group.parent_id else None

    header_grid = Table.grid(padding=(0, 2))
    header_grid.add_column(style=f"{_DIM}", width=20)
    header_grid.add_column()
    header_grid.add_row("Grupo",       f"[bold {_ID}]{group_id}[/bold {_ID}] — {group.name}")
    header_grid.add_row("Status",      _status_badge(group.status))
    header_grid.add_row("Prioridade",  _priority_badge(group.priority))
    if parent:
        header_grid.add_row("Complexo pai", f"[{_ID}]{group.parent_id}[/{_ID}] — {parent.name}")
    header_grid.add_row("Unidades",    f"[bold {_PINK}]{group.unit_count}[/bold {_PINK}] unidades físicas")
    header_grid.add_row("Energia grupo", f"{group.energy_consumption_kw:.2f} kW [{_DIM}](overhead)[/{_DIM}]")

    leaf_table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style=f"bold {_HDR}",
        padding=(0, 1),
        border_style=_DIM,
    )
    leaf_table.add_column("Unidade",  style=f"{_ID}",  width=9)
    leaf_table.add_column("Status",   justify="center", width=16)
    leaf_table.add_column("Energia",  justify="right",  width=10)
    leaf_table.add_column("Armazén.", justify="right",  width=10)
    leaf_table.add_column("Com.",     justify="center", width=6)

    total_leaf_kw = 0.0
    for lid in leaves:
        leaf = network.modules[lid]
        total_leaf_kw += leaf.energy_consumption_kw
        leaf_table.add_row(
            lid,
            _status_badge(leaf.status),
            f"{leaf.energy_consumption_kw:.2f} kW",
            f"{leaf.storage_capacity_m3:.0f} m³",
            str(leaf.communication_priority),
        )

    summary = Text()
    summary.append(f"\n  Total (grupo + unidades): ", style=_DIM)
    summary.append(f"{group.energy_consumption_kw + total_leaf_kw:.2f} kW", style="bold")

    console.print()
    console.print(Panel(
        Group(header_grid, Text(), leaf_table, summary),
        title=f"[bold {_HDR}]{group_id} — Unidades Físicas[/bold {_HDR}]",
        border_style=_BDR,
        padding=(1, 2),
    ))
    console.print()


def display_module_detail(network: ColonyNetwork, module_id: str) -> None:
    """Full detail panel for a single unique leaf module."""
    module = network.modules.get(module_id)
    if module is None:
        console.print(f"  [{_ERR}]Módulo '{module_id}' não registrado.[/{_ERR}]")
        return

    children = get_children(network, module_id)
    if module.parent_id:
        parent_mod  = network.modules[module.parent_id]
        # show the complex root (grandparent if parent is a group)
        gparent_str = ""
        if parent_mod.parent_id:
            gp = network.modules[parent_mod.parent_id]
            gparent_str = f" [{_DIM}](complexo: {parent_mod.parent_id} — {gp.name})[/{_DIM}]"
        parent_str = (
            f"[{_ID}]{module.parent_id}[/{_ID}] — {parent_mod.name}{gparent_str}"
        )
    elif children:
        parent_str = f"[{_DIM}]complexo raiz — {len(children)} sub-módulo(s)[/{_DIM}]"
    else:
        parent_str = f"[{_DIM}]standalone[/{_DIM}]"

    info = Table.grid(padding=(0, 2))
    info.add_column(style=_DIM, width=24)
    info.add_column()
    info.add_row("Módulo",              f"[bold {_ID}]{module.module_id}[/bold {_ID}] — {module.name}")
    info.add_row("Status",              _status_badge(module.status))
    info.add_row("Prioridade",          _priority_badge(module.priority))
    info.add_row("Hierarquia",          parent_str)
    info.add_row("Consumo energético",  f"{module.energy_consumption_kw:.2f} kW")
    info.add_row("Capacidade armazén.", f"{module.storage_capacity_m3:.0f} m³")
    info.add_row("Prior. comunicação",  f"{module.communication_priority} / 5")

    neighbors = network.adjacency_list.get(module_id, [])
    if neighbors:
        conn_table = Table(box=box.SIMPLE, show_header=True,
                           header_style=_DIM, padding=(0, 1))
        conn_table.add_column("Módulo",   style=_ID,  width=9)
        conn_table.add_column("Nome",     width=32)
        conn_table.add_column("Tipo",     width=22)
        conn_table.add_column("Dist.",    justify="right", width=8)
        conn_table.add_column("Energia",  justify="right", width=9)
        conn_table.add_column("Latência", justify="right", width=10)
        for edge in sorted(neighbors, key=lambda e: e.distance_m):
            target = network.modules[edge.target]
            conn_table.add_row(
                edge.target,
                target.name,
                _edge_type_label(edge.edge_type),
                f"{edge.distance_m:.0f} m",
                f"{edge.energy_cost_kw:.1f} kW",
                f"{edge.latency_ms:.1f} ms",
            )
    else:
        conn_table = Text(f"[{_DIM}]Sem conexões registradas.[/{_DIM}]")

    console.print()
    console.print(Panel(
        Group(info, Text(), conn_table),
        title=f"[bold {_HDR}]{module_id}[/bold {_HDR}] — Detalhes do Módulo",
        border_style=_BDR,
        padding=(1, 2),
    ))
    console.print()


def display_module_index(network: ColonyNetwork) -> None:
    """Compact module index for algorithm prompts — all IDs grouped by hierarchy."""
    total = len(network.modules)
    tree  = Tree(f"[bold {_HDR}]Módulos disponíveis ({total} nós)[/bold {_HDR}]")

    for top_id in get_top_level_modules(network):
        top     = network.modules[top_id]
        top_dot = _status_dot(top.status)
        branch  = tree.add(f"{top_dot} [{_ID}]{top_id}[/{_ID}]  [{_DIM}]{top.name}[/{_DIM}]")

        for cid in get_children(network, top_id):
            child     = network.modules[cid]
            c_dot     = _status_dot(child.status)
            grandkids = get_children(network, cid)

            if grandkids:
                leaf_hint = "  ".join(f"[{_DIM}]{gid}[/{_DIM}]" for gid in grandkids)
                branch.add(
                    f"{c_dot} [{_ID}]{cid}[/{_ID}] [bold {_PINK}]×{child.unit_count}[/bold {_PINK}]"
                    f"  [{_DIM}]{child.name}  ↳ {leaf_hint}[/{_DIM}]"
                )
            else:
                branch.add(f"{c_dot} [{_ID}]{cid}[/{_ID}]  [{_DIM}]{child.name}[/{_DIM}]")

    console.print()
    console.print(Panel(tree, border_style=_BDR, padding=(0, 1)))
    console.print()


# ---------------------------------------------------------------------------
# Algorithm results
# ---------------------------------------------------------------------------


def display_bfs_result(
    network: ColonyNetwork,
    start_id: str,
    visit_order: list[str],
) -> None:
    table = Table(
        title=f"[bold {_HDR}]⭐  BFS — Exploração por Largura[/bold {_HDR}]  [{_DIM}]partindo de {start_id}[/{_DIM}]",
        box=box.ROUNDED,
        border_style=_BDR,
        header_style=f"bold {_HDR}",
        padding=(0, 1),
    )
    table.add_column("Ordem",   justify="right", width=7, style=_DIM)
    table.add_column("ID",      style=_ID,        width=9)
    table.add_column("Módulo",  min_width=34)
    table.add_column("Status",  justify="center", width=16)
    table.add_column("Pai",     style=_DIM,        width=9)

    for step, mid in enumerate(visit_order, 1):
        module = network.modules[mid]
        table.add_row(
            str(step), mid, module.name,
            _status_badge(module.status),
            module.parent_id or "—",
        )

    console.print()
    console.print(table)
    console.print(f"  [{_DIM}]Total visitado: {len(visit_order)} módulos[/{_DIM}]")
    console.print()


def display_bfs_path(
    network: ColonyNetwork,
    start_id: str,
    end_id: str,
    path: list[str] | None,
) -> None:
    console.print()
    console.print(Rule(f"[bold {_HDR}]BFS — Caminho Mínimo (saltos)[/bold {_HDR}]", style=_BDR))
    console.print()
    if not path:
        console.print(f"  [{_ERR}]Nenhuma rota disponível entre {start_id} e {end_id}.[/{_ERR}]")
    else:
        arrows = f"  [{_DIM}]→[/{_DIM}]  ".join(f"[{_ID}]{mid}[/{_ID}]" for mid in path)
        console.print(f"  {arrows}")
        console.print()
        console.print(f"  [{_DIM}]Origem:[/{_DIM}]  [{_ID}]{start_id}[/{_ID}] — {network.modules[start_id].name}")
        console.print(f"  [{_DIM}]Destino:[/{_DIM}] [{_ID}]{end_id}[/{_ID}] — {network.modules[end_id].name}")
        console.print(f"  [{_DIM}]Saltos:[/{_DIM}]  {len(path) - 1}")
    console.print()


def display_dfs_result(
    network: ColonyNetwork,
    start_id: str,
    visit_order: list[str],
    bridges: list[tuple[str, str]],
) -> None:
    table = Table(
        title=f"[bold {_HDR}]⭐  DFS — Exploração por Profundidade[/bold {_HDR}]  [{_DIM}]partindo de {start_id}[/{_DIM}]",
        box=box.ROUNDED,
        border_style=_BDR,
        header_style=f"bold {_HDR}",
        padding=(0, 1),
    )
    table.add_column("Ordem",  justify="right", width=7, style=_DIM)
    table.add_column("ID",     style=_ID,        width=9)
    table.add_column("Módulo", min_width=34)
    table.add_column("Status", justify="center", width=16)

    for step, mid in enumerate(visit_order, 1):
        module = network.modules[mid]
        table.add_row(str(step), mid, module.name, _status_badge(module.status))

    console.print()
    console.print(table)
    console.print(f"  [{_DIM}]Total visitado: {len(visit_order)} módulos[/{_DIM}]")
    console.print()

    if bridges:
        bridge_table = Table(
            title=f"[bold {_WARN}]☄️   Pontes Críticas Detectadas — {len(bridges)}[/bold {_WARN}]",
            box=box.SIMPLE_HEAD,
            header_style=_DIM,
            padding=(0, 1),
        )
        bridge_table.add_column("Módulo A", style=_ID,  width=9)
        bridge_table.add_column("Nome A",   width=32)
        bridge_table.add_column("",         width=3, justify="center")
        bridge_table.add_column("Módulo B", style=_ID,  width=9)
        bridge_table.add_column("Nome B",   width=32)

        for u, v in bridges:
            bridge_table.add_row(
                u, network.modules[u].name,
                f"[{_DIM}]↔[/{_DIM}]",
                v, network.modules[v].name,
            )
        console.print(bridge_table)
        console.print(f"  [{_DIM}]Remoção de qualquer ponte acima desconecta a rede.[/{_DIM}]")
    else:
        console.print(f"  [{_OK}]Nenhuma ponte encontrada.[/{_OK}] [{_DIM}]Rede totalmente redundante.[/{_DIM}]")

    console.print()


def display_dijkstra_result(
    network: ColonyNetwork,
    start_id: str,
    end_id: str,
    path: list[str],
    total_cost: float,
    weight_type: WeightType,
) -> None:
    unit = _weight_unit(weight_type)
    console.print()
    console.print(Rule(
        f"[bold {_HDR}]⭐  Dijkstra — Caminho Mínimo · {weight_type.value}[/bold {_HDR}]",
        style=_BDR,
    ))
    console.print()

    if not path:
        console.print(f"  [{_ERR}]Nenhuma rota disponível entre {start_id} e {end_id}.[/{_ERR}]")
        console.print()
        return

    console.print(f"  [{_DIM}]Origem:[/{_DIM}]  [{_ID}]{start_id}[/{_ID}] — {network.modules[start_id].name}")
    console.print(f"  [{_DIM}]Destino:[/{_DIM}] [{_ID}]{end_id}[/{_ID}] — {network.modules[end_id].name}")
    console.print()

    arrows = f"  [{_DIM}]→[/{_DIM}]  ".join(f"[{_ID}]{mid}[/{_ID}]" for mid in path)
    console.print(f"  {arrows}")
    console.print()
    console.print(
        f"  [bold]Custo total ({weight_type.value}):[/bold] {total_cost:.2f} {unit}  "
        f"[{_DIM}]·  {len(path) - 1} salto(s)[/{_DIM}]"
    )
    console.print()


# ---------------------------------------------------------------------------
# Simulation results
# ---------------------------------------------------------------------------


def display_simulation_failure(
    network: ColonyNetwork,
    module_id: str,
    cascade_ids: list[str],
    still_connected: bool,
    unreachable: list[str],
) -> None:
    module         = network.modules[module_id]
    affected_others = [mid for mid in cascade_ids if mid != module_id]

    lines = [f"[{_ERR}]○ {module_id}[/{_ERR}] — {module.name} → [bold {_ERR}]OFFLINE[/bold {_ERR}]"]

    if affected_others:
        lines.append(f"\n[{_WARN}]Desligamento em cascata — {len(affected_others)} sub-módulo(s):[/{_WARN}]")
        for mid in affected_others:
            lines.append(f"  [{_DIM}]○[/{_DIM}] [{_ID}]{mid}[/{_ID}] — {network.modules[mid].name}")

    if still_connected:
        lines.append(f"\n[{_OK}]✔ Rede permanece conectada.[/{_OK}] Nenhum módulo isolado.")
    else:
        lines.append(
            f"\n[bold {_ERR}]☄️  ANOMALIA: rede fragmentada. {len(unreachable)} módulo(s) isolado(s):[/bold {_ERR}]"
        )
        for mid in unreachable:
            lines.append(f"  [{_DIM}]○[/{_DIM}] [{_ID}]{mid}[/{_ID}] — {network.modules[mid].name}")

    console.print()
    console.print(Panel(
        "\n".join(lines),
        title=f"[bold {_ERR}]Simulação — Falha: {module_id}[/bold {_ERR}]",
        border_style=_ERR,
        padding=(1, 2),
    ))
    console.print()


def display_energy_manager_result(
    network: ColonyNetwork,
    budget_kw: float,
    current_kw: float,
    candidates: list[str],
) -> None:
    if not candidates:
        console.print()
        console.print(Panel(
            f"[{_OK}]✔ Consumo atual ({current_kw:.1f} kW) já está dentro do orçamento ({budget_kw:.1f} kW).[/{_OK}]\n"
            "Nenhum desligamento necessário.",
            title=f"[bold {_HDR}]Gestor de Energia de Emergência[/bold {_HDR}]",
            border_style=_OK,
            padding=(1, 2),
        ))
        console.print()
        return

    table = Table(
        title=f"[bold {_WARN}]⚡  Gestor de Energia de Emergência — Desligamentos Sugeridos[/bold {_WARN}]",
        box=box.ROUNDED,
        border_style=_BDR,
        header_style=f"bold {_HDR}",
        padding=(0, 1),
    )
    table.add_column("Complexo",  style=_ID, width=9)
    table.add_column("Nome",      min_width=34)
    table.add_column("Prioridade", justify="center", width=15)
    table.add_column("Economia",   justify="right",  width=12)

    total_savings = 0.0
    for mid in candidates:
        module = network.modules[mid]
        all_ids = [mid] + get_descendants(network, mid)
        savings = sum(
            network.modules[i].energy_consumption_kw
            for i in all_ids
            if network.modules[i].status == ModuleStatus.OPERATIONAL
        )
        total_savings += savings
        table.add_row(mid, module.name, _priority_badge(module.priority), f"{savings:.1f} kW")

    projected   = current_kw - total_savings
    proj_color  = _OK if projected <= budget_kw else _WARN

    console.print()
    console.print(table)
    console.print()
    console.print(f"  Consumo atual:   [bold]{current_kw:.1f} kW[/bold]")
    console.print(f"  Orçamento alvo:  [bold]{budget_kw:.1f} kW[/bold]")
    console.print(f"  Após sugestões:  [bold {proj_color}]{projected:.1f} kW[/bold {proj_color}]")
    console.print()
    console.print(f"  [{_DIM}]Módulos de prioridade 1 são invioláveis e nunca aparecem aqui.[/{_DIM}]")
    console.print(f"  [{_DIM}]Use 'Simular falha' para aplicar o desligamento em cascata.[/{_DIM}]")
    console.print()


def display_connectivity_status(network: ColonyNetwork, is_connected: bool) -> None:
    active = get_active_module_ids(network)
    console.print()
    if is_connected:
        console.print(Panel(
            f"[{_OK}]✔ Rede íntegra.[/{_OK}] Todos os {len(active)} módulos ativos estão interligados.",
            title=f"[bold {_HDR}]Conectividade da Rede[/bold {_HDR}]",
            border_style=_OK,
            padding=(1, 2),
        ))
    else:
        console.print(Panel(
            f"[bold {_ERR}]☄️  ANOMALIA: rede fragmentada.[/bold {_ERR}] "
            f"Módulos inacessíveis detectados entre os {len(active)} ativos.",
            title=f"[bold {_HDR}]Conectividade da Rede[/bold {_HDR}]",
            border_style=_ERR,
            padding=(1, 2),
        ))
    console.print()


# ---------------------------------------------------------------------------
# Mathematical model results
# ---------------------------------------------------------------------------


def display_energy_path_cost(
    network: ColonyNetwork,
    path: list[str],
    base_cost: float,
    attenuated_cost: float,
) -> None:
    path_str = "  →  ".join(path)
    loss     = attenuated_cost - base_cost

    grid = Table.grid(padding=(0, 2))
    grid.add_column(style=_DIM, width=30)
    grid.add_column()
    grid.add_row("Rota",                    f"[{_ID}]{path_str}[/{_ID}]")
    grid.add_row("Custo base",              f"{base_cost:.3f} kW  [{_DIM}](sem atenuação)[/{_DIM}]")
    grid.add_row("Custo com atenuação",     f"[bold]{attenuated_cost:.3f} kW[/bold]")
    grid.add_row("Perda por atenuação",     f"[{_WARN}]+{loss:.3f} kW[/{_WARN}]")
    grid.add_row("",                        "")
    grid.add_row("Modelo",                  f"[{_DIM}]P_rota = Σ P_e × (1 + α × d_e / 1000)[/{_DIM}]")
    grid.add_row("Coeficiente α",           f"[{_DIM}]0.05 kW/km  — NASA ICES-2023-311[/{_DIM}]")

    console.print()
    console.print(Panel(
        grid,
        title=f"[bold {_HDR}]📡  Modelo Matemático — Custo Energético com Atenuação[/bold {_HDR}]",
        border_style=_BDR,
        padding=(1, 2),
    ))
    console.print()


def display_global_efficiency(network: ColonyNetwork, ge: float) -> None:
    n = len(get_active_module_ids(network))
    ge_color = _OK if ge >= GLOBAL_EFFICIENCY_ALERT_THRESHOLD else _ERR
    ge_label = "operacional" if ge >= GLOBAL_EFFICIENCY_ALERT_THRESHOLD else "⚠ ABAIXO DO LIMIAR"

    grid = Table.grid(padding=(0, 2))
    grid.add_column(style=_DIM, width=28)
    grid.add_column()
    grid.add_row("Módulos ativos (n)",       str(n))
    grid.add_row("Eficiência global (GE)",   f"[{ge_color}][bold]{ge:.5f}[/bold][/{ge_color}]  [{_DIM}]({ge * 100:.2f}%)[/{_DIM}]")
    grid.add_row("Avaliação",                f"[{ge_color}]{ge_label}[/{ge_color}]")
    grid.add_row("Limiar de alerta",         f"[{_DIM}]{GLOBAL_EFFICIENCY_ALERT_THRESHOLD}[/{_DIM}]")
    grid.add_row("",                         "")
    grid.add_row("Fórmula",                  f"[{_DIM}]GE = (1/n(n-1)) × Σ_{{i≠j}} 1/d(i,j)[/{_DIM}]")
    grid.add_row("d(i,j)",                   f"[{_DIM}]menor distância em metros (Dijkstra)[/{_DIM}]")
    grid.add_row("Fonte",                    f"[{_DIM}]Latora & Marchiori, Phys. Rev. Lett. 87(19), 2001[/{_DIM}]")
    grid.add_row("",                         "")
    grid.add_row("Escala de referência",     f"[{_DIM}]< 0.003 → gargalos / módulos periféricos[/{_DIM}]")
    grid.add_row("",                         f"[{_DIM}]0.003–0.007 → rede operacional[/{_DIM}]")
    grid.add_row("",                         f"[{_DIM}]> 0.007 → alta eficiência[/{_DIM}]")

    console.print()
    console.print(Panel(
        grid,
        title=f"[bold {_HDR}]📡  Modelo Matemático — Eficiência Global da Rede[/bold {_HDR}]",
        border_style=_BDR,
        padding=(1, 2),
    ))
    console.print()


# ---------------------------------------------------------------------------
# ESG sustainability report
# ---------------------------------------------------------------------------


def display_sustainability_report(
    network: ColonyNetwork,
    bridges: list[tuple[str, str]],
    density: float,
    density_status_label: str,
    ge: float,
    total_energy_kw: float,
) -> None:
    console.print()
    console.print(Rule(
        f"[bold {_HDR}]🛰  Relatório ESG — Sustentabilidade e Governança[/bold {_HDR}]",
        style=_BDR,
    ))
    console.print(f"  [{_DIM}]Aurora Siger · Análise completa da infraestrutura da colônia.[/{_DIM}]")
    console.print()

    # 1. Energy
    console.print(Rule(f"[bold {_WARN}]⚡  1. Uso sustentável de energia[/bold {_WARN}]", style=_DIM))
    high = [m for m in network.modules.values()
            if m.energy_consumption_kw >= HIGH_CONSUMPTION_KW and m.status != ModuleStatus.SHUTDOWN]

    e_grid = Table.grid(padding=(0, 2))
    e_grid.add_column(style=_DIM, width=28)
    e_grid.add_column()
    e_grid.add_row("Consumo total da rede",    f"[bold]{total_energy_kw:.1f} kW[/bold]")
    e_grid.add_row("Módulos de alto consumo",  f"[{_WARN}]{len(high)}[/{_WARN}] (≥ {HIGH_CONSUMPTION_KW:.0f} kW)")
    console.print(e_grid)

    if high:
        console.print()
        for m in sorted(high, key=lambda x: -x.energy_consumption_kw):
            console.print(f"    [{_WARN}]⚡[/{_WARN}] [{_ID}]{m.module_id}[/{_ID}]  {m.name}:  {m.energy_consumption_kw:.1f} kW")
        console.print(f"  [{_DIM}]Recomendação: revisar eficiência operacional destes módulos.[/{_DIM}]")
    console.print()

    # 2. Network density
    console.print(Rule(f"[bold {_HDR}]🌐  2. Expansão organizada da infraestrutura[/bold {_HDR}]", style=_DIM))
    d_color = _OK if "IDEAL" in density_status_label else _WARN
    d_grid  = Table.grid(padding=(0, 2))
    d_grid.add_column(style=_DIM, width=28)
    d_grid.add_column()
    d_grid.add_row("Densidade da rede", f"[bold]{density:.4f}[/bold]  [{_DIM}]({density * 100:.1f}%)[/{_DIM}]")
    d_grid.add_row("Avaliação",         f"[{d_color}]{density_status_label}[/{d_color}]")
    d_grid.add_row("Faixa ideal",       f"[{_DIM}]1.5%–8%  (SIMULATED — colônia de 108 módulos)[/{_DIM}]")
    console.print(d_grid)
    console.print()

    # 3. Critical modules
    console.print(Rule(f"[bold {_PINK}]🛰  3. Priorização de sistemas críticos[/bold {_PINK}]", style=_DIM))
    critical    = [m for m in network.modules.values() if m.priority <= CRITICAL_PRIORITY_THRESHOLD]
    op_critical = [m for m in critical if m.status not in (ModuleStatus.SHUTDOWN, ModuleStatus.DEGRADED)]
    c_color     = _OK if len(op_critical) == len(critical) else _ERR

    c_grid = Table.grid(padding=(0, 2))
    c_grid.add_column(style=_DIM, width=28)
    c_grid.add_column()
    c_grid.add_row("Módulos P1 (invioláveis)", str(len(critical)))
    c_grid.add_row("Operacionais",             f"[{c_color}]{len(op_critical)} / {len(critical)}[/{c_color}]")
    console.print(c_grid)
    console.print()
    for m in critical:
        console.print(f"    {_status_dot(m.status)}  [{_ID}]{m.module_id}[/{_ID}]  {m.name}")
    console.print()

    # 4. Bridges
    console.print(Rule(f"[bold {_ERR}]☄️   4. Governança tecnológica — pontes críticas[/bold {_ERR}]", style=_DIM))
    b_color = _OK if len(bridges) <= BRIDGE_REDUNDANCY_RECOMMENDATION else _WARN
    console.print(
        f"  Pontes identificadas: [{b_color}][bold]{len(bridges)}[/bold][/{b_color}]  "
        f"[{_DIM}](limite recomendado: {BRIDGE_REDUNDANCY_RECOMMENDATION})[/{_DIM}]"
    )
    console.print()
    if bridges:
        for u, v in bridges:
            console.print(
                f"    [{_WARN}]⚠[/{_WARN}] [{_ID}]{u}[/{_ID}] ↔ [{_ID}]{v}[/{_ID}]  "
                f"[{_DIM}]— {network.modules[u].name} / {network.modules[v].name}[/{_DIM}]"
            )
        console.print()
        if len(bridges) > BRIDGE_REDUNDANCY_RECOMMENDATION:
            console.print(f"  [{_WARN}]Recomendação: adicionar conexões redundantes para eliminar pontes críticas.[/{_WARN}]")
        else:
            console.print(f"  [{_DIM}]Dentro do limite aceitável. Monitoramento recomendado.[/{_DIM}]")
    else:
        console.print(f"  [{_OK}]Nenhuma ponte. Rede totalmente redundante.[/{_OK}]")
    console.print()

    # 5. Global efficiency
    console.print(Rule(f"[bold {_ID}]📡  5. Redução de desperdícios — eficiência global[/bold {_ID}]", style=_DIM))
    ge_color = _OK if ge >= GLOBAL_EFFICIENCY_ALERT_THRESHOLD else _ERR
    console.print(f"  GE = [{ge_color}][bold]{ge:.5f}[/bold][/{ge_color}]  [{_DIM}]({ge * 100:.2f}%)[/{_DIM}]")
    if ge >= GLOBAL_EFFICIENCY_ALERT_THRESHOLD:
        console.print(f"  [{_OK}]Fluxo de informação e recursos em nível operacional.[/{_OK}]")
    else:
        console.print(f"  [{_ERR}]⚠ GE abaixo de {GLOBAL_EFFICIENCY_ALERT_THRESHOLD}. Revisão da topologia recomendada.[/{_ERR}]")
    console.print()

    console.print(Rule(f"[{_DIM}]Análise ESG concluída · Missão em curso[/{_DIM}]", style=_DIM))
    console.print()
