# SIGIC — Engineering Guide · Aurora Siger Fase 4

> **SIGIC — Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia**
> Aurora Siger · Fase 4 · FIAP — Ciência da Computação · Julia Ramos RM568988

---

## O que é o SIGIC

O SIGIC é um sistema de gerenciamento de infraestrutura para uma colônia marciana de
1.000 habitantes. Enquanto a **Fase 3 (MGAB)** simulou o ciclo energético autônomo de
uma colônia de 6 pessoas, a **Fase 4 (SIGIC)** modela a infraestrutura física desta
colônia expandida como um **grafo ponderado**, permitindo análise de conectividade,
resiliência, rotas críticas e sustentabilidade energética.

A transição 6 → 1.000 pessoas é documentada em [`scaling-rationale.md`](scaling-rationale.md).

---

## A Colônia — 1.000 Habitantes em Marte

### Missão de referência

| Parâmetro | Valor | Fonte |
|---|---|---|
| Tripulação | 1.000 pessoas | Musk (2017) — capacidade inicial Starship |
| Localização | Top-3 sites de vento | Hartwick et al., Nature Astronomy (2023) |
| Ciclo marciano | 24,6 h/sol (12 h dia / 12,6 h noite) | NASA Mars Fact Sheet |
| Escopo energético | Solar + eólica (requisito do projeto) | — |

### Por que SpaceX Starship?

O Starship é o único veículo em desenvolvimento com capacidade de carga (~100 t/voo)
suficiente para transportar os módulos de uma colônia de 1.000 pessoas ao longo de
múltiplas janelas de transferência Terra–Marte.

**Referência:** Musk, E. (2017). *Making Humans a Multi-Planetary Species*. New Space, 5(2), 46–61.

---

## Arquitetura do Sistema

```
main.py
  ├── src/scenarios.py    ─ topologia de referência (108 nós · 137 arestas)
  ├── src/graph.py        ─ operações sobre ColonyNetwork
  ├── src/bfs.py          ─ BFS traversal e caminho mínimo por saltos
  ├── src/dfs.py          ─ DFS traversal e detecção de pontes (Tarjan)
  ├── src/dijkstra.py     ─ caminho mínimo ponderado (distância / energia / latência)
  ├── src/math_model.py   ─ eficiência global, atenuação energética, densidade
  ├── src/display.py      ─ UI Rich — navegação, algoritmos, ESG
  ├── src/models.py       ─ dataclasses: Module, Edge, ColonyNetwork
  ├── src/enums.py        ─ ModuleStatus, EdgeType, WeightType + enums Fase 3
  └── src/constants.py    ─ constantes físicas, limiares, escalonamento
```

### Estrutura do grafo

```
10 complexos raiz (top-level)
24 nós de grupo  (subsistemas multi-unidade com folhas numeradas)
 7 folhas únicas (filhas diretas de complexo, sem sub-unidades)
68 folhas numeradas (unidades físicas — XXX-01, XXX-02 ...)
──────────────────────────────────────────────────────────
108 nós totais · 137 arestas únicas
```

Os 137 edges se distribuem em:
- **22 backbone** — conexões inter-complexo
- **31 parent→child** — cada complexo aos seus subsistemas diretos
- **17 cross-complex** — fluxos operacionais entre subsistemas de complexos distintos
- **68 group→leaf** — grupo às unidades físicas individuais (geradas por `expand()`)

---

## Hierarquia de Módulos

Cada nó tem `priority` (1 = inviolável; 5 = pesquisa não-crítica):

| ID | Complexo | Prioridade | Consumo total | Subsistemas |
|---|---|---|---|---|
| CTL | Centro de Controle | P1 | 15,0 kW | standalone |
| PWR | Complexo de Energia | P1 | 27,0 kW | SOL WND BAT DST |
| LSS | Suporte de Vida | P1 | 505,0 kW | ATM WAT |
| HAB | Complexo Habitacional | P2 | 85,0 kW | QRT REC DIN EDU |
| MED | Complexo Médico | P2 | 106,0 kW | EMG SRG ICU CLN DEN PSY |
| COM | Sistema de Comunicação | P3 | 45,0 kW | INT EXT TOR |
| AGR | Complexo de Agricultura | P3 | 63,0 kW | GRH FPR |
| LOG | Complexo de Logística | P4 | 50,0 kW | TRN WRH EVA |
| MIN | Mineração ISRU | P4 | 93,0 kW | DRL REF RST |
| RES | Centro de Pesquisa | P5 | 41,0 kW | GEO AGT BIO ENV |

**Total da colônia: 1.030 kW (1,03 kW/pessoa)**

Detalhamento completo em [`modules-reference.md`](modules-reference.md).

---

## Infraestrutura Energética

### Por que solar e eólica juntas?

A complementaridade solar-eólica é a base do projeto energético marciano:
- **Solar** domina durante o dia; zero à noite
- **Eólica** opera 24 h e aumenta durante tempestades de poeira (quando o sol cai)
- **Baterias** cobrem o déficit de noites calmas (70% das noites — NASA NTRS 19790057281)

Apesar de a NASA planejar uso de energia nuclear para colônias permanentes, solar + eólica
têm base científica sólida para a localização top-3 de vento (Hartwick 2023).

### Capacidade instalada

| Fonte | Unidades físicas | Capacidade média | Cobertura |
|---|---|---|---|
| Solar (3 campos × 2.900 m²) | 3 campos | 615 kW (24 h avg) | 60% do consumo |
| Eólica (26 turbinas E33-class) | 26 turbinas | 624 kW | 61% do consumo |
| **Total geração** | — | **1.239 kW** | **1,20×** |
| Bateria (52 bancos × 312 kWh) | 52 bancos | 12.979 kWh utilizáveis | noite sem vento ✓ |

