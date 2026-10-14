#!/usr/bin/env python3
"""02 Data Science Collection: section architecture diagram.

One boundary, an aligned grid of unfilled dashed groups, icons on a shared slot grid,
right-angle lines with no crossings, and numbered steps with a plain-English legend.
Every helper and layout check is shared with the other section diagrams; only the EDIT
blocks (line kinds, canvas text, grid, groups, nodes, lines, badges, legend) are scoped
to this section's README. Data-science parts with no official icon are drawn as
stroke-only outline glyphs.

Set up once:  python3 -m venv .venv
              .venv/bin/pip install diagrams==0.25.1
              brew install librsvg                                  (rsvg-convert)
Run:          .venv/bin/python assets/architecture_diagram.py assets/architecture
It writes <out>.svg and <out>.png and must print "layout problems: none".
"""
import base64
import math
import os
import subprocess
import sys

import diagrams

R = os.path.join(os.path.dirname(os.path.dirname(diagrams.__file__)), "resources")
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/arch"
OUT_SVG, OUT_PNG = OUT + ".svg", OUT + ".png"

# ---------------- style ----------------
FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"
INK, TEXT2, LINE, GROUP, BADGE, RULE, ACCENT = (
    "#232F3E", "#545B64", "#3F4752", "#7D8998", "#146EB4", "#E3E6EA", "#8C4FFF")
ICON, HALF = 52, 26
ZOOM = 2  # PNG width = W * ZOOM; rendered at 2x for sharpness, GitHub scales it to fit
# ---------------- EDIT: line kinds ----------------
KINDS = {  # stroke, width, dash, arrowhead marker, legend label
    "service": (LINE, 1.6, None, "ah", "Data read by a notebook or dashboard"),
    "external": (LINE, 1.6, "6 5", "ah", "SQL queries to IBM Db2 on Cloud"),
    "business": (ACCENT, 2.2, None, "ahb", "Not used"),
}

# ---------------- EDIT: canvas text ----------------
W, H = 1900, 1010
TITLE = "02 Data Science Collection | Notebooks and Dash Dashboards"
SUBTITLE = ("Practice projects grouped by data source and output: SpaceX launch notebooks, stock and "
            "housing notebooks, and two Dash dashboards.")
CLOUD, REGION = "Analysis environment", "Python 3 and Jupyter on your computer"
TILE = "programming/language/python.png"

# ---------------- EDIT: grid ----------------
AX0, AX1, AY0, AY1 = 200, 1699, 110, 755             # the one boundary
COLS = [(225, 688), (718, 1181), (1211, 1674)]        # group columns
SL = [[round(x0 + (x1 - x0) * f) for f in (0.2, 0.5, 0.8)] for x0, x1 in COLS]  # icon slots
R0, R1 = (150, 370), (400, 730)                       # rows
A1, Q1, C1, D1 = 230, 340, 480, 640                   # icon lanes (center y); Q1 = SQL line lane

out, icons, SEGS, BADGES = [], [], [], []
N, BOX, USED = {}, {}, set()


def add(s):
    out.append(s)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def est_w(s, size):
    return len(s) * size * 0.53


def text(x, y, s, size=13, weight=400, color=INK, anchor="middle", halo=False):
    h = (' stroke="#FFFFFF" stroke-width="5" stroke-linejoin="round" paint-order="stroke"'
         if halo else "")
    add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}"{h}>{esc(s)}</text>')


_cache = {}


def data(rel):
    if rel not in _cache:
        with open(os.path.join(R, rel), "rb") as fh:
            _cache[rel] = "data:image/png;base64," + base64.b64encode(fh.read()).decode()
    return _cache[rel]


