from __future__ import annotations

from .constants import (
    BRIDGE_REDUNDANCY_RECOMMENDATION,
    CRITICAL_PRIORITY_THRESHOLD,
    GLOBAL_EFFICIENCY_ALERT_THRESHOLD,
    HIGH_CONSUMPTION_KW,
    SEPARATOR,
    SEPARATOR_THIN,
)
from .enums import ModuleStatus, WeightType
from .graph import edge_count, get_active_module_ids
from .models import ColonyNetwork, Edge

_STATUS_SYMBOL: dict[ModuleStatus, str] = {
    ModuleStatus.OPERATIONAL: "●",
    ModuleStatus.DEGRADED:    "◑",
    ModuleStatus.OFFLINE:     "○",
}

_PRIORITY_LABEL: dict[int, str] = {
    1: "CRÍTICO",
    2: "ALTO",
    3: "MÉDIO",
    4: "BAIXO",
    5: "PESQUISA",
}

_WEIGHT_UNIT: dict[WeightType, str] = {
    WeightType.DISTANCE: "m",
    WeightType.ENERGY:   "kW",
    WeightType.LATENCY:  "ms",
}


# ---------------------------------------------------------------------------
# Menus
# ---------------------------------------------------------------------------


def display_main_menu() -> None:
    print()
    print(SEPARATOR)
    print("⭐ SIGIC — GERENCIAMENTO DA INFRAESTRUTURA DA COLÔNIA")
    print("   Aurora Siger · Missão em curso")
    print(SEPARATOR)
    print()
    print("  [1] Visualizar rede da colônia")
    print("  [2] Consultar módulo")
    print("  [3] Algoritmos de grafo  (BFS · DFS · Dijkstra)")
    print("  [4] Simulações operacionais")
    print("  [5] Modelo matemático")
    print("  [6] Sustentabilidade e governança")
    print()
    print("  [0] Encerrar missão")
    print()


def display_view_submenu() -> None:
    print()
    print(SEPARATOR_THIN)
    print("  [1] Listar módulos")
    print("  [2] Listar conexões")
    print("  [3] Matriz de adjacência")
    print("  [0] Voltar")
    print()


def display_algorithms_submenu() -> None:
    print()
    print(SEPARATOR_THIN)
    print("  [1] BFS — exploração por largura")
    print("  [2] DFS — exploração por profundidade")
    print("  [3] Dijkstra — caminho mínimo ponderado")
    print("  [0] Voltar")
    print()


def display_dijkstra_weight_submenu() -> None:
    print()
    print(SEPARATOR_THIN)
    print("  [1] Distância (m)")
    print("  [2] Energia (kW)")
    print("  [3] Latência (ms)")
    print()


def display_simulations_submenu() -> None:
    print()
    print(SEPARATOR_THIN)
    print("  [1] Simular falha de módulo")
    print("  [2] Restaurar módulo")
    print("  [3] Verificar conectividade da rede")
    print("  [0] Voltar")
    print()


def display_math_submenu() -> None:
    print()
    print(SEPARATOR_THIN)
    print("  [1] Custo energético de transmissão em rota")
    print("  [2] Eficiência global da rede")
    print("  [0] Voltar")
    print()


# ---------------------------------------------------------------------------
# Network views
# ---------------------------------------------------------------------------


def display_module_list(network: ColonyNetwork) -> None:
    print()
    print(SEPARATOR)
    print("🛰  MÓDULOS DA COLÔNIA — AURORA SIGER")
    print("   Inventário completo da infraestrutura.")
    print(SEPARATOR)
    print()
    active = len(get_active_module_ids(network))
    print(f"   Total: {len(network.modules)} módulos  |  Ativos: {active}")
    print()
    print(f"   {'ID':<8} {'Nome':<32} {'Prior.':<10} {'Status':<14} {'Consumo'}")
    print(f"   {SEPARATOR_THIN}")
    for module in network.modules.values():
        symbol = _STATUS_SYMBOL[module.status]
        priority_label = _PRIORITY_LABEL.get(module.priority, str(module.priority))
        print(
            f"   {symbol} {module.module_id:<7} {module.name:<32} "
            f"{priority_label:<10} {module.status.value:<14} {module.energy_consumption_kw:.1f} kW"
        )
    print()


