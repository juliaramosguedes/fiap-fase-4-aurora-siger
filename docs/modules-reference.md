# Modules Reference — Aurora Siger SIGIC

> Consumo, prioridade e racional operacional para os 10 complexos da colônia.
> Todos os valores de consumo são SIMULATED — derivados da Fase 3 (46 kW / 6 pessoas)
> com escalonamento documentado em [`scaling-rationale.md`](scaling-rationale.md).
> Todos os módulos operam 24 h: desligamento é energeticamente motivado, não agendado.

---

## Operação 24 h

Todos os 108 módulos operam continuamente. Não há schedule dia/noite.

**Fontes:**
- CELSS (NIH, 2019) — sistemas de suporte de vida controlados automaticamente
- NASA ECLSS (NTRS 20230002103) — automação para operação de 24 h sem manutenção contínua
- Space S&T (2021) — ISRU pode operar 24 h; decisão energética, não de tripulação

---

## Consumo Total

```
Total nominal: 1.030 kW (108 nós operacionais)
```

Fase 3 referência: 46 kW / 6 pessoas → 7,67 kW/pessoa.
Fase 4 resultado: 1.030 kW / 1.000 pessoas → **1,03 kW/pessoa**.
A redução de 7,67 → 1,03 kW/pessoa reflete economias de escala da infraestrutura compartilhada.

**Âncora:** Hartwick et al. (2023) — 24–35 kW para crew support, missão de 6 pessoas.
**Âncora:** Musk (2017) — ~1 kW/pessoa para cidades marcianas de escala.

---

## Prioridade Operacional

A ordem de prioridade segue o princípio de **sobrevivência primeiro** (NASA HRP; Zubrin 1996):

| Prioridade | Lógica |
|---|---|
| P1 — Inviolável | Desligamento causa morte imediata ou perda total de missão |
| P2 — Crítico | Infraestrutura humana essencial; degradação rápida sem operação |
| P3 — Essencial | Missão sustentável; sem risco imediato por interrupção curta |
| P4 — Operacional | Operações de suporte; buffers de 24–72 h |
| P5 — Pesquisa | Missão científica; sem impacto em sobrevivência |

**Referência:** NASA HRP. *Human Research Roadmap*. https://humanresearchroadmap.nasa.gov/
**Referência:** Zubrin, R.; Wagner, R. *The Case for Mars*. Simon & Schuster, 1996.

---

## CTL — Centro de Controle

| Atributo | Valor | Fonte |
|---|---|---|
| ID | CTL | — |
| Prioridade | 1 — inviolável | Hub central de toda a rede de infraestrutura |
| Consumo | 15,0 kW | SIMULATED |
| Tipo | Standalone (sem filhos) | — |
| Hierarquia | top-level | — |

**Justificativa:** O CTL é o nó de comandos de toda a colônia — sem ele, coordenação
de emergência, controle de módulos e comunicação inter-complexo ficam indisponíveis.
15 kW cobre servidores de controle, terminais de monitoramento 24 h e sistemas redundantes.

---

## PWR — Complexo de Energia

| Atributo | Valor | Fonte |
|---|---|---|
| ID | PWR | — |
| Prioridade | 1 — inviolável | Toda a geração e distribuição passa por este complexo |
| Consumo total | 27,0 kW | SIMULATED |

### Subsistemas

| ID | Nome | Consumo total | Unidades físicas | Tipo |
|---|---|---|---|---|
| SOL | Campo Solar Fotovoltaico | 2,0 kW | 3 campos × 2.900 m² | 3 zonas (SOL-01…03) |
| WND | Parque de Turbinas Eólicas | 2,0 kW | 26 turbinas | 2 zonas (WND-01…02) |
| BAT | Bancos de Baterias | 8,0 kW | 52 bancos × 312 kWh | 4 zonas (BAT-01…04) |
| DST | Rede de Distribuição Elétrica | 10,0 kW | 1 | folha única |

**Nota:** O consumo de SOL e WND é o overhead de gerenciamento (monitoramento, controle),
não a potência gerada. A geração é documentada em [`energy-reference.md`](energy-reference.md).
DST (10 kW) representa perdas de conversão e equipamentos de distribuição — ~1% do total gerado.

---

## LSS — Sistema de Suporte de Vida

| Atributo | Valor | Fonte |
|---|---|---|
| ID | LSS | — |
| Prioridade | 1 — inviolável | Sem LSS a tripulação não sobrevive |
| Consumo total | 505,0 kW | 14 kW (Fase 3) × 35,92 (expoente 0,7) |

### Subsistemas

