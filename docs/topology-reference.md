# Topology Reference — Aurora Siger SIGIC

> Estrutura do grafo de infraestrutura da colônia: 108 nós · 137 arestas.
> Inclui definição de tipos de aresta, hierarquia de módulos, algoritmos
> aplicados e limiares de análise topológica.

---

## Visão Geral do Grafo

```
108 nós   ·  137 arestas únicas (não direcionadas)
Densidade: 0,0237  (2,37% — IDEAL para grafo de infraestrutura)
```

### Composição dos nós

| Camada | Contagem | Descrição |
|---|---|---|
| Complexos raiz | 10 | Top-level: CTL, PWR, LSS, HAB, MED, COM, AGR, LOG, MIN, RES |
| Nós de grupo | 24 | Subsistemas multi-unidade (ex: SOL, WND, ATM, QRT…) |
| Folhas únicas | 7 | Filhos diretos de complexo sem sub-unidades (ex: DST, EMG, ICU…) |
| Folhas numeradas | 68 | Unidades físicas individuais (ex: SOL-01, ATM-01, QRT-01…) |
| **Total** | **108** | — |

### Composição das arestas

| Categoria | Contagem | Descrição |
|---|---|---|
| Backbone inter-complexo | 22 | Conexões entre os 10 complexos raiz |
| Parent → child | 31 | Cada complexo aos seus subsistemas diretos |
| Cross-complex | 17 | Fluxos operacionais entre subsistemas de complexos distintos |
| Group → leaf | 68 | Grupo às unidades físicas individuais |
| **Total** | **138** | Nota: 1 aresta duplicada detectada — net 137 únicas |

---

## Hierarquia em 3 Camadas

```
Complexo raiz  (ex: LSS)
  └── Nó de grupo  (ex: ATM — "Controle Atmosférico ×3")
        └── Folha numerada  (ex: ATM-01, ATM-02, ATM-03)
  └── Folha única  (ex: sem sub-unidades — ex: DST)
```

A função `expand()` em `scenarios.py` gera automaticamente:
- 1 nó de grupo com `energy = total × 10%` (overhead de coordenação)
- N folhas com `energy = total × 90% / N` (proporcional à unidade)
- N arestas internas grupo → folha

`unit_count` no nó de grupo reflete as **unidades físicas reais**, não apenas a contagem
de folhas no grafo (ex: WND tem 2 folhas mas `unit_count = 26` turbinas físicas).

---

## Tipos de Aresta

| EdgeType | Valor | Uso | Característica |
|---|---|---|---|
| `PRESSURIZED_TUNNEL` | `"Túnel pressurizado"` | Conexões internas críticas | Proteção ambiental total; menor risco de falha |
| `SURFACE_PATH` | `"Caminho de superfície"` | Conexões externas longas | Exposição ao ambiente marciano; maior distância |
| `WIRELESS` | `"Wireless"` | Comunicações | Sem infraestrutura física; latência variável |

---

## Atributos das Arestas

Cada `Edge` tem 5 atributos numéricos:

| Atributo | Unidade | Uso |
|---|---|---|
| `distance_m` | metros | Distância física (peso Dijkstra DISTANCE) |
| `energy_cost_kw` | kW | Custo energético de manutenção (peso Dijkstra ENERGY) |
| `latency_ms` | ms | Latência de comunicação (peso Dijkstra LATENCY) |
| `edge_type` | EdgeType | Tipo de conexão |
| `source` / `target` | str | IDs dos módulos conectados |

---

## Algoritmos Aplicados

### BFS — `src/bfs.py`

**Complexidade:** O(V + E)

```python
# Implementação: fila deque, visited set
bfs_traverse(network, start_id)       → list[str]   # ordem de visita
bfs_shortest_path(network, s, t)      → list[str]   # caminho por saltos (sem peso)
bfs_reachable(network, start_id)      → set[str]    # todos os nós alcançáveis
is_network_connected(network)         → bool        # conectividade global
```

**Propriedade:** BFS garante o caminho com **menor número de saltos** entre dois nós.
Para menor distância/energia/latência, use Dijkstra.

---

### DFS — `src/dfs.py`

**Complexidade:** O(V + E)

```python
dfs_traverse(network, start_id)       → list[str]          # ordem de visita (profundidade)
find_bridges(network)                 → list[tuple[str,str]] # pontes (Tarjan)
```

**Algoritmo de Tarjan para pontes:**

```
Para cada aresta (u, v):
  se low_link[v] > discovery_time[u]:
    (u, v) é uma ponte
```

`low_link[v]` = menor discovery_time alcançável por v via arestas de retorno.
Se v não consegue "voltar" para trás de u, a remoção de (u, v) desconecta o grafo.

**Referência:** Tarjan, R. E. *Depth-First Search and Linear Graph Algorithms*. SIAM J. Comput. 1(2), 1972.

---

### Dijkstra — `src/dijkstra.py`

**Complexidade:** O((V + E) log V) com min-heap

```python
dijkstra_shortest_path(network, s, t, weight_type)  → (list[str], float)
dijkstra_all_distances(network, source, weight_type) → dict[str, float]
```

**Critérios:**

| WeightType | Campo da aresta | Pergunta respondida |
|---|---|---|
| `DISTANCE` | `distance_m` | Qual rota percorre menos metros? |
| `ENERGY` | `energy_cost_kw` | Qual rota dissipa menos energia? |
| `LATENCY` | `latency_ms` | Qual rota tem menor latência de comunicação? |