def glyph(kind, cx, cy):
    """Stroke-only outline glyph (no fill) for parts with no official icon."""
    x, y = cx - HALF, cy - HALF
    st = f'fill="none" stroke="{LINE}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"'
    if kind == "globe":  # web page or internet source
        add(f'<circle cx="{cx}" cy="{cy}" r="22" {st}/>')
        add(f'<ellipse cx="{cx}" cy="{cy}" rx="10" ry="22" {st}/>')
        add(f'<path d="M {cx-22},{cy} L {cx+22},{cy} M {cx-19},{cy-11} L {cx+19},{cy-11} '
            f'M {cx-19},{cy+11} L {cx+19},{cy+11}" {st}/>')
    elif kind == "table":  # tabular output
        add(f'<rect x="{x+4}" y="{y+8}" width="44" height="36" rx="3" {st}/>')
        add(f'<path d="M {x+4},{y+20} L {x+48},{y+20} M {x+4},{y+32} L {x+48},{y+32} '
            f'M {x+20},{y+8} L {x+20},{y+44}" {st}/>')
    elif kind == "script":  # script or code stage
        add(f'<rect x="{x+3}" y="{y+8}" width="46" height="36" rx="3" {st}/>')
        add(f'<path d="M {x+11},{y+18} L {x+19},{y+26} L {x+11},{y+34} M {x+23},{y+34} '
            f'L {x+37},{y+34}" {st}/>')
    elif kind == "chart":  # charts
        add(f'<path d="M {x+4},{y+6} L {x+4},{y+46} L {x+48},{y+46}" {st}/>')
        add(f'<rect x="{x+12}" y="{y+22}" width="9" height="24" {st}/>')
        add(f'<rect x="{x+26}" y="{y+12}" width="9" height="34" {st}/>')
        add(f'<rect x="{x+40}" y="{y+30}" width="6" height="16" {st}/>')
    elif kind == "doc":  # data file
        add(f'<path d="M {x+10},{y+4} L {x+34},{y+4} L {x+44},{y+14} L {x+44},{y+48} L {x+10},{y+48} Z '
            f'M {x+34},{y+4} L {x+34},{y+14} L {x+44},{y+14}" {st}/>')
        add(f'<path d="M {x+17},{y+24} L {x+37},{y+24} M {x+17},{y+32} L {x+37},{y+32} '
            f'M {x+17},{y+40} L {x+31},{y+40}" {st}/>')
    elif kind == "trash":  # discard
        add(f'<path d="M {x+8},{y+12} L {x+44},{y+12} M {cx-6},{y+12} L {cx-6},{y+6} L {cx+6},{y+6} '
            f'L {cx+6},{y+12} M {x+12},{y+12} L {x+15},{y+48} L {x+37},{y+48} L {x+40},{y+12} '
            f'M {cx-6},{y+20} L {cx-6},{y+40} M {cx+6},{y+20} L {cx+6},{y+40}" {st}/>')
    elif kind == "folder":  # folder of files
        add(f'<path d="M {x+4},{y+12} L {x+20},{y+12} L {x+25},{y+17} L {x+48},{y+17} L {x+48},{y+44} '
            f'L {x+4},{y+44} Z M {x+4},{y+22} L {x+48},{y+22}" {st}/>')
    elif kind == "flow":  # router or selector
        add(f'<rect x="{x+4}" y="{y+20}" width="16" height="12" rx="2" {st}/>')
        add(f'<rect x="{x+32}" y="{y+6}" width="16" height="12" rx="2" {st}/>')
        add(f'<rect x="{x+32}" y="{y+34}" width="16" height="12" rx="2" {st}/>')
        add(f'<path d="M {x+20},{y+26} L {x+26},{y+26} L {x+26},{y+12} L {x+32},{y+12} '
            f'M {x+26},{y+26} L {x+26},{y+40} L {x+32},{y+40}" {st}/>')
    elif kind == "person":  # a person at their own computer
        add(f'<circle cx="{cx}" cy="{y+15}" r="9" {st}/>')
        add(f'<path d="M {x+8},{y+48} C {x+8},{y+34} {x+16},{y+28} {cx},{y+28} C {x+36},{y+28} '
            f'{x+44},{y+34} {x+44},{y+48}" {st}/>')
    elif kind == "notebook":  # Jupyter notebook
        add(f'<rect x="{x+12}" y="{y+4}" width="34" height="44" rx="3" {st}/>')
        for i in range(4):
            add(f'<circle cx="{x+12}" cy="{y+12+i*10}" r="3" {st}/>')
        add(f'<path d="M {x+21},{y+16} L {x+39},{y+16} M {x+21},{y+24} L {x+39},{y+24} '
            f'M {x+21},{y+32} L {x+33},{y+32}" {st}/>')
    elif kind == "dashboard":  # web dashboard
        add(f'<rect x="{x+3}" y="{y+6}" width="46" height="40" rx="3" {st}/>')
        add(f'<path d="M {x+3},{y+14} L {x+49},{y+14}" {st}/>')
        add(f'<circle cx="{x+16}" cy="{y+30}" r="9" {st}/>')
        add(f'<path d="M {x+16},{y+21} L {x+16},{y+30} L {x+25},{y+30}" {st}/>')
        add(f'<path d="M {x+31},{y+40} L {x+31},{y+32} M {x+37},{y+40} L {x+37},{y+24} '
            f'M {x+43},{y+40} L {x+43},{y+28}" {st}/>')
    elif kind == "dataset":  # stored dataset (cylinder)
        add(f'<ellipse cx="{cx}" cy="{y+11}" rx="18" ry="6" {st}/>')
        add(f'<path d="M {x+8},{y+11} L {x+8},{y+41} A 18,6 0 0 0 {x+44},{y+41} L {x+44},{y+11} '
            f'M {x+8},{y+26} A 18,6 0 0 0 {x+44},{y+26}" {st}/>')
    elif kind == "model":  # ML model (decision tree)
        add(f'<rect x="{cx-8}" y="{y+4}" width="16" height="12" rx="2" {st}/>')
        add(f'<rect x="{x+4}" y="{y+36}" width="16" height="12" rx="2" {st}/>')
        add(f'<rect x="{x+32}" y="{y+36}" width="16" height="12" rx="2" {st}/>')
        add(f'<path d="M {cx},{y+16} L {cx},{y+26} M {x+12},{y+26} L {x+40},{y+26} '
            f'M {x+12},{y+26} L {x+12},{y+36} M {x+40},{y+26} L {x+40},{y+36}" {st}/>')
    elif kind == "map":  # folded map with a pin
        add(f'<path d="M {x+4},{y+10} L {x+18},{y+4} L {x+34},{y+10} L {x+48},{y+4} L {x+48},{y+42} '
            f'L {x+34},{y+48} L {x+18},{y+42} L {x+4},{y+48} Z M {x+18},{y+4} L {x+18},{y+42} '
            f'M {x+34},{y+10} L {x+34},{y+48}" {st}/>')
        add(f'<path d="M {x+26},{y+32} C {x+20},{y+24} {x+20},{y+20} {x+20},{y+19} A 6,6 0 0 1 '
            f'{x+32},{y+19} C {x+32},{y+20} {x+32},{y+24} {x+26},{y+32} Z" {st}/>')
    elif kind == "api":  # REST API
        add(f'<rect x="{x+3}" y="{y+10}" width="46" height="32" rx="3" {st}/>')
        add(f'<path d="M {x+19},{y+17} C {x+13},{y+17} {x+16},{cy} {x+11},{cy} C {x+16},{cy} '
            f'{x+13},{y+35} {x+19},{y+35} M {x+33},{y+17} C {x+39},{y+17} {x+36},{cy} {x+41},{cy} '
            f'C {x+36},{cy} {x+39},{y+35} {x+33},{y+35}" {st}/>')
    elif kind == "gear":  # processing engine
        add(f'<circle cx="{cx}" cy="{cy}" r="15" {st}/>')
        add(f'<circle cx="{cx}" cy="{cy}" r="6" {st}/>')
        teeth = " ".join(
            f'M {cx + 15 * math.cos(a):.1f},{cy + 15 * math.sin(a):.1f} '
            f'L {cx + 22 * math.cos(a):.1f},{cy + 22 * math.sin(a):.1f}'
            for a in (i * math.pi / 4 for i in range(8)))
        add(f'<path d="{teeth}" {st}/>')
    elif kind == "mask":  # masked card number
        add(f'<rect x="{x+3}" y="{y+10}" width="46" height="32" rx="3" {st}/>')
        add(f'<path d="M {x+3},{y+19} L {x+49},{y+19}" {st}/>')
        marks = " ".join(f'M {x+9+i*8},{y+28} L {x+14+i*8},{y+33} M {x+14+i*8},{y+28} '
                         f'L {x+9+i*8},{y+33}' for i in range(3))
        add(f'<path d="{marks} M {x+36},{y+31} L {x+44},{y+31}" {st}/>')
    elif kind == "convert":  # type conversion
        add(f'<path d="M {x+6},{y+18} L {x+44},{y+18} M {x+37},{y+11} L {x+44},{y+18} L {x+37},{y+25} '
            f'M {x+46},{y+34} L {x+8},{y+34} M {x+15},{y+27} L {x+8},{y+34} L {x+15},{y+41}" {st}/>')
    elif kind == "calc":  # expression evaluator
        add(f'<rect x="{x+10}" y="{y+4}" width="32" height="44" rx="3" {st}/>')
        add(f'<rect x="{x+15}" y="{y+9}" width="22" height="9" {st}/>')
        for r_ in range(3):
            for c_ in range(3):
                add(f'<rect x="{x+15+c_*8}" y="{y+23+r_*8}" width="5" height="5" {st}/>')
    elif kind == "sql":  # SQL query
        add(f'<ellipse cx="{cx}" cy="{y+11}" rx="18" ry="6" {st}/>')
        add(f'<path d="M {x+8},{y+11} L {x+8},{y+41} A 18,6 0 0 0 {x+44},{y+41} L {x+44},{y+11}" {st}/>')
        add(f'<path d="M {x+16},{y+26} L {x+22},{y+31} L {x+16},{y+36} M {x+26},{y+36} L {x+36},{y+36}" {st}/>')
    else:
        raise ValueError(kind)