def display_edge_list(network: ColonyNetwork) -> None:
    print()
    print(SEPARATOR)
    print("🌐  CONEXÕES DA REDE — AURORA SIGER")
    print("   Infraestrutura de interligação entre módulos.")
    print(SEPARATOR)
    print()
    print(f"   Total de conexões: {edge_count(network)}")
    print()
    print(f"   {'Origem':<8} {'Destino':<8} {'Tipo':<26} {'Distância':>9}  {'Energia':>8}  {'Latência':>9}")
    print(f"   {SEPARATOR_THIN}")

    seen: set[frozenset] = set()
    for edges in network.adjacency_list.values():
        for edge in edges:
            pair: frozenset = frozenset([edge.source, edge.target])
            if pair in seen:
                continue
            seen.add(pair)
            print(
                f"   {edge.source:<8} {edge.target:<8} {edge.edge_type.value:<26} "
                f"{edge.distance_m:>7.0f} m  {edge.energy_cost_kw:>6.1f} kW  {edge.latency_ms:>7.1f} ms"
            )
    print()


def display_adjacency_matrix(network: ColonyNetwork) -> None:
    print()
    print(SEPARATOR)
    print("🌐  MATRIZ DE ADJACÊNCIA — AURORA SIGER")
    print("   ◆ = conexão direta   ·  = sem conexão direta")
    print(SEPARATOR)
    print()

    module_ids = list(network.modules.keys())
    abbrevs = [mid[:3] for mid in module_ids]

    header = "          " + "".join(f" {a:>3}" for a in abbrevs)
    print(f"   {header}")
    print(f"   {SEPARATOR_THIN}")

    for row_id in module_ids:
        neighbor_ids = {e.target for e in network.adjacency_list.get(row_id, [])}
        cells = "".join("  ◆  " if mid in neighbor_ids else "  ·  " for mid in module_ids)
        print(f"   {row_id:<9}{cells}")

    print()


def display_module_detail(network: ColonyNetwork, module_id: str) -> None:
    module = network.modules.get(module_id)
    if module is None:
        print()
        print("   Anomalia detectada. Módulo não registrado na rede.")
        return

    print()
    print(SEPARATOR)
    print(f"🛰  MÓDULO: {module.module_id} — {module.name.upper()}")
    print("   Módulo identificado. Dados disponíveis.")
    print(SEPARATOR)
    print()
    symbol = _STATUS_SYMBOL[module.status]
    priority_label = _PRIORITY_LABEL.get(module.priority, str(module.priority))
    print(f"   Status:              {symbol} {module.status.value}")
    print(f"   Prioridade:          {priority_label} (nível {module.priority})")
    print(f"   Consumo energético:  {module.energy_consumption_kw:.1f} kW")
    print(f"   Capacidade armazen.: {module.storage_capacity_m3:.0f} m³")
    print(f"   Prior. comunicação:  {module.communication_priority} / 5")
    print()

    neighbors = network.adjacency_list.get(module_id, [])
    if neighbors:
        print(f"   Conexões diretas ({len(neighbors)}):")
        for edge in neighbors:
            target = network.modules[edge.target]
            target_symbol = _STATUS_SYMBOL[target.status]
            print(
                f"     {target_symbol} {edge.target:<8} {target.name:<32} "
                f"{edge.distance_m:.0f} m  |  {edge.energy_cost_kw:.1f} kW  |  {edge.latency_ms:.1f} ms"
            )
    else:
        print("   Sem conexões registradas.")
    print()


# ---------------------------------------------------------------------------
# Algorithm results
# ---------------------------------------------------------------------------


