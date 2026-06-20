"""
Aurora Siger Fase 4 — Gerador de Relatório Técnico PDF
=======================================================
SIGIC — Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia.
Dark mode, design Aurora Siger.

Uso:
  pip install reportlab
  python build_report.py

Saídas:
  relatorio_sigic_aurora_siger.pdf  — relatório técnico completo
  rede_colonia.pdf                  — diagrama standalone da rede (exigido no zip)
"""

from __future__ import annotations

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable, HRFlowable, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

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

PAGE_W, PAGE_H = A4
MARGIN   = 20 * mm
USABLE_W = PAGE_W - 2 * MARGIN

# Priority palette
P_COLORS = {
    1: colors.HexColor("#e74c3c"),
    2: colors.HexColor("#e67e22"),
    3: colors.HexColor("#f1c40f"),
    4: colors.HexColor("#52be80"),
    5: colors.HexColor("#5dade2"),
}
P_LABELS = {
    1: "P1 — CRÍTICO",
    2: "P2 — ALTO",
    3: "P3 — ESSENCIAL",
    4: "P4 — OPERACIONAL",
    5: "P5 — PESQUISA",
}

# Edge type palette
E_COLORS = {
    "T": colors.HexColor("#3a6fd8"),
    "S": colors.HexColor("#e8a020"),
    "W": colors.HexColor("#9b59b6"),
}


def _alpha(hex_color: colors.HexColor, a: float) -> colors.Color:
    return colors.Color(hex_color.red, hex_color.green, hex_color.blue, alpha=a)