| ID | Nome | Consumo total | Unidades | Consumo/unidade |
|---|---|---|---|---|
| ATM | Controle Atmosférico | 300,0 kW | 3 | 90,0 kW |
| WAT | Reciclagem de Água | 200,0 kW | 3 | 60,0 kW |

**Justificativa do expoente 0,7:** Ar e água escalam quase linearmente com a população.
Processamento de CO₂, produção de O₂ e reciclagem de água são proporcionais ao metabolismo
de 1.000 pessoas — economias de escala existem mas são limitadas.

**Fase 3:** LSS = 14 kW ("air, pressure, water recycling, thermal control").
**Referência:** NASA ECLSS. NTRS 20230002103.
**Referência:** NASA HRP. *Life Support Systems*. https://www.nasa.gov/hrp

---

## HAB — Complexo Habitacional

| Atributo | Valor | Fonte |
|---|---|---|
| ID | HAB | — |
| Prioridade | 2 — crítico | Abrigo pressurizado é pré-requisito para todas as operações |
| Consumo total | 85,0 kW | SIMULATED |

### Subsistemas

| ID | Nome | Consumo total | Unidades |
|---|---|---|---|
| QRT | Módulos Residenciais | 30,0 kW | 8 blocos habitacionais |
| REC | Hub de Recreação | 15,0 kW | 2 centros |
| DIN | Refeitório e Cozinha | 25,0 kW | 3 refeitórios |
| EDU | Centro Educacional | 10,0 kW | 1 centro |

**Justificativa:** HAB cobre HVAC, iluminação e pressurização da infraestrutura física
residencial de 1.000 pessoas. 8 blocos residenciais × ~125 pessoas/bloco cobrem a capacidade.
Recreação e educação são essenciais para saúde mental em isolamento prolongado
(NASA HRP — hazard: isolamento/confinamento).

**Referência:** NASA HRP. *Human Research Roadmap — The 5 Hazards*.
**Referência:** Hartwick et al. (2023) — habitation power included in crew estimate.

---

## MED — Complexo Médico

| Atributo | Valor | Fonte |
|---|---|---|
| ID | MED | — |
| Prioridade | 2 — crítico | Emergências médicas têm janela de tempo crítica |
| Consumo total | 106,0 kW | SIMULATED |

### Subsistemas

| ID | Nome | Consumo | Tipo |
|---|---|---|---|
| EMG | Pronto-Socorro | 20,0 kW | folha única |
| SRG | Centro Cirúrgico | 25,0 kW | 2 centros |
| ICU | UTI | 30,0 kW | folha única |
| CLN | Clínicas Gerais | 12,0 kW | 3 clínicas |
| DEN | Clínica Odontológica | 8,0 kW | 2 clínicas |
| PSY | Centro de Saúde Mental | 6,0 kW | 2 centros |

**Justificativa:** ICU (30 kW) é o módulo de maior consumo individual — ventiladores,
monitores contínuos, aquecimento. MED é expandido em relação à Fase 3 (5 kW para 6 pessoas)
para cobrir especialidades necessárias para uma comunidade autossuficiente de 1.000.

**Referência:** NASA HRP. *Human Research Roadmap — The 5 Hazards*.

---

## COM — Sistema de Comunicação

| Atributo | Valor | Fonte |
|---|---|---|
| ID | COM | — |
| Prioridade | 3 — essencial | Comunicação inter-módulo crítica; Terra-Marte essencial |
| Consumo total | 45,0 kW | SIMULATED |

### Subsistemas

| ID | Nome | Consumo total | Unidades |
|---|---|---|---|
| INT | Hub de Rede Interna | 8,0 kW | 2 hubs |
| EXT | Array de Comunicação com a Terra | 20,0 kW | 2 arrays |
| TOR | Torres de Transmissão | 12,0 kW | 3 torres |

**Referência:** NASA JPL. *Deep Space Network Telecommunications Link Design Handbook*. 2010.

---

## AGR — Complexo de Agricultura

| Atributo | Valor | Fonte |
|---|---|---|
| ID | AGR | — |
| Prioridade | 3 — essencial | Produção local de alimentos reduz dependência de resuprimento |
| Consumo total | 63,0 kW | SIMULATED |

### Subsistemas

| ID | Nome | Consumo total | Unidades |
|---|---|---|---|
| GRH | Complexo de Estufas | 40,0 kW | 5 estufas |
| FPR | Processamento de Alimentos | 18,0 kW | 2 unidades |

**Justificativa:** Módulo exclusivo da Fase 4 (sem equivalente na Fase 3 de 6 pessoas).
NASA estima ~43 m²/pessoa para produção alimentar — 43.000 m² para 1.000 pessoas.
Estufas requerem iluminação artificial suplementar (~45 W/m² em certas faixas espectrais),
aquecimento e controle atmosférico interno.

