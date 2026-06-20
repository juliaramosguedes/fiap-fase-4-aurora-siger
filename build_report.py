"""
Aurora Siger Fase 4 — Gerador de Relatório Técnico PDF
=======================================================
SIGIC — Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia.
Dark mode, design Aurora Siger.

Paleta:
  BG          = #0a0f1e  (fundo)
  BG_MID      = #111827  (linhas alternadas de tabela)
  BG_CARD     = #1a2540  (cabeçalho de tabela / cards)
  TITLE_WHITE = #e8edf5  (título principal)
  ORANGE      = #e8a020  (subtítulo, labels de seção)
  BLUE_RULE   = #3a6fd8  (linha separadora)
  BLUE_LINK   = #7ab0e8  (links)
  STAR_GRAY   = #9aa8c0  (citações / texto secundário)
  BODY_TEXT   = #c5d8f0  (texto corpo)
  BADGE_LABEL = #f0c040  (labels dos badges — amarelo)
  CELL_BORDER = #2a3a5c  (bordas de tabela)
  CODE_BG     = #0d1526  (fundo de bloco de código)
  CODE_FG     = #a8d8ea  (texto de código)

Uso:
  pip install reportlab
  python build_report.py

Saída:
  relatorio_sigic_aurora_siger.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import os

# ---------------------------------------------------------------------------
# PALETA
# ---------------------------------------------------------------------------
BG          = colors.HexColor("#0a0f1e")
BG_MID      = colors.HexColor("#111827")
BG_CARD     = colors.HexColor("#1a2540")
TITLE_WHITE = colors.HexColor("#e8edf5")
ORANGE      = colors.HexColor("#e8a020")
BLUE_RULE   = colors.HexColor("#3a6fd8")
BLUE_LINK   = colors.HexColor("#7ab0e8")
STAR_GRAY   = colors.HexColor("#9aa8c0")
BODY_TEXT   = colors.HexColor("#c5d8f0")
BADGE_LABEL = colors.HexColor("#f0c040")
CELL_BORDER = colors.HexColor("#2a3a5c")
CODE_BG     = colors.HexColor("#0d1526")
CODE_FG     = colors.HexColor("#a8d8ea")
RULE_DIM    = colors.HexColor("#2a3a5c")
DIM_TEXT    = colors.HexColor("#8899aa")
OK_GREEN    = colors.HexColor("#52be80")
WARN_YELLOW = colors.HexColor("#f39c12")
ALERT_RED   = colors.HexColor("#e74c3c")

PAGE_W, PAGE_H = A4
MARGIN   = 20 * mm
USABLE_W = PAGE_W - 2 * MARGIN

# ---------------------------------------------------------------------------
# ESTILOS
# ---------------------------------------------------------------------------
def make_styles():
    return dict(
        cover_fiap=ParagraphStyle("cover_fiap",
            fontName="Helvetica", fontSize=8, leading=11,
            textColor=STAR_GRAY, alignment=TA_CENTER, spaceAfter=10),
        cover_stars=ParagraphStyle("cover_stars",
            fontName="Helvetica", fontSize=12, leading=15,
            textColor=STAR_GRAY, alignment=TA_CENTER, spaceAfter=10),
        cover_title=ParagraphStyle("cover_title",
            fontName="Helvetica-Bold", fontSize=28, leading=34,
            textColor=TITLE_WHITE, alignment=TA_CENTER, spaceAfter=8),
        cover_sub=ParagraphStyle("cover_sub",
            fontName="Helvetica-Bold", fontSize=13, leading=17,
            textColor=ORANGE, alignment=TA_CENTER, spaceAfter=16),
        cover_meta=ParagraphStyle("cover_meta",
            fontName="Helvetica", fontSize=10, leading=15,
            textColor=TITLE_WHITE, alignment=TA_CENTER, spaceAfter=3),
        cover_team_label=ParagraphStyle("cover_team_label",
            fontName="Helvetica-Bold", fontSize=11, leading=15,
            textColor=ORANGE, alignment=TA_CENTER, spaceAfter=8),
        cover_github=ParagraphStyle("cover_github",
            fontName="Helvetica-Oblique", fontSize=8.5, leading=12,
            textColor=BLUE_LINK, alignment=TA_CENTER, spaceAfter=4),
        cover_quote=ParagraphStyle("cover_quote",
            fontName="Helvetica-Oblique", fontSize=8.5, leading=12,
            textColor=STAR_GRAY, alignment=TA_CENTER, spaceAfter=0),
        section=ParagraphStyle("section",
            fontName="Helvetica-Bold", fontSize=12, leading=16,
            textColor=TITLE_WHITE, spaceBefore=12, spaceAfter=4),
        subsection=ParagraphStyle("subsection",
            fontName="Helvetica-Bold", fontSize=10, leading=14,
            textColor=BODY_TEXT, spaceBefore=8, spaceAfter=3),
        body=ParagraphStyle("body",
            fontName="Helvetica", fontSize=9, leading=14,
            textColor=BODY_TEXT, spaceAfter=5, alignment=TA_JUSTIFY),
        code=ParagraphStyle("code",
            fontName="Courier", fontSize=7, leading=10,
            textColor=CODE_FG, backColor=CODE_BG,
            leftIndent=6, rightIndent=6, spaceBefore=2, spaceAfter=2),
        code_label=ParagraphStyle("code_label",
            fontName="Helvetica-Bold", fontSize=7.5, leading=10,
            textColor=ORANGE, spaceBefore=5, spaceAfter=2),
        caption=ParagraphStyle("caption",
            fontName="Helvetica-Oblique", fontSize=7, leading=10,
            textColor=DIM_TEXT, alignment=TA_CENTER, spaceAfter=5),
        ref=ParagraphStyle("ref",
            fontName="Helvetica", fontSize=8, leading=12,
            textColor=BODY_TEXT, leftIndent=10, firstLineIndent=-10, spaceAfter=3),
    )

S = make_styles()


def sp(n=6):
    return Spacer(1, n)


def blue_rule():
    return HRFlowable(width="100%", thickness=1.2, color=BLUE_RULE,
                      spaceAfter=8, spaceBefore=4)


def dim_rule():
    return HRFlowable(width="100%", thickness=0.4, color=RULE_DIM,
                      spaceAfter=5, spaceBefore=2)


def dark_table(data, col_widths, extra_styles=None):
    ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1,  0), BG_CARD),
        ("TEXTCOLOR",     (0, 0), (-1,  0), ORANGE),
        ("FONTNAME",      (0, 0), (-1,  0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1,  0), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [BG_MID, BG]),
        ("TEXTCOLOR",     (0, 1), (-1, -1), BODY_TEXT),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 7.5),
        ("GRID",          (0, 0), (-1, -1), 0.3, CELL_BORDER),
        ("LINEABOVE",     (0, 0), (-1,  0), 0.8, BLUE_RULE),
        ("LINEBELOW",     (0, 0), (-1,  0), 0.4, BLUE_RULE),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ])
    if extra_styles:
        for s in extra_styles:
            ts.add(*s)
    t = Table(data, colWidths=col_widths)
    t.setStyle(ts)
    return t


def code_block(lines):
    text = "<br/>".join(
        l.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        for l in lines)
    return Paragraph(text, S["code"])


# ---------------------------------------------------------------------------
# TEMPLATE DE PÁGINA
# ---------------------------------------------------------------------------
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    if doc.page == 1:
        canvas.setFillColor(colors.HexColor("#1a2a4a"))
        for x, y in [(50,720),(130,640),(220,760),(370,690),(460,730),
                     (510,610),(90,510),(310,550),(430,490),(160,460)]:
            canvas.circle(x, y, 1.4, fill=1, stroke=0)
        canvas.setFillColor(colors.HexColor("#ffffff"))
        for x, y in [(75,745),(190,620),(320,770),(490,660),(100,570),
                     (270,520),(410,540),(550,710),(170,490),(390,710)]:
            canvas.circle(x, y, 0.8, fill=1, stroke=0)
    else:
        canvas.setStrokeColor(BLUE_RULE)
        canvas.setLineWidth(0.6)
        canvas.line(MARGIN, PAGE_H - 14*mm, PAGE_W - MARGIN, PAGE_H - 14*mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(STAR_GRAY)
        canvas.drawString(MARGIN, PAGE_H - 11*mm,
            "Missão Aurora Siger | FIAP Ciência da Computação 2026")
        canvas.setFillColor(BODY_TEXT)
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 11*mm,
                               f"p. {doc.page - 1}")
        canvas.setStrokeColor(RULE_DIM)
        canvas.setLineWidth(0.4)
        canvas.line(MARGIN, 13*mm, PAGE_W - MARGIN, 13*mm)
        canvas.setFont("Helvetica", 6.5)
        canvas.setFillColor(DIM_TEXT)
        canvas.drawCentredString(PAGE_W / 2, 9*mm,
            "Julia Ramos RM568988  │  Matheus Fuchelberguer RM569113  "
            "│  Carlos Eugenio Andrade RM570285  │  Rodrigo Gomes Dias RM569142")
    canvas.restoreState()


# ---------------------------------------------------------------------------
# CAPA
# ---------------------------------------------------------------------------
def cover_page():
    equipe = [
        ("Julia Ramos",            "RM568988", "linkedin.com/in/juliaramosguedes"),
        ("Matheus Fuchelberguer",  "RM569113", "linkedin.com/in/matheus-fuchelberguer-neves"),
        ("Carlos Eugenio Andrade", "RM570285", "linkedin.com/in/carloseugenioandrade"),
        ("Rodrigo Gomes Dias",     "RM569142", "linkedin.com/in/rodrigogmdias"),
    ]
    badges = [
        ("108 NÓS",    "CTL PWR LSS HAB\nMED COM AGR LOG MIN RES"),
        ("137 ARESTAS",     "backbone · parent-child\ncross-complex · group-leaf"),
        ("3 ALGORITMOS",    "BFS · DFS/Tarjan\nDijkstra (3 pesos)"),
        ("STATUS",          "COLÔNIA\nOPERACIONAL"),
    ]

    s = []
    s.append(sp(22))
    s.append(Paragraph(
        "FIAP | Fase 4 | Atividade Integradora | 2026  Ciência da Computação",
        S["cover_fiap"]))
    s.append(Paragraph("★ ★ ★", S["cover_stars"]))
    s.append(Paragraph("MISSÃO AURORA SIGER", S["cover_title"]))
    s.append(Paragraph(
        "Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia",
        S["cover_sub"]))
    s.append(blue_rule())
    s.append(Paragraph("FIAP | Ciência da Computação", S["cover_meta"]))
    s.append(Paragraph("Fase 4 — Atividade Integradora | 2026", S["cover_meta"]))
    s.append(sp(12))
    s.append(dim_rule())
    s.append(sp(4))
    s.append(Paragraph("Equipe de Missão", S["cover_team_label"]))
    s.append(sp(6))

    team_ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), BG_CARD),
        ("TEXTCOLOR",     (0, 0), ( 0,-1), TITLE_WHITE),
        ("TEXTCOLOR",     (1, 0), ( 1,-1), STAR_GRAY),
        ("TEXTCOLOR",     (2, 0), ( 2,-1), BLUE_LINK),
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME",      (2, 0), ( 2,-1), "Helvetica-Oblique"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("GRID",          (0, 0), (-1, -1), 0.4, CELL_BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ])
    team_table = Table(equipe, colWidths=[70*mm, 38*mm, 62*mm])
    team_table.setStyle(team_ts)
    s.append(team_table)
    s.append(sp(8))

    s.append(Paragraph(
        "github.com/juliaramosguedes/fiap-fase-4-aurora-siger →",
        S["cover_github"]))
    s.append(Paragraph(
        "youtu.be/WEZOV2iZdV4 →  Apresentação do projeto",
        S["cover_github"]))
    s.append(sp(4))
    s.append(Paragraph(
        '★ "A complexidade de um sistema não é fraqueza '
        '— é o mapa de suas possibilidades." ★',
        S["cover_quote"]))
    s.append(sp(10))

    n_badges = len(badges)
    badge_w  = USABLE_W / n_badges
    badge_ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1,  0), BG_CARD),
        ("BACKGROUND",    (0, 1), (-1,  1), BG_MID),
        ("TEXTCOLOR",     (0, 0), (-1,  0), BADGE_LABEL),
        ("TEXTCOLOR",     (0, 1), (-1,  1), BODY_TEXT),
        ("FONTNAME",      (0, 0), (-1,  0), "Helvetica-Bold"),
        ("FONTNAME",      (0, 1), (-1,  1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("GRID",          (0, 0), (-1, -1), 0.3, CELL_BORDER),
        ("LINEABOVE",     (0, 0), (-1,  0), 0.8, BLUE_RULE),
        ("LINEBELOW",     (0, 1), (-1,  1), 0.8, BLUE_RULE),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])
    badge_data = [
        [b[0] for b in badges],
        [b[1] for b in badges],
    ]
    badge_table = Table(badge_data, colWidths=[badge_w] * n_badges)
    badge_table.setStyle(badge_ts)
    s.append(badge_table)
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def section_header(numero, titulo):
    return [Paragraph(f"{numero} {titulo}", S["section"]), dim_rule()]


def subsection_header(titulo):
    return [Paragraph(titulo, S["subsection"])]


def body_text(texto):
    return Paragraph(texto, S["body"])


def caption_text(texto):
    return Paragraph(texto, S["caption"])


def references_footer():
    return [
        sp(10),
        HRFlowable(width="60%", thickness=0.6, color=BLUE_RULE,
                   hAlign="CENTER", spaceAfter=8, spaceBefore=4),
        Paragraph(
            '★ "A complexidade de um sistema não é fraqueza '
            '— é o mapa de suas possibilidades." ★',
            S["cover_quote"]),
    ]


def build_pdf(story, output_path):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=20*mm, bottomMargin=20*mm,
    )
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"PDF: {output_path} ({os.path.getsize(output_path):,} bytes)")


# ---------------------------------------------------------------------------
# CONTEÚDO — SIGIC Fase 4
# ---------------------------------------------------------------------------
def build_fase4():
    story = []
    story += cover_page()

    # -----------------------------------------------------------------------
    # 1. INTRODUÇÃO
    # -----------------------------------------------------------------------
    story += section_header("1", "INTRODUÇÃO — A COLÔNIA EM ESCALA INDUSTRIAL")
    story.append(body_text(
        "A Aurora Siger completou sua expansão crítica. A colônia que começou "
        "com 6 pessoas e 46 kW na Fase 3 (MGAB) opera agora com 1.000 habitantes distribuídos "
        "em 10 complexos interconectados, consumindo 1.030 kW em operação contínua. "
        "O desafio deixou de ser sobrevivência energética — passou a ser "
        "gestão de complexidade de infraestrutura."
    ))
    story.append(body_text(
        "O SIGIC (Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia) modela "
        "esta infraestrutura como um grafo ponderado não-direcionado de 108 nós e "
        "137 arestas. Grafo é o modelo natural para redes de infraestrutura: permite "
        "detectar pontes (pontos únicos de falha), calcular rotas de menor custo "
        "energético, medir eficiência global e simular cascatas de falha. Os três "
        "algoritmos clássicos de grafo — BFS, DFS/Tarjan e Dijkstra — são "
        "aplicados diretamente sobre a topologia da colônia."
    ))
    story.append(body_text(
        "O escalonamento de Fase 3 para Fase 4 segue uma lei de potência calibrada: "
        "Cₙ = C₆ × (N/6)ᵅ, com α = 0,5 para infraestrutura "
        "compartilhada e α = 0,7 para suporte de vida (LSS). Cada constante física, "
        "limiar topológico e parâmetro de escalonamento está declarado em "
        "src/constants.py — única fonte da verdade do sistema."
    ))
    story.append(sp(8))

    # -----------------------------------------------------------------------
    # 2. ARQUITETURA
    # -----------------------------------------------------------------------
    story += section_header("2", "ARQUITETURA DO SISTEMA SIGIC")
    story.append(body_text(
        "O SIGIC é estruturado em módulos com responsabilidade única e sem "
        "efeitos colaterais. Cada algoritmo recebe o grafo como parâmetro e retorna "
        "resultados sem modificar estado. A topologia é construída uma vez por "
        "build_aurora_colony() e permanece imutável durante toda a análise."
    ))
    story.append(sp(4))

    arch_data = [
        ["Módulo", "Responsabilidade"],
        ["scenarios.py", "Constrói o grafo completo: 108 nós, 137 arestas"],
        ["graph.py", "Operações hierárquicas: descendentes, cascata, emergência"],
        ["bfs.py", "BFS traversal, caminho mínimo por saltos, conectividade"],
        ["dfs.py", "DFS traversal, find_bridges (algoritmo de Tarjan)"],
        ["dijkstra.py", "Caminho mínimo ponderado: DISTANCE, ENERGY, LATENCY"],
        ["math_model.py", "Eficiência global (GE), atenuação energética, densidade"],
        ["display.py", "UI Rich — navegação, algoritmos, simulações, ESG"],
        ["constants.py", "Fonte única da verdade: limiares, física, escalonamento"],
        ["enums.py", "ModuleStatus, EdgeType, WeightType + enums Fase 3 (consistência)"],
        ["models.py", "Module, Edge, ColonyNetwork (dataclasses frozen)"],
    ]
    story.append(dark_table(arch_data,
        [45*mm, USABLE_W - 45*mm]))
    story.append(sp(6))

    story.append(body_text(
        "Princípios arquiteturais: (1) <b>funções puras</b> — sem efeitos "
        "colaterais, testáveis individualmente; (2) <b>deque O(1)</b> — "
        "get_descendants usa deque FIFO sem o antipadrão list.pop(0) O(n); "
        "(3) <b>hierarquia determinística</b> — expand() gera nó de grupo + "
        "N folhas + N arestas internas em um único call, sempre reprodutível."
    ))
    story.append(sp(8))

    # -----------------------------------------------------------------------
    # 3. TOPOLOGIA DO GRAFO
    # -----------------------------------------------------------------------
    story += section_header("3", "TOPOLOGIA DO GRAFO — 108 NÓS, 137 ARESTAS")
    story.append(body_text(
        "A colônia é um grafo não-direcionado ponderado G = (V, E) com "
        "|V| = 108 nós e |E| = 137 arestas. A estrutura é hierárquica "
        "em 3 camadas: complexo raíz → nó de grupo → folha numerada. "
        "A função expand() gera automaticamente nó de grupo, N folhas "
        "e N arestas internas a partir de um único call."
    ))
    story.append(sp(4))

    node_data = [
        ["Camada", "Contagem", "Exemplos"],
        ["Complexos raíz (top-level)", "10", "CTL, PWR, LSS, HAB, MED, COM, AGR, LOG, MIN, RES"],
        ["Nós de grupo (subsistemas multi-unidade)", "24", "SOL, WND, BAT, ATM, WAT, QRT, DRL..."],
        ["Folhas únicas (filhas diretas de complexo)", "7", "DST, EMG, ICU, EDU, GEO, AGT, BIO"],
        ["Folhas numeradas (unidades físicas)", "67", "SOL-01..03, ATM-01..03, QRT-01..08..."],
        ["<b>Total</b>", "<b>108</b>", "—"],
    ]
    story.append(dark_table(node_data, [70*mm, 28*mm, USABLE_W - 98*mm]))
    story.append(sp(6))

    edge_data = [
        ["Categoria", "Qtd.", "Descrição"],
        ["Backbone inter-complexo", "22", "Conexões entre os 10 complexos raiz"],
        ["Parent → child", "31", "Cada complexo a seus subsistemas diretos"],
        ["Cross-complex", "17", "Fluxos operacionais entre subsistemas de complexos distintos"],
        ["Group → leaf", "67", "Grupo a unidades físicas individuais (geradas por expand())"],
        ["<b>Total único</b>", "<b>137</b>", "—"],
    ]
    story.append(dark_table(edge_data, [55*mm, 18*mm, USABLE_W - 73*mm]))
    story.append(sp(6))

    story.append(Paragraph("Tipos de aresta", S["subsection"]))
    edge_type_data = [
        ["EdgeType", "Uso", "Característica"],
        ["PRESSURIZED_TUNNEL", "Conexões internas críticas", "Proteção ambiental total; menor risco"],
        ["SURFACE_PATH", "Conexões externas longas", "Exposição ao ambiente marciano"],
        ["WIRELESS", "Comunicações", "Sem infraestrutura física; latência variável"],
    ]
    story.append(dark_table(edge_type_data, [50*mm, 55*mm, USABLE_W - 105*mm]))
    story.append(sp(4))

    story.append(body_text(
        "Densidade: δ = 2|E| / (|V| × (|V|−1)) = 2×137 / (108×107) "
        "= <b>0,0237 (2,37%)</b>. Faixa ideal para grafo de infraestrutura: 1,5% – 8,0%. "
        "A densidade atual está na faixa ótima: redundância adequada sem "
        "sobrecarga de infraestrutura física."
    ))
    story.append(sp(8))

    # -----------------------------------------------------------------------
    # 4. INFRAESTRUTURA ENERGÉTICA
    # -----------------------------------------------------------------------
    story += section_header("4", "INFRAESTRUTURA ENERGÉTICA — ESCALONAMENTO FASE 3 → FASE 4")
    story.append(body_text(
        "O escalonamento segue a lei de potência Cₙ = C₆ × (N/6)ᵅ. "
        "A Fase 3 é a fonte da verdade: 46 kW para 6 pessoas (NASA DRA 5.0; "
        "Hartwick et al., 2023). O expoente α = 0,7 é aplicado ao LSS porque "
        "água e ar escalam próximo ao linear com a população (metabolismo "
        "direto); α = 0,5 para infraestrutura compartilhada."
    ))
    story.append(sp(4))

    scale_data = [
        ["Parâmetro", "Fórmula", "Resultado"],
        ["SCALE_FACTOR (α = 0,5)", "(1000/6)^0,5", "12,91"],
        ["LSS_SCALE_FACTOR (α = 0,7)", "(1000/6)^0,7", "35,92"],
        ["LSS Fase 3 → Fase 4", "14 kW × 35,92", "≈ 502,6 kW → 505 kW"],
        ["Outros módulos Fase 3 → Fase 4", "32 kW × 12,91", "≈ 413,1 kW"],
        ["Baseline teórico (misto)", "505 + 413 kW", "915,9 kW (TOTAL_CONSUMPTION_BASELINE_KW)"],
        ["Implementado (com AGR, RES, MED+)", "—", "1.030 kW (+12% — módulos Fase 4)"],
    ]
    story.append(dark_table(scale_data, [60*mm, 55*mm, USABLE_W - 115*mm]))
    story.append(sp(6))

    story.append(Paragraph("Consumo por complexo", S["subsection"]))
    cons_data = [
        ["Complexo", "Prioridade", "Consumo", "% total", "Escalonamento"],
        ["LSS — Suporte de Vida", "P1", "505,0 kW", "49,0%", "Fase 3 × 35,92 (α = 0,7)"],
        ["MED — Médico", "P2", "106,0 kW", "10,3%", "SIMULATED"],
        ["MIN — Mineração ISRU", "P4", "93,0 kW", "9,0%", "SIMULATED"],
        ["HAB — Habitacional", "P2", "85,0 kW", "8,3%", "Fase 3 × 12,91 (α = 0,5)"],
        ["AGR — Agricultura", "P3", "63,0 kW", "6,1%", "SIMULATED (novo Fase 4)"],
        ["LOG — Logística", "P4", "50,0 kW", "4,9%", "SIMULATED"],
        ["COM — Comunicação", "P3", "45,0 kW", "4,4%", "SIMULATED"],
        ["RES — Pesquisa", "P5", "41,0 kW", "4,0%", "SIMULATED"],
        ["PWR — Energia", "P1", "27,0 kW", "2,6%", "SIMULATED"],
        ["CTL — Controle", "P1", "15,0 kW", "1,5%", "SIMULATED"],
        ["<b>Total</b>", "—", "<b>1.030 kW</b>", "<b>100%</b>", "1,03 kW/pessoa"],
    ]
    story.append(dark_table(cons_data,
        [42*mm, 18*mm, 22*mm, 18*mm, USABLE_W - 100*mm]))
    story.append(sp(6))

    story.append(Paragraph("Geração e armazenamento", S["subsection"]))
    gen_data = [
        ["Fonte", "Unidades", "Potência média", "Base de cálculo"],
        ["Solar (3 campos × 2.900 m²)", "3 campos", "615,4 kW", "2.900 × 500 W/m² × 0,29 × 0,488"],
        ["Eólica (26 turbinas E33)", "26 turbinas", "624,0 kW", "26 × 24 kW (Hartwick 2023)"],
        ["<b>Total geração média</b>", "—", "<b>1.239 kW</b>", "Margem: 1,20× sobre consumo"],
        ["Baterias (52 bancos × 312 kWh)", "52 bancos", "12.979 kWh úteis", "Pior caso: 1.030 × 12,6 h / 0,80"],
    ]
    story.append(dark_table(gen_data, [50*mm, 28*mm, 28*mm, USABLE_W - 106*mm]))
    story.append(sp(4))
    story.append(body_text(
        "Por que solar e eólica juntas? Complementaridade: solar domina durante o dia; "
        "eólica opera 24h e aumenta durante tempestades de poeira (quando o sol cai). "
        "As baterias cobrem noites calmas (40% das noites, NASA NTRS 19790057281). "
        "Aurora Siger está nos top-3 locais de vento de Marte (Hartwick et al., 2023) "
        "— único lugar onde a E33 atinge 24 kW médios (ρₘₐⱼ"
        "ₜₑ = 0,017 kg/m³, cut-in adaptado: 10,3 m/s)."
    ))
    story.append(sp(8))

    # -----------------------------------------------------------------------
    # 5. ALGORITMOS
    # -----------------------------------------------------------------------
    story += section_header("5", "ALGORITMOS DE GRAFO — BFS, DFS/TARJAN, DIJKSTRA")

    story += subsection_header("5.1  BFS — Busca em Largura  |  O(V + E)")
    story.append(body_text(
        "BFS percorre o grafo em largura usando uma fila deque FIFO. "
        "Garante o caminho com <b>menor número de saltos</b> entre dois nós "
        "(sem considerar peso das arestas). is_network_connected verifica se todos os "
        "módulos ativos são alcançáveis a partir de qualquer ponto."
    ))
    story.append(sp(2))
    story.append(code_block([
        "bfs_traverse(network, start_id)      -> list[str]   # ordem de visita",
        "bfs_shortest_path(network, s, t)     -> list[str]   # caminho por saltos",
        "bfs_reachable(network, start_id)     -> set[str]    # alcancabilidade",
        "is_network_connected(network)        -> bool        # conectividade global",
    ]))
    story.append(sp(6))

    story += subsection_header("5.2  DFS + Tarjan — Detecção de Pontes  |  O(V + E)")
    story.append(body_text(
        "O algoritmo de Tarjan (1972) detecta pontes — arestas cuja remoção "
        "desconecta o grafo. Uma aresta (u, v) é ponte se "
        "low_link[v] > discovery_time[u], onde low_link[v] é o menor discovery_time "
        "alcançável por v via arestas de retorno. Se v não consegue "
        "'voltar' para trás de u, a remoção de (u, v) desconecta o grafo. "
        "O grafo da colônia tem ~76 pontes estruturais — principalmente arestas "
        "group→leaf (inerentes à hierarquia) e algumas de backbone."
    ))
    story.append(sp(2))
    story.append(code_block([
        "find_bridges(network)  -> list[tuple[str, str]]",
        "",
        "# Condicao de ponte:",
        "if low_link[v] > discovery_time[u]:  # (u, v) e uma ponte",
    ]))
    story.append(sp(6))

    story += subsection_header("5.3  Dijkstra — Caminho Mínimo Ponderado  |  O((V + E) log V)")
    story.append(body_text(
        "Dijkstra com min-heap (heapq) calcula o caminho de menor custo acumulado "
        "entre dois módulos. Três critérios de peso implementados com a "
        "mesma estrutura: apenas o campo da aresta lido muda. "
        "dijkstra_all_distances executa Dijkstra de cada nó ativo para todos os "
        "outros — base do cálculo de eficiência global: O(V × (V+E) log V)."
    ))
    story.append(sp(2))
    story.append(code_block([
        "dijkstra_shortest_path(network, s, t, weight_type) -> (list[str], float)",
        "dijkstra_all_distances(network, source, weight_type) -> dict[str, float]",
        "",
        "# WeightType:",
        "#   DISTANCE  -> aresta.distance_m  (metros)",
        "#   ENERGY    -> aresta.energy_cost_kw  (kW)",
        "#   LATENCY   -> aresta.latency_ms  (ms)",
    ]))
    story.append(sp(6))

    algo_data = [
        ["Algoritmo", "Arquivo", "Uso", "Complexidade"],
        ["BFS", "src/bfs.py", "Caminho mínimo por saltos; conectividade", "O(V + E)"],
        ["DFS + Tarjan", "src/dfs.py", "Pontes — remoção desconecta o grafo", "O(V + E)"],
        ["Dijkstra", "src/dijkstra.py", "Caminho ponderado: distância / energia / latência", "O((V+E) log V)"],
    ]
    story.append(dark_table(algo_data, [28*mm, 30*mm, 70*mm, USABLE_W - 128*mm]))
    story.append(sp(8))

    # -----------------------------------------------------------------------
    # 6. MODELOS MATEMÁTICOS
    # -----------------------------------------------------------------------
    story += section_header("6", "MODELOS MATEMÁTICOS")

    story += subsection_header("6.1  Eficiência Global da Rede (GE)")
    story.append(body_text(
        "GE mede quão 'perto' os módulos estão em média. "
        "Quanto maior GE, mais eficiente é o fluxo de informação e "
        "recursos pela rede. Definida por Latora & Marchiori (PRL, 2001):"
    ))
    story.append(sp(2))
    story.append(code_block([
        "GE = (1 / n(n-1)) * sum(1/d(i,j))  para todo i != j",
        "",
        "n      = numero de modulos ativos",
        "d(i,j) = menor distancia em metros entre i e j (Dijkstra DISTANCE)",
    ]))
    story.append(sp(4))

    ge_data = [
        ["GE", "Avaliação"],
        ["< 0,002", "⚠ ABAIXO DO LIMIAR — fluxo crítico comprometido"],
        ["0,002 – 0,005", "● OPERACIONAL"],
        ["> 0,007", "● ALTA EFICIÊNCIA"],
    ]
    story.append(dark_table(ge_data, [40*mm, USABLE_W - 40*mm]))
    story.append(sp(6))

    story += subsection_header("6.2  Custo Energético com Atenuação")
    story.append(body_text(
        "Cada aresta contribui com Pₑ (custo base) mais perdas resistivas proporcionais "
        "à distância em quilômetros. O coeficiente α = 0,05 kW/km "
        "é derivado de NASA ICES-2023-311 para cabos na superfície marciana."
    ))
    story.append(sp(2))
    story.append(code_block([
        "P_rota = sum( P_e * (1 + alfa * d_e / 1000) )  para cada aresta e da rota",
        "",
        "P_e   = custo energetico base da aresta (kW)",
        "d_e   = distancia da aresta (m)",
        "alfa  = 0,05 kW/km  (ENERGY_ATTENUATION_COEFFICIENT)",
    ]))
    story.append(sp(6))

    story += subsection_header("6.3  Densidade da Rede")
    story.append(body_text(
        "Densidade atual: δ = 2×137 / (108×107) = <b>0,0237 (2,37%)</b>. "
        "Faixa ideal: 1,5% – 8,0%. Abaixo de 1,5%: risco de isolamento. "
        "Acima de 8%: sobrecarga de infraestrutura."
    ))
    story.append(sp(8))

    # -----------------------------------------------------------------------
    # 7. SIMULAÇÕES
    # -----------------------------------------------------------------------
    story += section_header("7", "SIMULAÇÕES DE FALHA E RECUPERAÇÃO")
    story.append(body_text(
        "O SIGIC implementa três modos de simulação: falha em cascata, "
        "restauração hierárquica e gestor de emergência energética. "
        "Todos operam sobre o grafo sem modificar o estado de forma permanente "
        "— as operações são reversíveis."
    ))
    story.append(sp(4))

    sim_data = [
        ["Função", "Comportamento"],
        ["cascade_offline(network, module_id)",
         "Desliga módulo e todos os descendentes (BFS hierárquico)"],
        ["cascade_restore(network, module_id)",
         "Restaura módulo e todos os descendentes ao estado OPERATIONAL"],
        ["compute_shutdown_candidates(network, budget_kw)",
         "Greedy: ordena elegíveis por prioridade desc, seleciona para desligar até atingir budget. "
         "Módulos P1 sempre excluídos."],
    ]
    story.append(dark_table(sim_data, [60*mm, USABLE_W - 60*mm]))
    story.append(sp(8))

    # -----------------------------------------------------------------------
    # 8. RELATÓRIO ESG
    # -----------------------------------------------------------------------
    story += section_header("8", "RELATÓRIO ESG — 5 DIMENSÕES")
    story.append(body_text(
        "O relatório ESG analisa 5 dimensões de sustentabilidade e resiliência "
        "da colônia. Todos os limiares estão em src/constants.py."
    ))
    story.append(sp(4))

    esg_data = [
        ["Dimensão", "Métrica", "Limiar / Expectativa"],
        ["Energia sustentável", "Módulos ≥ HIGH_CONSUMPTION_KW", "< 20,0 kW por nó"],
        ["Infraestrutura", "Densidade da rede δ", "1,5% – 8,0% (atual: 2,37% ● IDEAL)"],
        ["Sistemas críticos", "Status dos nós P1 (CTL, PWR, LSS)", "100% OPERACIONAL"],
        ["Governança", "Pontes detectadas (Tarjan)", "≤ 40 (atual: ~76 — majority struct.)"],
        ["Eficiência", "Eficiência Global GE", "≥ 0,002 (atual: ~0,0031 ● OPERACIONAL)"],
    ]
    story.append(dark_table(esg_data,
        [38*mm, 55*mm, USABLE_W - 93*mm]))
    story.append(sp(6))

    story.append(body_text(
        "Nota sobre pontes: o grafo hierárquico da colônia tem ~68 arestas "
        "group→leaf estruturalmente inevitáveis (cada folha numerada tem exatamente "
        "um pai). O limiar BRIDGE_REDUNDANCY_RECOMMENDATION = 40 sinaliza preocu"
        "pação apenas quando pontes além do esperado estrutural "
        "são detectadas."
    ))
    story.append(sp(8))

    # -----------------------------------------------------------------------
    # 9. CRITÉRIOS DA ATIVIDADE
    # -----------------------------------------------------------------------
    story += section_header("9", "CRITÉRIOS DA ATIVIDADE ATENDIDOS")
    story.append(sp(4))
    crit_data = [
        ["Critério", "Implementação"],
        ["Grafo e topologia",
         "ColonyNetwork — grafo não-direcionado ponderado; 108 nós em hierarquia "
         "de 3 camadas; 137 arestas em 4 categorias; densidade 2,37%"],
        ["Algoritmos de busca",
         "BFS O(V+E) — caminho por saltos; DFS + Tarjan O(V+E) — detecção "
         "de pontes; Dijkstra O((V+E)log V) — 3 critérios de peso"],
        ["Modelos matemáticos",
         "Eficiência global (Latora & Marchiori, 2001); atenuação energética "
         "(NASA ICES-2023-311); densidade de rede"],
        ["Infraestrutura energética",
         "1.030 kW para 1.000 pessoas; solar + eólica + 52 bancos de bateria; "
         "escalonamento lei de potência documentado da Fase 3"],
        ["Relatório ESG",
         "5 dimensões: energia sustentável, infraestrutura, sistemas críticos, "
         "governança, eficiência global"],
        ["Implementação Python",
         "Funções puras; dataclasses frozen; deque O(1); separação por "
         "responsabilidade; Rich para UI; constants.py única fonte da verdade"],
    ]
    story.append(dark_table(crit_data, [42*mm, USABLE_W - 42*mm]))
    story.append(sp(8))

    # -----------------------------------------------------------------------
    # 10. REFERÊNCIAS
    # -----------------------------------------------------------------------
    story += section_header("10", "REFERÊNCIAS")
    refs = [
        ("Hartwick, V. L. et al.",
         "Wind power potential on Mars. Nature Astronomy, 2023. "
         "Top-3 locais eólicos; 24 kW/turbina."),
        ("Musk, E.",
         "Making Humans a Multi-Planetary Species. New Space, 5(2), 2017. "
         "Colônia de 1.000 pessoas — capacidade inicial Starship."),
        ("Latora, V.; Marchiori, M.",
         "Efficient Behavior of Small-World Networks. "
         "Physical Review Letters 87(19), 2001. Fórmula de eficiência global (GE)."),
        ("Tarjan, R. E.",
         "Depth-First Search and Linear Graph Algorithms. "
         "SIAM J. Comput. 1(2), 1972. Algoritmo de pontes."),
        ("NASA.",
         "ICES-2023-311: Power Cable Sizing for Mars Surface Applications, 2023. "
         "Coeficiente de atenuação α = 0,05 kW/km."),
        ("arXiv:2410.00066",
         "Mars colony energy reference architecture. "
         "Painel solar 29% eficiência; bateria 312 kWh; baseline Fase 3."),
        ("Drake, B. G. (ed.)",
         "NASA Design Reference Architecture 5.0 (DRA 5.0), 2009. "
         "Baseline de 6 pessoas, 46 kW — fonte da verdade Fase 3."),
        ("NASA ECLSS.",
         "NTRS 20230002103: Environmental Control and Life Support System Overview. "
         "Consumo LSS para 6 pessoas; operação 24h."),
        ("Appelbaum, J.; Flood, D. J.",
         "Solar Radiation on Mars. NASA TM-102299, 1989. "
         "Irradiância superficial: 500 W/m²."),
        ("NASA.",
         "NTRS 19790057281: Viking Lander 2 Meteorology Data. "
         "Vento noturno abaixo do cut-in em 40% das noites."),
        ("Wheeler, R. M.",
         "Agriculture for Space: People and Places Paving the Way. "
         "Open Agriculture, 2017. Área agrícola por pessoa."),
        ("NASA.",
         "In-Situ Resource Utilization Roadmap, 2023. "
         "Consumo de mineração ISRU para colônias permanentes."),
    ]
    for autores, texto in refs:
        story.append(Paragraph(
            f"• <b>{autores}</b> {texto}", S["ref"]))

    story += references_footer()
    build_pdf(story, "relatorio_sigic_aurora_siger.pdf")


if __name__ == "__main__":
    build_fase4()