# ---------------------------------------------------------------------------
# NETWORK DIAGRAM — Flowable
# ---------------------------------------------------------------------------
class NetworkDiagram(Flowable):
    """
    Colony network diagram — 10 top-level complexes + 22 backbone edges.
    All logical positions in pt, centered at (0, 0); y+ = up in canvas.
    scale: multiplier applied to all positions and sizes.
    """

    _NODES: dict = {
        "CTL": {"p": 1, "kw":  15, "x":   0,  "y":   0,  "name": "Centro de\nControle"},
        "PWR": {"p": 1, "kw":  27, "x": -135,  "y":  65,  "name": "Energia"},
        "LSS": {"p": 1, "kw": 505, "x": -170,  "y":  -5,  "name": "Suporte\nde Vida"},
        "HAB": {"p": 2, "kw":  85, "x":  168,  "y":   0,  "name": "Habitação"},
        "MED": {"p": 2, "kw": 106, "x":  128,  "y":  72,  "name": "Médico"},
        "COM": {"p": 3, "kw":  45, "x":    0,  "y": 150,  "name": "Comunicação"},
        "AGR": {"p": 3, "kw":  63, "x": -125,  "y": -82,  "name": "Agricultura"},
        "LOG": {"p": 4, "kw":  50, "x":  -42,  "y": -152, "name": "Logística"},
        "MIN": {"p": 4, "kw":  93, "x":  145,  "y": -135, "name": "Mineração\nISRU"},
        "RES": {"p": 5, "kw":  41, "x":   85,  "y":  -82, "name": "Pesquisa"},
    }

    _BACKBONE: list = [
        ("CTL", "COM", "T"), ("CTL", "LSS", "T"), ("CTL", "PWR", "T"),
        ("CTL", "HAB", "T"), ("CTL", "MED", "T"), ("CTL", "LOG", "S"),
        ("PWR", "LSS", "T"), ("PWR", "HAB", "T"), ("PWR", "AGR", "S"),
        ("PWR", "MIN", "S"), ("LSS", "HAB", "T"), ("LSS", "AGR", "S"),
        ("HAB", "MED", "T"), ("HAB", "AGR", "S"), ("HAB", "LOG", "S"),
        ("MED", "RES", "T"), ("COM", "RES", "W"), ("AGR", "LOG", "S"),
        ("MIN", "LOG", "S"), ("MIN", "RES", "S"), ("RES", "AGR", "S"),
        ("COM", "HAB", "T"),
    ]

    def __init__(self, width: float, height: float, scale: float = 1.0) -> None:
        super().__init__()
        self.width = width
        self.height = height
        self.scale = scale

    def draw(self) -> None:
        c = self.canv
        w, h = self.width, self.height
        s = self.scale
        cx, cy = w / 2, h / 2
        r = 26 * s

        def pos(nid: str) -> tuple[float, float]:
            n = self._NODES[nid]
            return cx + n["x"] * s, cy + n["y"] * s

        # background
        c.setFillColor(BG)
        c.rect(0, 0, w, h, fill=1, stroke=0)

        # faint radial guides
        c.setStrokeColor(_alpha(BLUE_RULE, 0.07))
        c.setLineWidth(0.4)
        for rad in (90 * s, 168 * s):
            c.circle(cx, cy, rad, fill=0, stroke=1)

        # edges
        for src, dst, etype in self._BACKBONE:
            x1, y1 = pos(src)
            x2, y2 = pos(dst)
            c.setStrokeColor(E_COLORS[etype])
            c.setLineWidth(1.8 if etype == "T" else 1.2)
            c.setDash([5, 5] if etype == "W" else [])
            c.line(x1, y1, x2, y2)
        c.setDash([])

        # nodes
        for nid, info in self._NODES.items():
            x, y = pos(nid)
            pc = P_COLORS[info["p"]]

            # glow ring
            c.setFillColor(_alpha(pc, 0.12))
            c.setStrokeColor(colors.transparent)
            c.circle(x, y, r + 7 * s, fill=1, stroke=0)

            # node body
            c.setFillColor(BG_CARD)
            c.setStrokeColor(pc)
            c.setLineWidth(2.2)
            c.circle(x, y, r, fill=1, stroke=1)

            # code (inside, upper half)
            c.setFillColor(pc)
            c.setFont("Helvetica-Bold", max(9 * s, 7))
            c.drawCentredString(x, y + 5 * s, nid)

            # kW (inside, lower half)
            c.setFillColor(BODY_TEXT)
            c.setFont("Helvetica", max(6.5 * s, 5.5))
            c.drawCentredString(x, y - 7 * s, f"{info['kw']} kW")

            # name label — positioned by quadrant
            nx, ny = info["x"], info["y"]
            name_lines = info["name"].split("\n")
            fs = max(6 * s, 5.0)
            lh = fs + 2

            if abs(nx) >= abs(ny):          # more horizontal than vertical
                if nx < 0:                  # left → text left-aligned to the left
                    tx = x - r - 6 * s
                    for i, ln in enumerate(name_lines):
                        ty = y + (len(name_lines) - 1) * lh / 2 - i * lh
                        c.setFillColor(STAR_GRAY)
                        c.setFont("Helvetica", fs)
                        c.drawRightString(tx, ty, ln)
                else:                       # right → text right-aligned to the right
                    tx = x + r + 6 * s
                    for i, ln in enumerate(name_lines):
                        ty = y + (len(name_lines) - 1) * lh / 2 - i * lh
                        c.setFillColor(STAR_GRAY)
                        c.setFont("Helvetica", fs)
                        c.drawString(tx, ty, ln)
            elif ny > 0:                    # upper half → text above
                for i, ln in enumerate(name_lines[::-1]):
                    ty = y + r + 8 * s + i * lh
                    c.setFillColor(STAR_GRAY)
                    c.setFont("Helvetica", fs)
                    c.drawCentredString(x, ty, ln)
            else:                           # lower half → text below
                for i, ln in enumerate(name_lines):
                    ty = y - r - 8 * s - i * lh
                    c.setFillColor(STAR_GRAY)
                    c.setFont("Helvetica", fs)
                    c.drawCentredString(x, ty, ln)

        # legend — priorities
        lx, ly = 14, h - 16
        c.setFont("Helvetica-Bold", 6.5)
        c.setFillColor(STAR_GRAY)
        c.drawString(lx, ly, "PRIORIDADE")
        ly -= 10
        for p in range(1, 6):
            c.setFillColor(P_COLORS[p])
            c.circle(lx + 5, ly + 3, 4, fill=1, stroke=0)
            c.setFillColor(STAR_GRAY)
            c.setFont("Helvetica", 6)
            c.drawString(lx + 13, ly + 1, P_LABELS[p])
            ly -= 9

        # legend — edge types
        ly -= 4
        c.setFont("Helvetica-Bold", 6.5)
        c.setFillColor(STAR_GRAY)
        c.drawString(lx, ly, "CONEXÃO")
        ly -= 10
        for etype, label in [("T", "Túnel pressurizado"),
                              ("S", "Rota de superfície"),
                              ("W", "Sem fio (wireless)")]:
            c.setStrokeColor(E_COLORS[etype])
            c.setLineWidth(1.5)
            c.setDash([4, 4] if etype == "W" else [])
            c.line(lx, ly + 3, lx + 18, ly + 3)
            c.setDash([])
            c.setFillColor(STAR_GRAY)
            c.setFont("Helvetica", 6)
            c.drawString(lx + 22, ly + 1, label)
            ly -= 9

        # metrics — bottom right
        stats = ["108 nós", "137 arestas", "δ = 2,37%", "3 algoritmos"]
        sx = w - 14
        sy = 12 + len(stats) * 9
        c.setFont("Helvetica-Bold", 6.5)
        c.setFillColor(STAR_GRAY)
        c.drawRightString(sx, sy, "MÉTRICAS")
        sy -= 9
        for st in stats:
            c.setFont("Helvetica", 6)
            c.setFillColor(BODY_TEXT)
            c.drawRightString(sx, sy, st)
            sy -= 9