def display_bfs_result(
    network: ColonyNetwork,
    start_id: str,
    visit_order: list[str],
) -> None:
    print()
    print(SEPARATOR)
    print("⭐  BFS — EXPLORAÇÃO POR LARGURA")
    print(f"   Partindo de {start_id}. Visitando camada por camada.")
    print(SEPARATOR)
    print()
    print(f"   Módulos visitados: {len(visit_order)}")
    print()
    for step, module_id in enumerate(visit_order, 1):
        module = network.modules[module_id]
        print(f"   [{step:>2}] {module_id:<8} {module.name}")
    print()


def display_bfs_path(
    network: ColonyNetwork,
    start_id: str,
    end_id: str,
    path: list[str] | None,
) -> None:
    print()
    print(SEPARATOR)
    print("⭐  BFS — CAMINHO MÍNIMO (por número de saltos)")
    print(f"   Origem: {start_id}  →  Destino: {end_id}")
    print(SEPARATOR)
    print()
    if not path:
        print("   Resistência é inútil. Nenhuma rota disponível.")
    else:
        print("   Rota calculada. Navegação autorizada.")
        print(f"   Caminho ({len(path) - 1} salto(s)):")
        print(f"   {'  →  '.join(path)}")
    print()


def display_dfs_result(
    network: ColonyNetwork,
    start_id: str,
    visit_order: list[str],
    bridges: list[tuple[str, str]],
) -> None:
    print()
    print(SEPARATOR)
    print("⭐  DFS — EXPLORAÇÃO POR PROFUNDIDADE")
    print(f"   Partindo de {start_id}. Explorando em profundidade.")
    print(SEPARATOR)
    print()
    print(f"   Módulos visitados: {len(visit_order)}")
    print()
    for step, module_id in enumerate(visit_order, 1):
        module = network.modules[module_id]
        print(f"   [{step:>2}] {module_id:<8} {module.name}")

    print()
    print(f"☄️   Conexões críticas detectadas (pontes): {len(bridges)}")
    if bridges:
        print("   Remoção de qualquer ponte abaixo desconecta a rede:")
        print()
        for u, v in bridges:
            mod_u = network.modules[u]
            mod_v = network.modules[v]
            print(f"   ⚠  {u} ({mod_u.name})  ↔  {v} ({mod_v.name})")
    else:
        print("   Nenhuma ponte encontrada. Rede totalmente redundante.")
    print()


def display_dijkstra_result(
    network: ColonyNetwork,
    start_id: str,
    end_id: str,
    path: list[str],
    total_cost: float,
    weight_type: WeightType,
) -> None:
    unit = _WEIGHT_UNIT[weight_type]
    print()
    print(SEPARATOR)
    print("⭐  DIJKSTRA — CAMINHO MÍNIMO PONDERADO")
    print(f"   Critério: {weight_type.value}")
    print(SEPARATOR)
    print()
    print(f"   Origem:  {start_id} — {network.modules[start_id].name}")
    print(f"   Destino: {end_id} — {network.modules[end_id].name}")
    print()
    if not path:
        print("   Resistência é inútil. Nenhuma rota disponível.")
    else:
        print("   Rota calculada. Navegação autorizada.")
        print()
        print(f"   Caminho ({len(path) - 1} salto(s)):")
        print(f"   {'  →  '.join(path)}")
        print()
        print(f"   Custo total ({weight_type.value}): {total_cost:.2f} {unit}")
    print()


# ---------------------------------------------------------------------------
# Mathematical model results
# ---------------------------------------------------------------------------


