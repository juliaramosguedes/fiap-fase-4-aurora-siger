# Scaling Rationale — Fase 3 (6 pessoas) → Fase 4 (1.000 pessoas)

> Metodologia de escalonamento dos parâmetros energéticos da Fase 3 para a Fase 4.
> A Fase 3 é a **fonte da verdade**: todos os valores da Fase 4 são derivados de seus
> constantes físicas com expoentes de economia de escala declarados e justificados.
> Este documento é a ponte científica entre as duas fases do projeto Aurora Siger.

---

## Premissa de Continuidade

A Fase 3 (MGAB) modelou uma colônia de **6 pessoas** com 46 kW de consumo,
baseada no NASA DRA 5.0 e em medições reais (arXiv:2410.00066, Hartwick 2023).

A Fase 4 (SIGIC) expande para **1.000 pessoas** com 1.030 kW de consumo.
Todos os valores são derivados da Fase 3 — não são estimativas independentes.

---

## A Lei de Escala de Potência

Para infraestrutura compartilhada, consumo não cresce linearmente com a população.
A relação é modelada por uma **lei de potência**:

```
C_N = C_6 × (N / 6)^α

C_6 = consumo para 6 pessoas (Fase 3)
N   = nova população
α   = expoente de economia de escala
```

| Expoente α | Interpretação | Aplicação |
|---|---|---|
| 1,0 | Linear — sem economia de escala | Consumíveis por pessoa (comida, O₂, H₂O) |
| 0,7 | Sublinear moderado | Sistemas de suporte de vida (LSS) |
| 0,5 | Raiz quadrada | Infraestrutura compartilhada (hab, energia, comms) |
| 0,3 | Fortemente sublinear | Sistemas de controle e pesquisa |

**Referência:** Baumol, W. J. *Returns to Scale in Research and Development*. 1967.
**Referência:** Hartwick et al. (2023) — energy scaling for Mars mission architectures.

---

## Fator de Escala por Expoente

Para N = 1.000 e base = 6:

```
Razão = 1000 / 6 = 166,67

α = 0,5: (166,67)^0.5 = 12,91  →  SCALE_FACTOR
α = 0,7: (166,67)^0.7 = 35,92  →  LSS_SCALE_FACTOR
```

---

## Escalonamento por Módulo

### Suporte de Vida (LSS) — expoente 0,7

**Justificativa do expoente 0,7:**
Ar e água escalam quase linearmente porque o processamento é proporcional ao
metabolismo da tripulação. Cada pessoa consome ~0,84 kg/dia de O₂ e ~2 L/dia
de água — a escala de equipamentos de purificação segue o volume de fluido, não
a área construída. O expoente 0,7 reconhece economias parciais (tanques maiores
têm melhor razão volume/superfície) mas não superdimensiona o ganho de eficiência.

```
Fase 3 (LSS): 14 kW
Fase 4 (LSS): 14 × 35,92 = 502,6 kW → arredondado para 505 kW
```

| Subsistema | Fase 3 | Fase 4 | Fator real |
|---|---|---|---|
| ATM (controle atmosférico) | ~8 kW (estimado) | 300 kW | 37,5× ≈ 35,9× |
| WAT (reciclagem de água) | ~6 kW (estimado) | 200 kW | 33,3× ≈ 35,9× |
| LSS overhead | — | 5 kW | — |
| **Total LSS** | **14 kW** | **505 kW** | **36,1×** |

**Referência:** NASA ECLSS. NTRS 20230002103.
**Referência:** NIH. *CELSS — Controlled Ecological Life Support*. 2019.

---

### Habitat (HAB) — expoente 0,5

**Justificativa do expoente 0,5:**
HVAC, iluminação e pressurização escalam com a área construída. Para uma colônia
de 1.000 pessoas, módulos habitacionais são compartilhados — corredores, áreas
comuns, cozinhas coletivas — gerando economias de escala significativas vs. unidades
individuais. Raiz quadrada é o modelo padrão para infraestrutura de construção urbana.

```
Fase 3 (HAB): 7 kW
Fase 4 (HAB): 7 × 12,91 = 90,4 kW → SIMULATED em 85 kW (−6%)
```

---

### Energia (PWR) — expoente 0,5

```
Fase 3 (PWR): 4 kW
Fase 4 (PWR): 4 × 12,91 = 51,6 kW → SIMULATED em 27 kW
```

O valor simulado (27 kW) é menor que a previsão por escalonamento porque o overhead
de distribuição não cresce proporcionalmente à geração — a rede elétrica de uma
colônia maior tem maior eficiência de cabo/carga.

---

### Outros módulos — expoente 0,5 (base) ou SIMULATED

| Módulo | Fase 3 | Escala 0,5 | Fase 4 real | Diferença |
|---|---|---|---|---|
| COM | 3 kW | 38,7 kW | 45 kW | +16% |
| LOG | 3 kW | 38,7 kW | 50 kW | +29% |
| MIN | 5 kW | 64,5 kW | 93 kW | +44% |
| MED | 5 kW | 64,5 kW | 106 kW | +64% |