# ---------------------------------------------------------------------------
# ESTILOS
# ---------------------------------------------------------------------------
def make_styles() -> dict:
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
        caption=ParagraphStyle("caption",
            fontName="Helvetica-Oblique", fontSize=7, leading=10,
            textColor=DIM_TEXT, alignment=TA_CENTER, spaceAfter=5),
        ref=ParagraphStyle("ref",
            fontName="Helvetica", fontSize=8, leading=12,
            textColor=BODY_TEXT, leftIndent=10, firstLineIndent=-10, spaceAfter=3),
    )


S = make_styles()


def sp(n: float = 6) -> Spacer:
    return Spacer(1, n)


def blue_rule() -> HRFlowable:
    return HRFlowable(width="100%", thickness=1.2, color=BLUE_RULE,
                      spaceAfter=8, spaceBefore=4)


def dim_rule() -> HRFlowable:
    return HRFlowable(width="100%", thickness=0.4, color=RULE_DIM,
                      spaceAfter=5, spaceBefore=2)


def dark_table(data: list, col_widths: list,
               extra_styles: list | None = None) -> Table:
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
        for es in extra_styles:
            ts.add(*es)
    t = Table(data, colWidths=col_widths)
    t.setStyle(ts)
    return t


def code_block(lines: list[str]) -> Paragraph:
    text = "<br/>".join(
        l.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        for l in lines)
    return Paragraph(text, S["code"])


# ---------------------------------------------------------------------------
# TEMPLATE DE PÁGINA
# ---------------------------------------------------------------------------
def on_page(canvas, doc) -> None:
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


def on_page_diagram(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
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
# HELPERS
# ---------------------------------------------------------------------------
def section_header(numero: str, titulo: str) -> list:
    return [Paragraph(f"{numero} {titulo}", S["section"]), dim_rule()]


def subsection_header(titulo: str) -> list:
    return [Paragraph(titulo, S["subsection"])]


def body_text(texto: str) -> Paragraph:
    return Paragraph(texto, S["body"])


def references_footer() -> list:
    return [
        sp(10),
        HRFlowable(width="60%", thickness=0.6, color=BLUE_RULE,
                   hAlign="CENTER", spaceAfter=8, spaceBefore=4),
        Paragraph(
            '★ "A complexidade de um sistema não é fraqueza '
            '— é o mapa de suas possibilidades." ★',
            S["cover_quote"]),
    ]


def build_pdf(story: list, output_path: str,
              first_cb=None, later_cb=None) -> None:
    first_cb = first_cb or on_page
    later_cb = later_cb or on_page
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=20*mm, bottomMargin=20*mm,
    )
    doc.build(story, onFirstPage=first_cb, onLaterPages=later_cb)
    print(f"PDF: {output_path} ({os.path.getsize(output_path):,} bytes)")