def node(key, rel, cx, cy, l1, l2=None):
    """Register an icon (official PNG, or 'glyph:<kind>') at slot (cx, cy) with labels."""
    assert key not in N, key
    N[key] = (cx, cy, 2 if l2 else 1)
    icons.append((rel, cx, cy, l1, l2))
    w = max(ICON, est_w(l1, 13), est_w(l2 or "", 12))
    BOX[key] = (cx - w / 2, cy - HALF, cx + w / 2, cy + HALF + (36 if l2 else 21))


def draw_nodes():
    for rel, cx, cy, l1, l2 in icons:
        if rel.startswith("glyph:"):
            glyph(rel[6:], cx, cy)
        else:
            add(f'<image x="{cx-HALF}" y="{cy-HALF}" width="{ICON}" height="{ICON}" '
                f'xlink:href="{data(rel)}"/>')
        text(cx, cy + HALF + 17, l1, 13, 400, INK)
        if l2:
            text(cx, cy + HALF + 32, l2, 12, 400, TEXT2)


def port(key, side, gap=5):
    """Connection point: l, r, t (top edge of icon), b (below the label block)."""
    cx, cy, n = N[key]
    return {"l": (cx - HALF - gap, cy), "r": (cx + HALF + gap, cy),
            "t": (cx, cy - HALF - gap),
            "b": (cx, cy + HALF + (36 if n == 2 else 21) + gap)}[side]