### Validação noturna

```
Pior caso (noite calma, sem vento, consumo total):
  1.030 kW × 12,6 h = 12.978 kWh

Capacidade usável das baterias:
  52 × 312 kWh × 0,80 = 12.979 kWh  ≥  12.978 kWh  ✓

Com vento noturno (60% das noites):
  (1.030 − 624) kW × 12,6 h = 5.116 kWh
  Margem: 12.979 / 5.116 = 2,54×  ✓
```

Detalhamento em [`energy-reference.md`](energy-reference.md).
Escalonamento da Fase 3 em [`scaling-rationale.md`](scaling-rationale.md).

---

## Algoritmos de Grafo

### BFS — Busca em Largura

```
Complexidade: O(V + E)   V = 108 nós · E = 137 arestas
Arquivo: src/bfs.py
```

- `bfs_traverse` — ordem de visita a partir de um módulo
- `bfs_shortest_path` — caminho mínimo por **saltos** (sem peso)
- `is_network_connected` — verifica se todos os módulos ativos são alcançáveis

### DFS — Busca em Profundidade

```
Complexidade: O(V + E)
Arquivo: src/dfs.py
```

- `dfs_traverse` — exploração em profundidade
- `find_bridges` — algoritmo de Tarjan: detecta arestas cuja remoção desconecta a rede

Uma aresta (u, v) é ponte se `low_link[v] > discovery_time[u]`.

**Referência:** Tarjan, R. E. *Depth-First Search and Linear Graph Algorithms*. SIAM, 1972.

### Dijkstra — Caminho Mínimo Ponderado

```
Complexidade: O((V + E) log V)   min-heap (heapq)
Arquivo: src/dijkstra.py
```

| Critério | Unidade | Aplicação |
|---|---|---|
| `DISTANCE` | metros | rota de menor percurso físico |
| `ENERGY` | kW | rota de menor custo energético |
| `LATENCY` | ms | rota de menor latência de comunicação |

---

## Modelos Matemáticos

### Custo Energético com Atenuação

```
P_rota = Σ_e [ P_e × (1 + α × d_e / 1000) ]

α = 0,05 kW/km  (NASA ICES-2023-311)
```

### Eficiência Global da Rede

```
GE = (1 / n(n−1)) × Σ_{i≠j} [1 / d(i,j)]

Limiar operacional: GE ≥ 0,002
```

**Referência:** Latora & Marchiori, Physical Review Letters 87(19), 2001.

### Densidade da Rede

```
δ = 2|E| / (|V| × (|V| − 1))   →   δ_atual = 0,0237  (2,37% — IDEAL)

Faixa ideal: 1,5% – 8,0%
```

---

## Relatório ESG

| Dimensão | Métrica | Limiar |
|---|---|---|
| Energia sustentável | módulos ≥ 20 kW | HIGH_CONSUMPTION_KW |
| Infraestrutura | densidade da rede | 1,5% – 8,0% |
| Sistemas críticos | status dos nós P1 | 100% operacional |
| Governança | pontes críticas | ≤ 40 |
| Eficiência | GE | ≥ 0,002 |

---

## Como Executar

```bash
cd fiap_fase_4_aurora_siger
pip install rich
python main.py
```

| Opção | Função |
|---|---|
| [1] | Navegar infraestrutura — drill-down 3 níveis |
| [2] | Algoritmos de grafo — BFS, DFS, Dijkstra |
| [3] | Simulações — falha em cascata, restauração, gestor de energia |
| [4] | Modelo matemático — atenuação, eficiência global |
| [5] | Relatório ESG |
| [0] | Encerrar missão |

---

## Consistência com a Fase 3

| Enum | Fase 3 | Fase 4 |
|---|---|---|
| `ModuleStatus.OPERATIONAL` | ✓ `"OPERACIONAL"` | ✓ |
| `ModuleStatus.SURVIVAL` | ✓ `"SOBREVIVÊNCIA"` | ✓ herdado |
| `ModuleStatus.SHUTDOWN` | ✓ `"DESLIGADO"` | ✓ (era OFFLINE) |
| `ModuleStatus.DEGRADED` | — | ✓ novo — estado intermediário |
| `SystemStatus` | ✓ | ✓ herdado |
| `AlertType` | ✓ | ✓ herdado |
| `AnomalyType` | ✓ | ✓ herdado |

---

## Referências

| Fonte | Uso |
|---|---|
| Musk, E. (2017). *Making Humans a Multi-Planetary Species*. New Space, 5(2), 46–61. | Escala de 1.000 pessoas |
| Hartwick, V. L. et al. Nature Astronomy, 2023. | 24 kW/turbina; localização |
| arXiv:2410.00066 | 1.000 m² solar, E33, 312 kWh/bateria (Fase 3 baseline) |
| NASA DRA 5.0 (Drake, 2009) | Baseline de 6 pessoas (Fase 3 — fonte da verdade) |
| NASA Mars Fact Sheet | Ciclo marciano, temperatura |
| Latora & Marchiori, PRL 87(19), 2001 | Fórmula GE |
| Tarjan, R. E. SIAM, 1972 | Algoritmo de ponte |
| NASA ICES-2023-311 | Coeficiente de atenuação α |
| NASA ECLSS NTRS 20230002103 | Operação 24 h — suporte de vida |
| NASA NTRS 19790057281 | Viking Lander: 70% noites calmas |