`dijkstra_all_distances` é usada pelo cálculo de Eficiência Global (GE) — executa
Dijkstra de cada nó ativo para todos os outros: O(V × (V + E) log V).

---

## Modelos Matemáticos — `src/math_model.py`

### Eficiência Global (GE)

```
GE = (1 / n(n−1)) × Σ_{i≠j} [1 / d(i,j)]

n = número de módulos ativos
d(i,j) = menor distância em metros entre i e j (Dijkstra DISTANCE)
```

GE mede quão "perto" os módulos estão em média — quanto maior GE, mais eficiente
é o fluxo de informação e recursos pela rede.

| GE | Avaliação |
|---|---|
| < 0,002 | ⚠ ABAIXO DO LIMIAR |
| 0,002 – 0,005 | ● OPERACIONAL |
| > 0,007 | ● ALTA EFICIÊNCIA |

**Referência:** Latora, V.; Marchiori, M. PRL 87(19), 2001.

---

### Custo Energético com Atenuação

```
P_rota = Σ_e [ P_e × (1 + α × d_e / 1000) ]

α = 0,05 kW/km  (ENERGY_ATTENUATION_COEFFICIENT)
```

Cada aresta contribui com `P_e` (custo base) mais perdas resistivas proporcionais
à distância em quilômetros. Arestas longas (surface path inter-complexo) acumulam
perda adicional significativa.

**Referência:** NASA ICES-2023-311 — dimensionamento de cabos para superfície marciana.

---

### Densidade da Rede

```
δ = 2|E| / (|V| × (|V| − 1))

Valor atual: 2 × 137 / (108 × 107) = 0,0237  (2,37%)
```

| Faixa | Status |
|---|---|
| < 0,015 (1,5%) | ABAIXO DO IDEAL — risco de isolamento |
| 0,015 – 0,08 (1,5–8%) | IDEAL — redundância adequada |
| > 0,08 (8%) | ACIMA DO IDEAL — sobrecarga de infraestrutura |

---

## Operações Hierárquicas — `src/graph.py`

| Função | Descrição |
|---|---|
| `get_children(network, parent_id)` | Filhos diretos |
| `get_descendants(network, root_id)` | Todos os descendentes (BFS) |
| `get_top_level_modules(network)` | Complexos raiz (sem pai) |
| `cascade_offline(network, module_id)` | Desliga módulo e todos os descendentes |
| `cascade_restore(network, module_id)` | Restaura módulo e todos os descendentes |
| `compute_shutdown_candidates(network, budget_kw)` | Gestor greedy de emergência energética |

### Gestor de Emergência — Lógica Greedy

```
1. Calcula consumo atual
2. Se atual ≤ budget → sem ação
3. Ordena complexos elegíveis: por prioridade desc, depois por energia desc
4. Seleciona para desligar até atingir budget
```

Complexos P1 são **sempre excluídos** dos candidatos (`priority > CRITICAL_PRIORITY_THRESHOLD`).

---

## Limiares de Análise Topológica

| Constante | Valor | Justificativa |
|---|---|---|
| `NETWORK_DENSITY_IDEAL_MIN` | 0,015 | Mínimo para grafo de 108 nós sem risco de isolamento |
| `NETWORK_DENSITY_IDEAL_MAX` | 0,080 | Máximo antes de sobrecarga de infraestrutura |
| `GLOBAL_EFFICIENCY_ALERT_THRESHOLD` | 0,002 | GE < 0,002 = distância efetiva > 500 m entre pares |
| `BRIDGE_REDUNDANCY_RECOMMENDATION` | 40 | Grafo hierárquico de 108 nós tem ~68 pontes estruturais esperadas; acima de 40 = preocupação |
| `HIGH_CONSUMPTION_KW` | 20,0 | ~3,5× a média por nó (615 kW / 108 nós ≈ 5,7 kW) |
| `CRITICAL_PRIORITY_THRESHOLD` | 1 | Módulos P1 — invioláveis em qualquer operação |

---

## Layout Físico da Colônia

```
Diâmetro aproximado: ~2 km
Núcleo central (CTL, LSS, PWR): 0–200 m raio
Anel interno (HAB, MED, COM): 200–400 m raio
Zonas externas (AGR, LOG, MIN): 400–1.000 m raio
Sensores remotos: até 900 m
```

Distâncias das arestas refletem este layout. As conexões backbone mais longas
(PWR → MIN: 800 m; PWR → AGR: 500 m) são do tipo `SURFACE_PATH` — exposição
ambiental justificada pela distância que inviabiliza túnel pressurizado.

---

## Consistência de Status entre Fases

| `ModuleStatus` | Valor | Fase 3 | Fase 4 |
|---|---|---|---|
| `OPERATIONAL` | `"OPERACIONAL"` | ✓ | ✓ |
| `DEGRADED` | `"DEGRADADO"` | — | ✓ novo — estado intermediário |
| `SURVIVAL` | `"SOBREVIVÊNCIA"` | ✓ | ✓ herdado |
| `SHUTDOWN` | `"DESLIGADO"` | ✓ | ✓ (era OFFLINE) |

`DEGRADED` é exclusivo da Fase 4: representa um módulo que perdeu capacidade parcial
mas ainda contribui para a rede (ex: turbina com abrasão acima do limiar, ainda gerando).
