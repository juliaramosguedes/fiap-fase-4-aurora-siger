# Energy Reference — Aurora Siger SIGIC

> Geração, armazenamento e balanço energético para a colônia de 1.000 habitantes.
> Todos os valores são derivados da Fase 3 (6 pessoas) aplicando expoentes de
> economia de escala documentados em [`scaling-rationale.md`](scaling-rationale.md).
> Valores marcados como SIMULATED são estimativas com justificativa declarada.

---

## Consumo Total da Colônia

```
Consumo total nominal: 1.030 kW  (1,03 kW/pessoa)
```

**Distribuição por complexo:**

| Complexo | Consumo | % do total | Escalonamento |
|---|---|---|---|
| LSS — Suporte de Vida | 505,0 kW | 49,0% | Fase 3 × 35,92 (expoente 0,7) |
| MED — Médico | 106,0 kW | 10,3% | SIMULATED |
| MIN — Mineração ISRU | 93,0 kW | 9,0% | SIMULATED |
| HAB — Habitacional | 85,0 kW | 8,3% | Fase 3 × 12,91 (expoente 0,5) |
| PWR — Energia | 27,0 kW | 2,6% | SIMULATED |
| AGR — Agricultura | 63,0 kW | 6,1% | SIMULATED |
| COM — Comunicação | 45,0 kW | 4,4% | SIMULATED |
| LOG — Logística | 50,0 kW | 4,9% | SIMULATED |
| RES — Pesquisa | 41,0 kW | 4,0% | SIMULATED |
| CTL — Controle | 15,0 kW | 1,5% | SIMULATED |
| **Total** | **1.030,0 kW** | 100% | — |

**Âncora:** Hartwick et al. (2023) — 24–35 kW para missão de 6 pessoas.
Escalonamento metodológico em [`scaling-rationale.md`](scaling-rationale.md).

---

## Suporte de Vida — Dimensionamento Crítico

LSS é o módulo dominante (49% do consumo total) porque água e ar escalam
quase linearmente com a população — sistemas compartilhados têm ganhos
de escala limitados para fluidos.

| Subsistema | Consumo total | Unidades | Consumo/unidade |
|---|---|---|---|
| ATM — Controle Atmosférico | 300,0 kW | 3 | 90,0 kW |
| WAT — Reciclagem de Água | 200,0 kW | 3 | 60,0 kW |
| LSS — overhead | 5,0 kW | — | — |
| **LSS total** | **505,0 kW** | — | — |

**Fase 3 referência:** LSS = 14 kW para 6 pessoas.
**Fase 4 derivado:** 14 × (1000/6)^0.7 = 14 × 35,92 = 502,6 kW → arredondado para 505 kW.

**Referência:** NASA ECLSS. NTRS 20230002103. *Environmental Control and Life Support System Overview*.
**Referência:** NIH. *Controlled Ecological Life Support Systems (CELSS)*. 2019.

---

## Geração Solar

### Fórmula

```
P_solar_campo = AREA × irradiância × EFICIÊNCIA / 1000

P_solar_total = P_solar_campo × SOLAR_ARRAY_COUNT × fração_diurna
```

| Parâmetro | Valor | Fonte |
|---|---|---|
| Área por campo | 2.900 m² | SIMULATED — 1.000 m² (Fase 3) × 12,91 |
| Irradiância superfície | 500 W/m² | NASA TM-102299 (Appelbaum & Flood, 1989) |
| Eficiência células | 0,29 | SIMULATED — McMillon-Brown et al. (2020) |
| Número de campos | 3 | scenarios.py — `SOL` group (3 zonas físicas) |
| Fração diurna | 12 / 24,6 = 0,488 | NASA Mars Fact Sheet |

**Potência de pico por campo:** 2.900 × 500 × 0,29 / 1.000 = **420,5 kW**

**Potência média 24 h (todos os campos):**
420,5 kW × 0,488 × 3 campos = **615,4 kW**

**Referência:** Appelbaum, J.; Flood, D. J. *Solar Radiation on Mars*. NASA TM-102299, 1989.
**Referência:** McMillon-Brown, L. et al. *High-efficiency photovoltaic cells*. ScienceDirect, 2020.

---

## Geração Eólica

### Fórmula (E33-class adaptado para Marte)

```
P_turbina = ½ × ρ × A × v³ × η / 1000

ρ = 0,017 kg/m³  (densidade do ar marciano — arXiv:2410.00066)
A = π × (D/2)²   (área varrida pelo rotor)
η = 0,35          (eficiência conservadora — SIMULATED)
```

### Por que a E33 gera ~24 kW em Marte vs 330 kW na Terra

```
P ∝ ρ × v³

ρ_Marte / ρ_Terra = 0,017 / 1,225 = 1,4%
```

A 1,4% da densidade terrestre, a velocidade de cut-in sobe para 10,3 m/s (vs 3 m/s
na Terra). Nos top-3 sites de vento (Hartwick 2023), a média diurna é **24 kW/turbina**.

**Referência:** Hartwick, V. L. et al. Nature Astronomy, 2023. Tabela 2.
**Referência:** arXiv:2410.00066 — curva Cp para E33 adaptado a Marte.