def display_energy_path_cost(
    network: ColonyNetwork,
    path: list[str],
    base_cost: float,
    attenuated_cost: float,
) -> None:
    print()
    print(SEPARATOR)
    print("📡  MODELO MATEMÁTICO — CUSTO ENERGÉTICO COM ATENUAÇÃO")
    print("   P_rota = Σ P_e × (1 + α × d_e / 1000)  |  α = 0.05 kW/km")
    print(SEPARATOR)
    print()
    print(f"   Rota: {'  →  '.join(path)}")
    print()
    print(f"   Custo base (sem atenuação): {base_cost:.3f} kW")
    print(f"   Custo com atenuação:        {attenuated_cost:.3f} kW")
    print(f"   Perda por atenuação:        {attenuated_cost - base_cost:.3f} kW")
    print()
    print("   Variáveis do modelo:")
    print("     P_e  = custo energético base da aresta (kW)")
    print("     d_e  = distância física da aresta (m)")
    print("     α    = coeficiente de atenuação = 0.05 kW/km")
    print("            (Fonte: NASA ICES-2023-311 — cable sizing for surface systems)")
    print()
    print("   Análise qualitativa:")
    print("   Conexões mais longas dissipam mais energia por resistência elétrica")
    print("   nos cabos e pressurização dos túneis. O modelo fundamenta a escolha")
    print("   de rotas curtas e eficientes para comunicação e distribuição de energia.")
    print()


def display_global_efficiency(network: ColonyNetwork, ge: float) -> None:
    print()
    print(SEPARATOR)
    print("📡  MODELO MATEMÁTICO — EFICIÊNCIA GLOBAL DA REDE")
    print("   GE = (1 / n(n-1)) × Σ_{i≠j}  1 / d(i,j)")
    print(SEPARATOR)
    print()
    n = len(get_active_module_ids(network))
    print(f"   Módulos ativos (n): {n}")
    print(f"   Eficiência global:  {ge:.4f}  ({ge * 100:.1f}%)")
    print()
    if ge < GLOBAL_EFFICIENCY_ALERT_THRESHOLD:
        print("   ☄️  ALERTA: eficiência abaixo do limiar (0.003).")
        print("   Recomendação: adicionar conexões redundantes aos módulos isolados.")
    else:
        print("   Comunicação inter-módulos em nível operacional adequado.")
    print()
    print("   Escala de referência (distâncias em metros):")
    print("   GE ≈ 0.001–0.003  → rede com gargalos / módulos periféricos")
    print("   GE ≈ 0.003–0.007  → rede operacional para colônia compacta")
    print("   GE ≈ 0.007–0.010  → rede altamente eficiente")
    print()
    print("   Variáveis do modelo:")
    print("     n       = número de módulos ativos")
    print("     d(i,j)  = menor distância entre módulos i e j (metros, via Dijkstra)")
    print("     GE → 0  → rede completamente desconectada")
    print("     GE → máximo quando d(i,j) → mínimo para todos os pares")
    print()
    print("   Análise qualitativa:")
    print("   GE alto indica que todos os módulos se comunicam com eficiência —")
    print("   rotas curtas, sem gargalos. GE baixo sinaliza módulos periféricos")
    print("   dependentes de longas cadeias de roteamento, aumentando latência")
    print("   e consumo energético de transmissão.")
    print()
    print("   Fonte: Latora & Marchiori, Physical Review Letters 87(19), 2001.")
    print()


# ---------------------------------------------------------------------------
# Simulation results
# ---------------------------------------------------------------------------


def display_simulation_failure(
    network: ColonyNetwork,
    module_id: str,
    still_connected: bool,
    unreachable: list[str],
) -> None:
    module = network.modules[module_id]
    print()
    print(SEPARATOR)
    print(f"☄️   SIMULAÇÃO — FALHA DE MÓDULO: {module_id}")
    print(f"   {module.name} marcado como OFFLINE.")
    print(SEPARATOR)
    print()
    if still_connected:
        print("   Rede permanece conectada. Nenhum módulo isolado.")
    else:
        print(f"   ANOMALIA CRÍTICA. {len(unreachable)} módulo(s) isolado(s):")
        for mid in unreachable:
            print(f"   ○ {mid} — {network.modules[mid].name}")
    print()


def display_connectivity_status(network: ColonyNetwork, is_connected: bool) -> None:
    active = get_active_module_ids(network)
    print()
    print(SEPARATOR)
    print("🌐  CONECTIVIDADE DA REDE — AURORA SIGER")
    print(f"   Módulos ativos: {len(active)}")
    print(SEPARATOR)
    print()
    if is_connected:
        print("   Rede íntegra. Todos os módulos ativos estão interligados.")
    else:
        print("   ☄️  ANOMALIA: rede fragmentada. Módulos inacessíveis detectados.")
    print()