MED e MIN excedem a previsão 0,5 porque:
- **MED** escala mais próximo de 0,6–0,7 (especialidades médicas não são tão compartilháveis)
- **MIN** envolve operação de maquinário pesado que escala com produção, não com população

AGR e RES (exclusivos da Fase 4) são SIMULATED sem equivalente direto na Fase 3.

---

## Escalonamento da Geração de Energia

### Solar

```
Fase 3: 1 campo × 1.000 m²
Fase 4: SCALE_FACTOR = 12,91 → 12,91 × 1.000 m² = 12.910 m² total
Implementado: 3 campos × 2.900 m² = 8.700 m²

Cobertura relativa: 8.700 / 12.910 = 67% do escalonamento esperado
```

**Justificativa:** A geração solar não precisa escalar exatamente com o consumo porque
a eólica complementa. 3 campos de 2.900 m² cobrem 615 kW médios — suficiente para
cobrir 60% do consumo com margem para baterias. A escolha de 3 campos é consistente
com a estrutura do grafo (3 nós folha SOL).

### Eólica

```
Fase 3: 2 turbinas → 48 kW
Fase 4: 2 × 12,91 = 25,8 → 26 turbinas → 624 kW
```

26 turbinas armazenadas em 2 zonas (WND-01, WND-02) no grafo — cada zona representa
13 turbinas físicas. O `unit_count = 26` no nó WND reflete a contagem física real.

### Baterias

```
Fase 3: 3 bancos × 312 kWh = 936 kWh
Método Fase 3: usável ≥ consumo × noite_horas

Para Fase 4:
  1.030 kW × 12,6 h = 12.978 kWh
  Com reserva 20%: 12.978 / 0,80 = 16.222 kWh
  Bancos necessários: ⌈16.222 / 312⌉ = 52
```

O número de bancos (52) é calculado exatamente pelo mesmo método que a Fase 3
(dimensionamento para pior caso: noite calma, sem vento). A fórmula é a âncora
metodológica de continuidade entre as fases.

---

## Baseline Teórico vs. Implementado

O cálculo teórico com expoentes mistos (LSS 0,7 + outros 0,5) dá:

```
LSS:    14 × 35,92 = 502,6 kW
Outros: 32 × 12,91 = 413,1 kW
Total baseline: 915,7 kW  (TOTAL_CONSUMPTION_BASELINE_KW)
```

O grafo implementado totaliza **1.030 kW** (+12% acima do baseline) porque:
- Fase 4 adiciona módulos sem equivalente na Fase 3 (AGR, RES expandido, MED ampliado)
- Módulos como MED e MIN foram calibrados com expoentes mais altos que 0,5
- A margem de +12% é intencional: colonias permanentes têm overhead operacional maior
  que missões de curto prazo (maquinário pesado, laboratórios especializados, educação)

---

## Validação do Balanço

```
Geração total média: 1.239 kW
Consumo implementado: 1.030 kW
Margem de geração: 1,20×

Fase 3 referência:
  Geração: 120,5 kW
  Consumo: 46 kW
  Margem: 2,62×
```

A margem menor da Fase 4 (1,20× vs 2,62×) é esperada: a geração foi escalada
proporcionalmente ao consumo enquanto o LSS foi escalonado com expoente maior (0,7),
aumentando o denominador. Ampliações de campos solares ou turbinas adicionais
são a alavanca correta para aumentar a margem se necessário.

---

## Resumo das Decisões de Escalonamento

| Parâmetro | Fase 3 | Fase 4 | Expoente | Justificativa |
|---|---|---|---|---|
| Consumo LSS | 14 kW | 505 kW | 0,7 | Fluidos escalam próximo ao linear |
| Consumo outros módulos | 32 kW | ~525 kW | 0,5 – 0,7 | Infraestrutura compartilhada |
| Área solar | 1.000 m² | 8.700 m² | ~0,46 | Complementada por eólica |
| Turbinas eólicas | 2 | 26 | 0,5 | Fator exato |
| Bancos de bateria | 3 | 52 | — | Calculado por capacidade, não por fator |
| Capacidade bateria/banco | 312 kWh | 312 kWh | — | Inalterado (arXiv:2410.00066) |

---

## Referências

| Fonte | Aplicação |
|---|---|
| NASA DRA 5.0 (Drake, 2009) | Baseline Fase 3: 6 pessoas, 46 kW |
| arXiv:2410.00066 | Configuração de referência: 1.000 m², E33, 312 kWh |
| Hartwick et al., Nature Astronomy (2023) | 24 kW/turbina, top-3 sites |
| Musk, E. New Space 5(2), 2017 | 1.000 pessoas — colônia inicial Starship |
| NASA ECLSS NTRS 20230002103 | Consumo de suporte de vida para 6 pessoas |
| NASA HRP | Medicina, habitat, segurança de tripulação |
| NASA ISRU Roadmap (2023) | Consumo de mineração para colônias permanentes |
| Wheeler, R. M. Open Agriculture, 2017 | Área de agricultura por pessoa em espaço |