# ---------------------------------------------------------------------------
# CAPA
# ---------------------------------------------------------------------------
def cover_page() -> list:
    equipe = [
        ("Julia Ramos",            "RM568988", "linkedin.com/in/juliaramosguedes"),
        ("Matheus Fuchelberguer",  "RM569113", "linkedin.com/in/matheus-fuchelberguer-neves"),
        ("Carlos Eugenio Andrade", "RM570285", "linkedin.com/in/carloseugenioandrade"),
        ("Rodrigo Gomes Dias",     "RM569142", "linkedin.com/in/rodrigogmdias"),
    ]
    badges = [
        ("108 NÓS",      "CTL PWR LSS HAB\nMED COM AGR LOG MIN RES"),
        ("137 ARESTAS",  "backbone · parent-child\ncross · group-leaf"),
        ("3 ALGORITMOS", "BFS · DFS/Tarjan\nDijkstra (3 pesos)"),
        ("STATUS",       "COLÔNIA\nOPERACIONAL"),
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
        ("TEXTCOLOR",     (0, 0), ( 0, -1), TITLE_WHITE),
        ("TEXTCOLOR",     (1, 0), ( 1, -1), STAR_GRAY),
        ("TEXTCOLOR",     (2, 0), ( 2, -1), BLUE_LINK),
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME",      (2, 0), ( 2, -1), "Helvetica-Oblique"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("GRID",          (0, 0), (-1, -1), 0.4, CELL_BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ])
    s.append(Table(equipe, colWidths=[70*mm, 38*mm, 62*mm], style=team_ts))
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

    n = len(badges)
    bw = USABLE_W / n
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
    s.append(Table([[b[0] for b in badges], [b[1] for b in badges]],
                   colWidths=[bw] * n, style=badge_ts))
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------------------
# STANDALONE — rede_colonia.pdf
# ---------------------------------------------------------------------------
def build_colonia_diagram() -> None:
    """Generate rede_colonia.pdf — standalone colony network diagram (zip requirement)."""
    title_style = ParagraphStyle("diag_title",
        fontName="Helvetica-Bold", fontSize=20, leading=26,
        textColor=TITLE_WHITE, alignment=TA_CENTER, spaceAfter=4)
    sub_style = ParagraphStyle("diag_sub",
        fontName="Helvetica", fontSize=9.5, leading=14,
        textColor=STAR_GRAY, alignment=TA_CENTER, spaceAfter=6)

    diag_w = PAGE_W - 2 * MARGIN
    diag_h = 560

    story = [
        sp(8),
        Paragraph("REDE DA COLÔNIA — AURORA SIGER", title_style),
        Paragraph(
            "SIGIC · Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia  "
            "·  108 nós · 137 arestas · 10 complexos · 1.030 kW",
            sub_style),
        HRFlowable(width="100%", thickness=1.0, color=BLUE_RULE,
                   spaceAfter=10, spaceBefore=2),
        NetworkDiagram(width=diag_w, height=diag_h, scale=1.15),
        sp(10),
        HRFlowable(width="100%", thickness=0.4, color=RULE_DIM,
                   spaceAfter=6, spaceBefore=4),
    ]

    info_data = [
        ["Métrica", "Valor", "Referência"],
        ["Nós totais", "108",
         "CTL+PWR+LSS+HAB+MED+COM+AGR+LOG+MIN+RES + grupos + folhas"],
        ["Arestas únicas", "137",
         "22 backbone + 31 parent-child + 17 cross-complex + 67 group→leaf"],
        ["Densidade (δ)", "2,37%",
         "2|E|/(|V|×(|V|−1))  —  faixa ideal: 1,5% – 8,0%"],
        ["Consumo total", "1.030 kW", "1,03 kW/pessoa para 1.000 habitantes"],
        ["Geração média", "1.239 kW",
         "Solar 615 kW + Eólica 624 kW  —  margem 1,20×"],
    ]
    story.append(dark_table(info_data, [38*mm, 30*mm, USABLE_W - 68*mm]))
    story.append(sp(8))

    prio_data = [
        ["Cor", "Prioridade", "Complexos"],
        ["● P1 — CRÍTICO",      "Sem desligamento permitido",     "CTL · PWR · LSS"],
        ["● P2 — ALTO",         "Desligamento só em emergência",  "HAB · MED"],
        ["● P3 — ESSENCIAL",    "Redução controlada",             "COM · AGR"],
        ["● P4 — OPERACIONAL",  "Pode entrar em standby",         "LOG · MIN"],
        ["● P5 — PESQUISA",     "Primeira a ser reduzida",        "RES"],
    ]
    prio_ts = [
        ("TEXTCOLOR", (0, 1), (0, 1), P_COLORS[1]),
        ("TEXTCOLOR", (0, 2), (0, 2), P_COLORS[2]),
        ("TEXTCOLOR", (0, 3), (0, 3), P_COLORS[3]),
        ("TEXTCOLOR", (0, 4), (0, 4), P_COLORS[4]),
        ("TEXTCOLOR", (0, 5), (0, 5), P_COLORS[5]),
    ]
    story.append(dark_table(prio_data, [42*mm, 72*mm, USABLE_W - 114*mm],
                            extra_styles=prio_ts))
    story.append(sp(8))
    story.append(Paragraph(
        '★ "A complexidade de um sistema não é fraqueza '
        '— é o mapa de suas possibilidades." ★',
        S["cover_quote"]))

    build_pdf(story, "rede_colonia.pdf",
              first_cb=on_page_diagram, later_cb=on_page_diagram)


# ---------------------------------------------------------------------------
# RELATÓRIO PRINCIPAL
# ---------------------------------------------------------------------------
def build_fase4() -> None:
    story: list = []
    story += cover_page()

    # 1. INTRODUÇÃO
    story += section_header("1", "INTRODUÇÃO — A COLÔNIA EM ESCALA INDUSTRIAL")
    story.append(body_text(
        "A Aurora Siger completou sua expansão crítica. A colônia que começou "
        "com 6 pessoas e 46 kW na Fase 3 (MGAB) opera agora com 1.000 habitantes "
        "distribuídos em 10 complexos interconectados, consumindo 1.030 kW em operação "
        "contínua. O desafio deixou de ser sobrevivência energética — passou a ser "
        "gestão de complexidade de infraestrutura."
    ))
    story.append(body_text(
        "O SIGIC modela esta infraestrutura como um grafo ponderado não-direcionado "
        "de 108 nós e 137 arestas. Os três algoritmos clássicos de grafo — "
        "BFS, DFS/Tarjan e Dijkstra — detectam pontes (pontos únicos de falha), "
        "calculam rotas de menor custo energético e medem eficiência global da rede."
    ))
    story.append(body_text(
        "O escalonamento de Fase 3 para Fase 4 segue a lei de potência: "
        "Cₙ = C₆ × (N/6)ᵅ, com α = 0,5 para infraestrutura compartilhada e "
        "α = 0,7 para suporte de vida (LSS). Todos os parâmetros físicos declarados em "
        "src/constants.py — única fonte da verdade do sistema."
    ))
    story.append(sp(8))

    # 2. ARQUITETURA
    story += section_header("2", "ARQUITETURA DO SISTEMA SIGIC")
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
        ["enums.py", "ModuleStatus, EdgeType, WeightType"],
        ["models.py", "Module, Edge, ColonyNetwork (dataclasses frozen)"],
    ]
    story.append(dark_table(arch_data, [45*mm, USABLE_W - 45*mm]))
    story.append(sp(8))

    # 3. TOPOLOGIA — com diagrama
    story += section_header("3", "TOPOLOGIA DO GRAFO — 108 NÓS, 137 ARESTAS")
    story.append(body_text(
        "G = (V, E) com hierarquia em 3 camadas: complexo raíz → nó de grupo → "
        "folha numerada. A função expand() gera automaticamente nó de grupo, N folhas "
        "e N arestas internas em um único call — topologia determinística e auditável."
    ))
    story.append(sp(6))

    story.append(NetworkDiagram(width=USABLE_W, height=370, scale=0.97))
    story.append(sp(4))
    story.append(Paragraph(
        "Fig. 1 — Rede Aurora Siger: 10 complexos e 22 conexões backbone. "
        "Cor = prioridade. Azul = túnel pressurizado; laranja = superfície; roxo tracejado = sem fio.",
        S["caption"]))
    story.append(sp(6))

    node_data = [
        ["Camada", "Qtd.", "Exemplos"],
        ["Complexos (top-level)", "10", "CTL, PWR, LSS, HAB, MED, COM, AGR, LOG, MIN, RES"],
        ["Grupos (subsistemas multi-unidade)", "24", "SOL, WND, BAT, ATM, WAT, QRT, DRL..."],
        ["Folhas únicas (filhas diretas)", "7", "DST, EMG, ICU, EDU, GEO, AGT, BIO"],
        ["Folhas numeradas (unidades físicas)", "67", "SOL-01..03, ATM-01..03, QRT-01..08..."],
        ["<b>Total</b>", "<b>108</b>", "—"],
    ]
    story.append(dark_table(node_data, [68*mm, 22*mm, USABLE_W - 90*mm]))
    story.append(sp(6))

    edge_data = [
        ["Categoria", "Qtd.", "Descrição"],
        ["Backbone inter-complexo", "22", "Conexões entre os 10 complexos raiz"],
        ["Parent → child", "31", "Cada complexo a seus subsistemas diretos"],
        ["Cross-complex", "17", "Fluxos operacionais entre subsistemas distintos"],
        ["Group → leaf", "67", "Grupo a unidades físicas (geradas por expand())"],
        ["<b>Total único</b>", "<b>137</b>", "—"],
    ]
    story.append(dark_table(edge_data, [55*mm, 18*mm, USABLE_W - 73*mm]))
    story.append(sp(4))
    story.append(body_text(
        "Densidade: δ = 2×137 / (108×107) = <b>0,0237 (2,37%)</b>. "
        "Faixa ideal: 1,5% – 8,0% — o grafo está na zona ótima."
    ))
    story.append(sp(8))

    # 4. ENERGIA
    story += section_header("4", "INFRAESTRUTURA ENERGÉTICA — FASE 3 → FASE 4")
    story.append(body_text(
        "Lei de potência: Cₙ = C₆ × (N/6)ᵅ. Fonte da verdade: Fase 3 — "
        "46 kW para 6 pessoas (NASA DRA 5.0). α = 0,7 para LSS; α = 0,5 para "
        "infraestrutura compartilhada."
    ))
    story.append(sp(4))

    cons_data = [
        ["Complexo", "Prioridade", "Consumo", "% total"],
        ["LSS — Suporte de Vida", "P1", "505,0 kW", "49,0%"],
        ["MED — Médico", "P2", "106,0 kW", "10,3%"],
        ["MIN — Mineração ISRU", "P4", "93,0 kW", "9,0%"],
        ["HAB — Habitacional", "P2", "85,0 kW", "8,3%"],
        ["AGR — Agricultura", "P3", "63,0 kW", "6,1%"],
        ["LOG — Logística", "P4", "50,0 kW", "4,9%"],
        ["COM — Comunicação", "P3", "45,0 kW", "4,4%"],
        ["RES — Pesquisa", "P5", "41,0 kW", "4,0%"],
        ["PWR — Energia", "P1", "27,0 kW", "2,6%"],
        ["CTL — Controle", "P1", "15,0 kW", "1,5%"],
        ["<b>Total</b>", "—", "<b>1.030 kW</b>", "<b>100%</b>"],
    ]
    story.append(dark_table(cons_data, [60*mm, 22*mm, 26*mm, USABLE_W - 108*mm]))
    story.append(sp(6))

    gen_data = [
        ["Fonte", "Especificação", "Potência"],
        ["Solar (3 × 2.900 m²)", "29% efic.; 500 W/m²", "615 kW"],
        ["Eólica (26 × E33)", "24 kW/turbina — top-3 locais Marte", "624 kW"],
        ["<b>Total geração</b>", "Margem 1,20× sobre consumo", "<b>1.239 kW</b>"],
        ["Baterias (52 × 312 kWh)", "1.030×12,6h/0,80 = 16.222 kWh", "12.979 kWh"],
    ]
    story.append(dark_table(gen_data, [50*mm, 75*mm, USABLE_W - 125*mm]))
    story.append(sp(8))

    # 5. ALGORITMOS
    story += section_header("5", "ALGORITMOS DE GRAFO — BFS, DFS/TARJAN, DIJKSTRA")

    story += subsection_header("5.1  BFS — Busca em Largura  |  O(V + E)")
    story.append(body_text(
        "Percorre o grafo em largura com deque FIFO. Garante o caminho com "
        "<b>menor número de saltos</b> entre dois módulos. "
        "is_network_connected verifica se toda a rede é alcançável."
    ))
    story.append(code_block([
        "bfs_traverse(network, start_id)   -> list[str]",
        "bfs_shortest_path(network, s, t)  -> list[str]",
        "is_network_connected(network)     -> bool",
    ]))
    story.append(sp(6))

    story += subsection_header("5.2  DFS + Tarjan — Pontes  |  O(V + E)")
    story.append(body_text(
        "Aresta (u, v) é ponte se low_link[v] > discovery_time[u]. "
        "low_link[v] = menor discovery_time alcançável por v via arestas de retorno. "
        "Se v não consegue 'voltar' para trás de u, remover (u, v) desconecta o grafo. "
        "O grafo da colônia tem ~76 pontes — maioria são group→leaf (estruturais)."
    ))
    story.append(code_block([
        "find_bridges(network)  -> list[tuple[str, str]]",
        "# ponte: low_link[v] > discovery_time[u]",
    ]))
    story.append(sp(6))

    story += subsection_header("5.3  Dijkstra — Caminho Mínimo Ponderado  |  O((V + E) log V)")
    story.append(body_text(
        "Min-heap (heapq) com três critérios. dijkstra_all_distances executa de "
        "cada nó ativo para todos os outros — base do cálculo de GE: O(V×(V+E) log V)."
    ))
    story.append(code_block([
        "dijkstra_shortest_path(network, s, t, weight_type) -> (list[str], float)",
        "# WeightType: DISTANCE (m) | ENERGY (kW) | LATENCY (ms)",
    ]))
    story.append(sp(8))

    # 6. MODELOS MATEMÁTICOS
    story += section_header("6", "MODELOS MATEMÁTICOS")

    story += subsection_header("6.1  Eficiência Global da Rede (GE)  |  Latora & Marchiori, 2001")
    story.append(code_block([
        "GE = (1 / n(n-1)) * sum(1/d(i,j))  para todo i != j",
        "n = modulos ativos | d(i,j) = menor distancia em metros (Dijkstra)",
    ]))
    ge_data = [
        ["GE", "Avaliação"],
        ["< 0,002", "⚠ ABAIXO DO LIMIAR — fluxo crítico comprometido"],
        ["0,002 – 0,007", "● OPERACIONAL  (atual: ~0,0031)"],
        ["> 0,007", "● ALTA EFICIÊNCIA"],
    ]
    story.append(dark_table(ge_data, [40*mm, USABLE_W - 40*mm]))
    story.append(sp(6))

    story += subsection_header("6.2  Atenuação Energética  |  NASA ICES-2023-311")
    story.append(code_block([
        "P_rota = sum( P_e * (1 + 0.05 * d_e / 1000) )  para cada aresta e na rota",
    ]))
    story.append(sp(6))

    story += subsection_header("6.3  Densidade  |  δ = 2|E| / (|V|×(|V|−1))")
    story.append(body_text(
        "δ atual = <b>2,37%</b>. Ideal: 1,5% – 8,0%. "
        "Abaixo de 1,5%: risco de isolamento. Acima de 8%: sobrecarga física."
    ))
    story.append(sp(8))

    # 7. ESTRUTURAS DE DADOS
    story += section_header("7", "ESTRUTURAS DE DADOS")
    ds_data = [
        ["Estrutura", "Tipo Python", "Papel no SIGIC"],
        ["ColonyNetwork", "dataclass (frozen)", "Grafo — todo o estado da colônia"],
        ["modules", "dict[str, Module]", "Lookup O(1) de módulo por ID"],
        ["adjacency_list", "dict[str, list[Edge]]", "Vizinhos de um nó em O(1)"],
        ["visited", "set[str]", "BFS/DFS: marcação O(1) de nós visitados"],
        ["queue", "deque[str]", "BFS — FIFO com enqueue/dequeue O(1)"],
        ["dist", "dict[str, float]", "Dijkstra: distâncias mínimas acumuladas"],
        ["heap", "list heapq", "Dijkstra: min-heap O(log V) por operação"],
        ["discovery_time / low_link", "dict[str, int]", "Tarjan: timestamps DFS para pontes"],
    ]
    story.append(dark_table(ds_data, [38*mm, 48*mm, USABLE_W - 86*mm]))
    story.append(sp(8))

    # 8. SIMULAÇÕES
    story += section_header("8", "SIMULAÇÕES DE FALHA E RECUPERAÇÃO")
    sim_data = [
        ["Função", "Comportamento"],
        ["cascade_offline(network, module_id)",
         "Desliga módulo e todos os descendentes (BFS hierárquico)"],
        ["cascade_restore(network, module_id)",
         "Restaura módulo e todos os descendentes ao estado OPERATIONAL"],
        ["compute_shutdown_candidates(network, budget_kw)",
         "Greedy: ordena elegíveis por prioridade desc, desliga até atingir budget. "
         "Módulos P1 sempre excluídos."],
    ]
    story.append(dark_table(sim_data, [65*mm, USABLE_W - 65*mm]))
    story.append(sp(8))

    # 9. ESG
    story += section_header("9", "RELATÓRIO ESG — 5 DIMENSÕES")
    esg_data = [
        ["Dimensão", "Métrica", "Resultado"],
        ["Energia sustentável", "Módulos ≥ HIGH_CONSUMPTION_KW", "< 20,0 kW por nó"],
        ["Infraestrutura", "Densidade δ", "2,37%  ● IDEAL"],
        ["Sistemas críticos", "Status dos nós P1", "CTL · PWR · LSS — OPERACIONAL"],
        ["Governança", "Pontes (Tarjan)", "~76 pontes (~68 group→leaf estruturais)"],
        ["Eficiência", "GE", "~0,0031  ● OPERACIONAL  [limiar ≥ 0,002]"],
    ]
    story.append(dark_table(esg_data, [38*mm, 50*mm, USABLE_W - 88*mm]))
    story.append(sp(8))

    # 10. CRITÉRIOS
    story += section_header("10", "CRITÉRIOS DA ATIVIDADE ATENDIDOS")
    crit_data = [
        ["Critério (10 pts)", "Implementação"],
        ["Integração das disciplinas (2,0)",
         "Grafos + lei de potência (matemática) + ESG (governança) + energia (física)"],
        ["Organização computacional (2,0)",
         "Módulos com responsabilidade única; constants.py fonte única da verdade; "
         "funções puras testáveis; dataclasses frozen"],
        ["Aplicação dos algoritmos (2,5)",
         "BFS O(V+E) — saltos e conectividade; DFS+Tarjan O(V+E) — pontes; "
         "Dijkstra O((V+E)log V) — 3 critérios de peso"],
        ["Estruturas de dados (1,5)",
         "dict/set O(1); deque O(1) BFS; heapq O(log V) Dijkstra; "
         "dataclass frozen; dict adjacency list"],
        ["Sustentabilidade e governança (2,0)",
         "ESG 5 dimensões: energia sustentável, infraestrutura, sistemas críticos, "
         "governança (pontes Tarjan), eficiência global (GE)"],
    ]
    story.append(dark_table(crit_data, [52*mm, USABLE_W - 52*mm]))
    story.append(sp(8))

    # 11. REFERÊNCIAS
    story += section_header("11", "REFERÊNCIAS")
    refs = [
        ("Hartwick, V. L. et al.",
         "Wind power potential on Mars. Nature Astronomy, 2023."),
        ("Musk, E.",
         "Making Humans a Multi-Planetary Species. New Space, 5(2), 2017."),
        ("Latora, V.; Marchiori, M.",
         "Efficient Behavior of Small-World Networks. PRL 87(19), 2001."),
        ("Tarjan, R. E.",
         "Depth-First Search and Linear Graph Algorithms. SIAM J. Comput. 1(2), 1972."),
        ("NASA.",
         "ICES-2023-311: Power Cable Sizing for Mars Surface. 2023."),
        ("arXiv:2410.00066",
         "Mars colony energy reference architecture."),
        ("Drake, B. G. (ed.)",
         "NASA Design Reference Architecture 5.0, 2009."),
        ("NASA ECLSS.",
         "NTRS 20230002103: ECLSS Overview."),
        ("Appelbaum, J.; Flood, D. J.",
         "Solar Radiation on Mars. NASA TM-102299, 1989."),
        ("NASA.",
         "NTRS 19790057281: Viking Lander 2 Meteorology."),
    ]
    for autores, texto in refs:
        story.append(Paragraph(f"• <b>{autores}</b> {texto}", S["ref"]))

    story += references_footer()
    build_pdf(story, "relatorio_sigic_aurora_siger.pdf")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    build_fase4()
    build_colonia_diagram()