def path(pts, a, b, kind="service"):
    color, width, dash, marker, _ = KINDS[kind]
    USED.add(kind)
    for p, q in zip(pts, pts[1:]):
        assert p[0] == q[0] or p[1] == q[1], ("diagonal segment", a, b, p, q)
        SEGS.append((p, q, a, b))
    d = "M " + " L ".join(f"{x},{y}" for x, y in pts)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{da} '
        f'marker-end="url(#{marker})"/>')


def link(a, sa, b, sb, kind="service", via=None, end=None):
    """Connect two nodes. via = elbow points; end overrides the target point."""
    path([port(a, sa)] + (via or []) + [end or port(b, sb)], a, b, kind)


def badge(cx, cy, n, record=True):
    if record:
        BADGES.append((cx, cy, n))
    add(f'<rect x="{cx-12}" y="{cy-12}" width="24" height="24" rx="3" fill="{BADGE}"/>')
    text(cx, cy + 4.6, str(n), 13, 700, "#FFFFFF")


def group(x0, y0, x1, y1, title):
    add(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="none" '
        f'stroke="{GROUP}" stroke-width="1.3" stroke-dasharray="5 4"/>')
    text(x0 + 14, y0 + 25, title, 14.5, 700, INK, "start")


def tile(kind, tx, ty):
    """24 px boundary tile: an official icon (path), or a stroke-only glyph scaled down."""
    if "/" in kind:
        add(f'<image x="{tx}" y="{ty}" width="24" height="24" xlink:href="{data(kind)}"/>')
        return
    add(f'<g transform="translate({tx},{ty}) scale({24 / ICON})">')
    glyph(kind, HALF, HALF)
    add('</g>')