### Capacidade instalada

| Parâmetro | Valor | Derivação |
|---|---|---|
| Turbinas físicas | 26 | Fase 3 (2) × 12,91 = 25,8 → 26 |
| Potência média por turbina | 24 kW | Hartwick et al. (2023) — top-3 sites |
| **Potência total média** | **624 kW** | 26 × 24 kW |

26 turbinas estão divididas em **2 zonas** (nós WND-01 e WND-02) no grafo —
cada zona representa 13 turbinas físicas (`unit_count = 26` no grupo WND).

**Referência:** arXiv:2410.00066 — configuração de referência Fase 3: 2 turbinas para 6 pessoas.

---

## Armazenamento — Baterias

### Dimensionamento

```
Consumo máximo (noite sem vento):
  1.030 kW × 12,6 h = 12.978 kWh

Capacidade necessária (reserva de 20%):
  12.978 / 0,80 = 16.222 kWh

Bancos necessários:
  ⌈16.222 / 312⌉ = 52 bancos
```

### Parâmetros

| Parâmetro | Valor | Fonte |
|---|---|---|
| Capacidade por banco | 312 kWh | arXiv:2410.00066 |
| Número de bancos físicos | 52 | Dimensionamento conservador (ver acima) |
| Capacidade total | 16.224 kWh | 52 × 312 |
| Reserva mínima (20%) | 3.244,8 kWh | SIMULATED — padrão Fase 3 |
| **Capacidade utilizável** | **12.979 kWh** | — |
| Exigência noite s/ vento | 12.978 kWh | 1.030 kW × 12,6 h |

Os 52 bancos estão organizados em **4 zonas** (BAT-01 a BAT-04) no grafo.
Cada zona representa 13 bancos físicos (`unit_count = 52` no grupo BAT).

**Fase 3 referência:** 3 × 312 kWh = 936 kWh para 46 kW / 6 pessoas.

---

## Balanço Energético

### Cobertura diurna

```
Geração: solar (1.262 kW peak) + eólica (624 kW)
Consumo: 1.030 kW
Excedente diurno médio: 1.239 − 1.030 = +209 kW → carrega baterias
```

### Cenários noturnos

| Cenário | Probabilidade | Geração noturna | Déficit baterias |
|---|---|---|---|
| Noite com vento | 60% | 624 kW | 5.116 kWh |
| Noite calma | 40% | 0 kW | 12.978 kWh |

Probabilidade de noite com vento derivada de Hartwick et al. (2023) — top-3 sites.
Em sites de qualidade superior, a disponibilidade de vento noturno é maior que a média
global de 30% (NASA NTRS 19790057281 — Viking Lander 2).

### Margem de geração

```
Geração média 24h: 615 (solar) + 624 (eólica) = 1.239 kW
Consumo:          1.030 kW
Margem:           1.239 / 1.030 = 1,20×

Fase 3 referência: 120,5 kW / 46 kW = 2,62×
```

A margem menor na Fase 4 é esperada: o escalonamento de infraestrutura cresce mais
rápido que o de geração porque LSS usa expoente 0,7, enquanto a geração foi escalada
proporcionalmente ao consumo a 0,5. Ampliações futuras devem priorizar campos solares
adicionais ou zonas eólicas extras.

---

## Tabela Resumo

| Constante | Valor | Tipo | Fonte |
|---|---|---|---|
| `SOLAR_ARRAY_COUNT` | 3 | SIMULATED | Fase 3 × escalonamento |
| `SOLAR_PANEL_AREA_M2` | 2.900 m² | SIMULATED | 1.000 m² × 12,91 |
| `SOLAR_PANEL_EFFICIENCY` | 0,29 | SIMULATED | McMillon-Brown et al. (2020) |
| `SOLAR_PEAK_POWER_KW` | 420,5 kW/campo | Derivado | — |
| `SOLAR_AVERAGE_POWER_KW` | 615,4 kW | Derivado | — |
| `WIND_TURBINE_COUNT` | 26 | SIMULATED | 2 × 12,91 |
| `WIND_AVERAGE_POWER_KW_PER_TURBINE` | 24 kW | Referenced | Hartwick et al. (2023) |
| `WIND_TOTAL_AVERAGE_KW` | 624 kW | Derivado | — |
| `TOTAL_GENERATION_AVERAGE_KW` | 1.239 kW | Derivado | — |
| `BATTERY_BANK_COUNT` | 52 | SIMULATED | Dimensionamento noite s/ vento |
| `BATTERY_CAPACITY_KWH` | 312 kWh/banco | Referenced | arXiv:2410.00066 |
| `BATTERY_TOTAL_CAPACITY_KWH` | 16.224 kWh | Derivado | — |
| `BATTERY_MIN_PCT` | 20% | SIMULATED | Padrão Fase 3 |
| `BATTERY_USABLE_KWH` | 12.979 kWh | Derivado | — |
| `BATTERY_NIGHT_REQUIREMENT_KWH` | 12.978 kWh | Derivado | 1.030 × 12,6 h |