# ---------------------------------------------------------------------------
# Sustainability report
# ---------------------------------------------------------------------------


def display_sustainability_report(
    network: ColonyNetwork,
    bridges: list[tuple[str, str]],
    density: float,
    density_status_label: str,
    ge: float,
    total_energy_kw: float,
) -> None:
    print()
    print(SEPARATOR)
    print("🌙  SUSTENTABILIDADE E GOVERNANÇA — AURORA SIGER")
    print("   Análise ESG da infraestrutura da colônia.")
    print(SEPARATOR)
    print()

    # 1. Energy
    print("⚡  1. Uso sustentável de energia")
    print(f"   Consumo total da rede: {total_energy_kw:.1f} kW")
    high_consumers = [
        m for m in network.modules.values()
        if m.energy_consumption_kw >= HIGH_CONSUMPTION_KW and m.status != ModuleStatus.OFFLINE
    ]
    if high_consumers:
        print(f"   Módulos com alto consumo (>= {HIGH_CONSUMPTION_KW:.0f} kW):")
        for m in high_consumers:
            print(f"     ⚡ {m.module_id} {m.name}: {m.energy_consumption_kw:.1f} kW")
        print("   Recomendação: revisar eficiência operacional destes módulos.")
    else:
        print("   Consumo distribuído de forma equilibrada entre os módulos.")
    print()

    # 2. Expansion
    print("🌐  2. Expansão organizada da infraestrutura")
    print(f"   Densidade da rede: {density:.3f}  ({density * 100:.1f}%)")
    print(f"   Avaliação: {density_status_label}")
    print("   Faixa ideal: 25%–60% (SIMULATED — NASA infrastructure guidelines)")
    print()

    # 3. Critical modules
    print("🛰  3. Priorização de sistemas críticos")
    critical = [m for m in network.modules.values() if m.priority <= CRITICAL_PRIORITY_THRESHOLD]
    operational_critical = [m for m in critical if m.status == ModuleStatus.OPERATIONAL]
    print(f"   Módulos críticos (prioridade <= {CRITICAL_PRIORITY_THRESHOLD}): {len(critical)}")
    print(f"   Operacionais: {len(operational_critical)} / {len(critical)}")
    for m in critical:
        symbol = _STATUS_SYMBOL[m.status]
        print(f"   {symbol} {m.module_id:<8} {m.name} — prioridade {m.priority}")
    print()

    # 4. Bridges / governance
    print("☄️   4. Governança tecnológica — pontes críticas")
    print(f"   Pontes identificadas: {len(bridges)}")
    if len(bridges) > BRIDGE_REDUNDANCY_RECOMMENDATION:
        print(f"   Acima do limite recomendado ({BRIDGE_REDUNDANCY_RECOMMENDATION}).")
        print("   Recomendação: adicionar conexões redundantes para eliminar pontes.")
    elif bridges:
        print("   Dentro do limite aceitável. Monitoramento recomendado.")
    else:
        print("   Rede sem pontes. Infraestrutura totalmente redundante.")
    for u, v in bridges:
        print(f"   ⚠  {u} ↔ {v} — isolamento na falha desta conexão")
    print()

    # 5. Efficiency
    print("📡  5. Redução de desperdícios — eficiência global")
    print(f"   Eficiência global (GE): {ge:.4f}  ({ge * 100:.1f}%)")
    if ge >= GLOBAL_EFFICIENCY_ALERT_THRESHOLD:
        print(f"   Fluxo de informação e recursos em nível operacional.")
    else:
        print(f"   ☄️  GE abaixo de {GLOBAL_EFFICIENCY_ALERT_THRESHOLD}. Revisão da topologia recomendada.")
    print()
    print(SEPARATOR)
    print("   Análise ESG concluída. Sistemas nominais. Missão em curso.")
    print(SEPARATOR)
    print()