# ---------------- canvas and boundary ----------------
add(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
    f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
add('<defs>'
    '<marker id="ah" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6.5" '
    f'markerHeight="6.5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{LINE}"/></marker>'
    '<marker id="ahb" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="5" '
    f'markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{ACCENT}"/></marker>'
    '</defs>')
add(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')
text(40, 52, TITLE, 26, 700, INK, "start")
text(40, 78, SUBTITLE, 14, 400, TEXT2, "start")
add(f'<rect x="{AX0}" y="{AY0}" width="{AX1-AX0}" height="{AY1-AY0}" fill="none" '
    f'stroke="{INK}" stroke-width="1.6"/>')
tile(TILE, AX0 + 6, AY0 + 5)
add(f'<text x="{AX0+38}" y="{AY0+22}" font-family="{FONT}" font-size="14.5" '
    f'font-weight="700" fill="{INK}">{esc(CLOUD)}<tspan dx="10" font-weight="400" '
    f'fill="{TEXT2}">{esc(REGION)}</tspan></text>')

# ---------------- EDIT: groups ----------------
for (x0, x1), (y0, y1), title in [
    (COLS[0], R0, "SpaceX: collect notebooks"),
    (COLS[1], R0, "SpaceX: explore and model"),
    (COLS[2], R0, "SpaceX: dashboard"),
    (COLS[0], R1, "Stocks: collect and chart"),
    (COLS[1], R1, "Housing: regression"),
    (COLS[2], R1, "Airline: dashboard"),
]:
    group(x0, y0, x1, y1, title)

# ---------------- EDIT: nodes ----------------
node("sx_src", "glyph:api", 105, A1, "SpaceX API, Wikipedia", "launch records")
node("yf", "glyph:api", 105, C1, "yfinance", "TSLA price history")
node("web", "glyph:globe", 105, D1, "Web pages", "stock and revenue")
node("course1", "glyph:dataset", 1800, A1, "IBM course files", "spacex_launch_dash.csv")
node("db2", "programming/language/sql.png", 1800, Q1, "IBM Db2 on Cloud", "SpaceX table")
node("course2", "glyph:dataset", 1800, D1, "IBM course files", "house, airline CSVs")
node("sx_col", "glyph:notebook", SL[0][0], A1, "Collection notebooks", "API, web scraping")
node("sx_wr", "glyph:notebook", SL[0][2], A1, "Data Wrangling", "Class landing label")
node("sx_eda", "glyph:notebook", SL[1][0], A1, "EDA notebooks", "SQL, charts, Folium")
node("sx_ml", "glyph:model", SL[1][2], A1, "Machine Learning", "4 tuned classifiers")
node("sx_dash", "glyph:dashboard", SL[2][2], A1, "SpaceX dashboard", "spacex_dash_app.py")
node("tesla", "glyph:notebook", SL[0][0], C1, "Tesla notebooks", "yfinance, Plotly")
node("nflx", "glyph:notebook", SL[0][0], D1, "Netflix V Amazon", "read_html, DataFrames")
node("king", "glyph:model", SL[1][2], D1, "King County houses", "linear, ridge regression")
node("air", "glyph:dashboard", SL[2][2], C1, "Airline dashboard", "Airline Analysis.py")

# ---------------- EDIT: connections ----------------
link("sx_src", "r", "sx_col", "l")
link("sx_col", "r", "sx_wr", "l")
link("sx_wr", "r", "sx_eda", "l")
link("sx_eda", "r", "sx_ml", "l")
link("sx_eda", "b", "db2", "l", "external", via=[(SL[1][0], Q1)])
link("course1", "l", "sx_dash", "r")
link("yf", "r", "tesla", "l")
link("web", "r", "nflx", "l")
link("web", "t", "tesla", "b", via=[(105, 578), (SL[0][0], 578)])
link("course2", "l", "king", "r")
link("course2", "t", "air", "r", via=[(1800, C1)])

# ---------------- EDIT: line labels (white halo keeps them readable over lines) ----------------
LBL = 11.5
text(1300, Q1 - 8, "%sql queries", LBL, 400, TEXT2, "middle", halo=True)
text(1300, D1 - 8, "house sales CSV", LBL, 400, TEXT2, "middle", halo=True)

draw_nodes()

# ---------------- EDIT: step badges (x, y, number), in a gutter beside their line ----------------
for cx, cy, n in [(457, A1 + 30, 1), (1443, 312, 2), (950, A1 + 30, 3), (1655, 200, 4),
                  (178, C1 - 28, 5), (178, D1 + 28, 6), (1300, D1 + 28, 7), (1655, C1 - 28, 8)]:
    badge(cx, cy, n)

# ---------------- EDIT: legend, one short sentence per badge ----------------
LY = AY1 + 55
STEPS = [
    "SpaceX: notebooks pull launches from the SpaceX API and Wikipedia; Data Wrangling adds the Class label.",
    "EDA queries the launches in IBM Db2 on Cloud with %sql, charts them with seaborn, and maps the sites with Folium.",
    "Machine Learning Prediction tunes logistic regression, SVM, decision tree, and KNN with GridSearchCV.",
    "The SpaceX Dash app reads the course file spacex_launch_dash.csv for its success pie and payload scatter charts.",
    "Tesla notebooks pull TSLA prices with yfinance, scrape revenue with BeautifulSoup, and chart both with Plotly.",
    "Netflix V Amazon reads course-hosted stock pages with requests, BeautifulSoup, and pandas.read_html.",
    "King County explores course house sales data with seaborn and fits linear, polynomial, and ridge regression.",
    "The airline Dash app reads a course flights CSV and draws yearly performance or delay reports for 2005 to 2020.",
]

# ---------------- legend and key ----------------
text(40, LY, "How it works", 16, 700, INK, "start")
per_col = (len(STEPS) + 1) // 2
for i, s in enumerate(STEPS):
    col, row = divmod(i, per_col)
    bx, by = 52 + col * 920, LY + 32 + row * 30
    badge(bx, by, i + 1, record=False)
    text(bx + 22, by + 4.6, s, 13.5, 400, INK, "start")
    if est_w(s, 13.5) > 880:
        print("legend line too long:", i + 1)

# line-style key, one entry per line kind actually used
KEY_Y = LY + 36 + per_col * 30
lx = 40
for k, (color, width, dash, marker, label) in KINDS.items():
    if k not in USED:
        continue
    da = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<path d="M {lx},{KEY_Y} L {lx+52},{KEY_Y}" stroke="{color}" stroke-width="{width}"'
        f'{da} marker-end="url(#{marker})"/>')
    text(lx + 62, KEY_Y + 4.5, label, 12.5, 400, TEXT2, "start")
    lx += 62 + est_w(label, 12.5) + 48
add("</svg>")
assert KEY_Y + 30 <= H, "canvas too short for the legend: raise H"


# ---------------- checks ----------------
def seg_hits_box(p, q, box, pad=2):
    x0, y0, x1, y1 = box
    (ax, ay), (bx, by) = p, q
    if ay == by:
        lo, hi = sorted((ax, bx))
        return y0 - pad < ay < y1 + pad and lo < x1 + pad and hi > x0 - pad
    lo, hi = sorted((ay, by))
    return x0 - pad < ax < x1 + pad and lo < y1 + pad and hi > y0 - pad


def boxes_overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def crossings():
    hs = [s for s in SEGS if s[0][1] == s[1][1]]
    vs = [s for s in SEGS if s[0][0] == s[1][0]]
    found = []
    for hp, hq, ha, hb in hs:
        y = hp[1]
        x0, x1 = sorted((hp[0], hq[0]))
        for vp, vq, va, vb in vs:
            if (ha, hb) == (va, vb):
                continue
            x = vp[0]
            y0, y1 = sorted((vp[1], vq[1]))
            if x0 < x < x1 and y0 < y < y1:
                found.append(f"{ha}->{hb} x {va}->{vb}")
    return found


def shared_segments():
    found = []
    for i in range(len(SEGS)):
        for j in range(i + 1, len(SEGS)):
            (p, q, a, b), (r, s, c, d) = SEGS[i], SEGS[j]
            if (a, b) == (c, d):
                continue
            if p[1] == q[1] == r[1] == s[1]:
                lo1, hi1 = sorted((p[0], q[0]))
                lo2, hi2 = sorted((r[0], s[0]))
            elif p[0] == q[0] == r[0] == s[0]:
                lo1, hi1 = sorted((p[1], q[1]))
                lo2, hi2 = sorted((r[1], s[1]))
            else:
                continue
            if min(hi1, hi2) - max(lo1, lo2) > 0:
                found.append(f"{a}->{b} shares a segment with {c}->{d}")
    return found


problems = []
for p, q, a, b in SEGS:
    for k, box in BOX.items():
        if k not in (a, b) and seg_hits_box(p, q, box):
            problems.append(f"line {a}->{b} crosses {k}")
keys = list(BOX)
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        if boxes_overlap(BOX[keys[i]], BOX[keys[j]]):
            problems.append(f"label overlap {keys[i]} / {keys[j]}")
for cx, cy, n in BADGES:
    bb = (cx - 12, cy - 12, cx + 12, cy + 12)
    for p, q, a, b in SEGS:
        if seg_hits_box(p, q, bb, pad=1):
            problems.append(f"badge {n} sits on line {a}->{b}")
    for k, box in BOX.items():
        if boxes_overlap(bb, box):
            problems.append(f"badge {n} overlaps {k}")
for k, (x0, y0, x1, y1) in BOX.items():
    for (c0, c1) in COLS:
        if c0 < (x0 + x1) / 2 < c1 and (x0 < c0 + 4 or x1 > c1 - 4):
            problems.append(f"label of {k} touches its group border")
problems += shared_segments()
X = crossings()
if X:
    problems.append(f"{len(X)} line crossings")

svg = "\n".join(out)
assert "\u2014" not in svg and "\u2013" not in svg, "em or en dash found"
with open(OUT_SVG, "w") as fh:
    fh.write(svg)
subprocess.run(["rsvg-convert", "-z", str(ZOOM), "-o", OUT_PNG, OUT_SVG], check=True)
print("nodes:", len(N), "segments:", len(SEGS), "badges:", len(BADGES))
print("crossings:", len(X), *X)
print("layout problems:", problems if problems else "none")
print("wrote", OUT_SVG, "and", OUT_PNG)