**Referência:** Wheeler, R. M. *Agriculture for Space*. Open Agriculture, 2017.

---

## LOG — Complexo de Logística

| Atributo | Valor | Fonte |
|---|---|---|
| ID | LOG | — |
| Prioridade | 4 — operacional | Suporte de superfície com buffers de 24–72 h |
| Consumo total | 50,0 kW | SIMULATED |

### Subsistemas

| ID | Nome | Consumo total | Unidades |
|---|---|---|---|
| TRN | Depósito de Veículos | 15,0 kW | 2 depósitos |
| WRH | Armazém Central | 10,0 kW | 3 armazéns |
| EVA | Câmara de Atividade Extravehicular | 20,0 kW | 2 câmaras |

**Justificativa:** EVA (20 kW) é operacionalmente crítico para manutenção externa —
câmaras de pressurização, aquecimento de trajes, recarregamento de unidades de suporte
de vida portáteis. TRN cobre carregamento de rovers e veículos de superfície.

**Referência:** SpaceX. *Starship cargo configuration for Mars*. https://www.spacex.com/vehicles/starship/

---

## MIN — Complexo de Mineração ISRU

| Atributo | Valor | Fonte |
|---|---|---|
| ID | MIN | — |
| Prioridade | 4 — operacional | Capacidade de longo prazo; reservas armazenadas protegem interrupções |
| Consumo total | 93,0 kW | SIMULATED |

### Subsistemas

| ID | Nome | Consumo total | Unidades |
|---|---|---|---|
| DRL | Operações de Perfuração | 45,0 kW | 2 perfuradoras |
| REF | Refinaria de Regolito | 35,0 kW | 2 refinarias |
| RST | Armazenamento de Recursos Minerados | 8,0 kW | 3 depósitos |

**Justificativa:** DRL é o subsistema de maior consumo do complexo — perfuração em
regolito exige torque significativo. NASA MOXIE demonstrou produção de O₂ a ~300 W
no Perseverance (2021); escala para 1.000 pessoas requer múltiplas unidades em paralelo.

**Referência:** NASA. *MOXIE*. Perseverance Rover, 2021.
**Referência:** NASA. *In-Situ Resource Utilization*. NASA ISRU Roadmap, 2023.

---

## RES — Centro de Pesquisa Científica

| Atributo | Valor | Fonte |
|---|---|---|
| ID | RES | — |
| Prioridade | 5 — pesquisa | Missão científica começa após infraestrutura estabilizada |
| Consumo total | 41,0 kW | SIMULATED |

### Subsistemas

| ID | Nome | Consumo | Tipo |
|---|---|---|---|
| GEO | Laboratório de Geologia Planetária | 8,0 kW | folha única |
| AGT | Laboratório de Pesquisa Agrícola | 10,0 kW | folha única |
| BIO | Laboratório de Biologia e Ciências | 12,0 kW | folha única |
| ENV | Monitoramento Ambiental | 6,0 kW | 2 estações |

**Justificativa:** Zubrin (1996) estabelece que ciência começa após survival
infrastructure estar ativa. RES expande o SCI-01 da Fase 3 com geologia, biologia,
pesquisa agrícola e monitoramento ambiental — capacidades essenciais para uma
comunidade científica de 1.000 pessoas.

**Referência:** Zubrin, R.; Wagner, R. *The Case for Mars*. Simon & Schuster, 1996.

---

## Tabela Resumo

| Módulo | Consumo | Prioridade | Tipo | Fase 3 equiv. |
|---|---|---|---|---|
| CTL Centro de Controle | 15,0 kW | P1 | SIMULATED | — |
| PWR Complexo de Energia | 27,0 kW | P1 | SIMULATED | PWR-01 |
| LSS Suporte de Vida | 505,0 kW | P1 | Fase3×0.7 | LSS-01 |
| HAB Complexo Habitacional | 85,0 kW | P2 | Fase3×0.5 | HAB-01 |
| MED Complexo Médico | 106,0 kW | P2 | SIMULATED | MED-01 |
| COM Sistema de Comunicação | 45,0 kW | P3 | SIMULATED | COM-01 |
| AGR Complexo de Agricultura | 63,0 kW | P3 | SIMULATED | — (novo) |
| LOG Complexo de Logística | 50,0 kW | P4 | SIMULATED | LOG-01 |
| MIN Mineração ISRU | 93,0 kW | P4 | SIMULATED | MIN-01 |
| RES Centro de Pesquisa | 41,0 kW | P5 | SIMULATED | SCI-01 |
| **Total** | **1.030,0 kW** | — | — | 46,0 kW (Fase 3) |
