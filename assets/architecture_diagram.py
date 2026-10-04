"""Build the Data Science Set data-flow diagram (SVG + PNG).

Hand-built SVG on an aligned grid, rendered to PNG with rsvg-convert.
Style follows the architecture standard (white canvas, no fills, dashed
unfilled groups, orthogonal solid lines with filled arrowheads), adapted to a
left-to-right data flow. Real logos are used only where a legitimate one ships
with the `diagrams` package (Python, Ubuntu); every other tool is a
labeled box. Stages per lane come from notes.md (verified against the repo).
No branding, hosts, credentials, or personal data appear in the output.
"""
import base64
import subprocess
import sys
from html import escape
from pathlib import Path

import diagrams

HERE = Path(__file__).resolve().parent
SVG_OUT = HERE / "architecture.svg"
PNG_OUT = HERE / "architecture.png"
RSVG = "/opt/homebrew/bin/rsvg-convert"
RES = Path(diagrams.__file__).resolve().parent.parent / "resources"
LOGOS = {
    "python": RES / "programming/language/python.png",
    "ubuntu": RES / "generic/os/ubuntu.png",
}

# Canvas and grid
W = 1440
FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"
INK, BODY, MUTED, GROUP = "#232F3E", "#545B64", "#7D8998", "#7D8998"
LINE = "#3F4752"
STAGES = ["Sources", "Ingest / Collect", "Wrangle / Clean", "Store / Query",
          "Analyze / Visualize", "Model / Predict"]
LANE_X, LANE_W = 20, W - 40
LABEL_X, LABEL_W = 34, 128          # lane title column inside the lane
COL_X0, COL_W, BOX_W = 176, 210, 184
TOP = 132                            # top of first lane
LANE_GAP = 18
BOX_PAD = 16                         # box inset from lane top and bottom
LOGO = 22

# Each lane: title, {stage_index: (title, [lines], [logos])}
LANES = [
    ("01 Creating & Processing Data Pipeline", {
        0: ("NYC taxi CSV", ["sample trip data", "read by Directory origin"], []),
        1: ("StreamSets", ["Data Collector 3.22.3", "in an Ubuntu VM", "on VMware Workstation"], ["ubuntu"]),
        2: ("Pipeline stages", ["Stream Selector (card)", "Jython + Field Masker", "type and field converters"], []),
        3: ("Local FS", ["masked out_ files", "non-card rows to Trash"], []),
    }),
    ("02 Data Science Collection", {
        0: ("APIs, web, CSVs", ["SpaceX API, Wikipedia", "yfinance, stock pages", "course datasets"], []),
        1: ("Collect", ["requests, BeautifulSoup", "pandas.read_html", "yfinance"], ["python"]),
        2: ("pandas", ["clean and reshape", "DataFrames to CSV"], ["python"]),
        3: ("IBM Db2 on Cloud", ["SQL EDA with %sql", "(SpaceX notebooks)"], []),
        4: ("Charts, dashboards", ["seaborn, matplotlib", "Plotly, Folium map", "Dash: SpaceX, Airline"], []),
        5: ("scikit-learn", ["landing classifiers", "house price regression"], []),
    }),
    ("03 SpaceX Falcon-9", {
        0: ("SpaceX REST API v4", ["Wikipedia Falcon 9", "launch tables"], []),
        1: ("Collect", ["requests, BeautifulSoup", "dataset_part_1.csv", "spacex_web_scraped.csv"], ["python"]),
        2: ("Wrangle (pandas)", ["Class landing label", "one-hot features", "dataset_part_2/3.csv"], ["python"]),
        3: ("IBM Db2 on Cloud", ["SQL EDA queries"], []),
        4: ("Visualize", ["seaborn, matplotlib", "Folium launch-site map", "Plotly Dash dashboard"], []),
        5: ("Predict landing", ["LogReg, SVM, Tree, KNN", "tuned with GridSearchCV"], []),
    }),
]

problems = []


def text_w(s, size, bold=False):
    """Conservative width estimate for Helvetica."""
    return len(s) * size * (0.60 if bold else 0.55)


def wrap(title, limit=14):
    lines, cur = [], ""
    for w_ in title.split(" "):
        if cur and len(cur) + 1 + len(w_) > limit:
            lines.append(cur)
            cur = w_
        else:
            cur = (cur + " " + w_).strip()
    return lines + [cur]


def inside(inner, outer):
    x, y, w, h = inner
    ox, oy, ow, oh = outer
    return x >= ox and y >= oy and x + w <= ox + ow and y + h <= oy + oh


def overlap(a, b):
    return not (a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0] or a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1])


def href(name):
    return "data:image/png;base64," + base64.b64encode(LOGOS[name].read_bytes()).decode()


def box(x, y, h, title, lines, logos, texts):
    out = [f'<rect x="{x}" y="{y}" width="{BOX_W}" height="{h}" fill="none" stroke="{INK}" stroke-width="1.3"/>']
    rect = (x, y, BOX_W, h)
    logo_w = len(logos) * (LOGO + 4)
    for i, name in enumerate(logos):
        lx = x + BOX_W - 8 - (len(logos) - i) * (LOGO + 4) + 4
        out.append(f'<image x="{lx}" y="{y + 8}" width="{LOGO}" height="{LOGO}" href="{href(name)}"/>')
    tb = (x + 10, y + 10, text_w(title, 14, True), 16)
    if tb[2] > BOX_W - 20 - logo_w:
        problems.append(f"title too wide: {title}")
    texts.append(tb)
    out.append(f'<text x="{x + 10}" y="{y + 24}" class="bt">{escape(title)}</text>')
    for i, ln in enumerate(lines):
        ty = y + 46 + i * 17
        lb = (x + 10, ty - 12, text_w(ln, 12), 15)
        if not inside(lb, (x + 1, y + 1, BOX_W - 2, h - 2)):
            problems.append(f"line clipped: {ln}")
        texts.append(lb)
        out.append(f'<text x="{x + 10}" y="{ty}" class="bl">{escape(ln)}</text>')
    return out, rect


def build():
    max_lines = max(len(v[1]) for _, st in LANES for v in st.values())
    box_h = 46 + (max_lines - 1) * 17 + 14
    lane_h = box_h + 2 * BOX_PAD
    legend_y = TOP + len(LANES) * (lane_h + LANE_GAP) + 10
    height = legend_y + 40

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}">',
         f'<style>text{{font-family:{FONT};fill:{INK}}}'
         '.t{font-size:26px;font-weight:700}'
         f'.st{{font-size:14px;fill:{BODY}}}'
         f'.h{{font-size:13px;font-weight:700;fill:{BODY};letter-spacing:0.3px}}'
         '.lt{font-size:14.5px;font-weight:700}'
         '.bt{font-size:14px;font-weight:700}'
         f'.bl{{font-size:12px;fill:{BODY}}}</style>',
         f'<defs><marker id="a" markerWidth="9" markerHeight="8" refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse">'
         f'<path d="M0,0 L9,4 L0,8 z" fill="{LINE}"/></marker></defs>',
         '<text x="20" y="44" class="t">Data Science Set: how data flows through the 3 projects</text>',
         '<text x="20" y="70" class="st">Read each lane left to right: where the data comes from, how it is collected and cleaned, '
         'where it is stored or queried, and how it is visualized and modeled.</text>']

    texts, boxes, segs = [], [], []
    for i, name in enumerate(STAGES):
        cx = COL_X0 + i * COL_W + BOX_W / 2
        texts.append((cx - text_w(name, 13, True) / 2, TOP - 30, text_w(name, 13, True), 16))
        s.append(f'<text x="{cx}" y="{TOP - 16}" text-anchor="middle" class="h">{escape(name)}</text>')

    y = TOP
    for title, stages in LANES:
        lane = (LANE_X, y, LANE_W, lane_h)
        s.append(f'<rect x="{LANE_X}" y="{y}" width="{LANE_W}" height="{lane_h}" fill="none" '
                 f'stroke="{GROUP}" stroke-width="1.3" stroke-dasharray="5 4"/>')
        lines = wrap(title)
        for j, ln in enumerate(lines):
            ty = y + 30 + j * 19
            tb = (LABEL_X, ty - 13, text_w(ln, 14.5, True), 17)
            if tb[2] > LABEL_W or not inside(tb, lane):
                problems.append(f"lane title clipped: {ln}")
            texts.append(tb)
            s.append(f'<text x="{LABEL_X}" y="{ty}" class="lt">{escape(ln)}</text>')
        by = y + BOX_PAD
        idx = sorted(stages)
        for k in idx:
            out, rect = box(COL_X0 + k * COL_W, by, box_h, *stages[k], texts)
            if not inside(rect, lane):
                problems.append(f"box outside lane: {stages[k][0]}")
            boxes.append(rect)
            s += out
        for a, b in zip(idx, idx[1:]):
            x1 = COL_X0 + a * COL_W + BOX_W
            x2 = COL_X0 + b * COL_W
            ly = by + box_h / 2
            segs.append((x1, ly, x2, ly))
            s.append(f'<line x1="{x1}" y1="{ly}" x2="{x2}" y2="{ly}" stroke="{LINE}" stroke-width="1.6" marker-end="url(#a)"/>')
        y += lane_h + LANE_GAP

    # Key below the lanes
    ky = legend_y + 10
    s.append(f'<line x1="20" y1="{ky}" x2="60" y2="{ky}" stroke="{LINE}" stroke-width="1.6" marker-end="url(#a)"/>')
    s.append(f'<text x="70" y="{ky + 5}" class="st">Data flows to the next stage</text>')
    s.append(f'<image x="320" y="{ky - 11}" width="{LOGO}" height="{LOGO}" href="{href("python")}"/>')
    s.append(f'<text x="350" y="{ky + 5}" class="st">Python step. The Ubuntu logo marks the pipeline VM. '
             'Other tools are labeled boxes.</text>')
    s.append("</svg>")

    # Layout checks
    for i, a in enumerate(boxes):
        if a[0] + a[2] > W - 20 or a[1] + a[3] > height:
            problems.append("box clipped by canvas")
        for b in boxes[i + 1:]:
            if overlap(a, b):
                problems.append("boxes overlap")
    for x1, y1, x2, y2 in segs:
        if x1 != x2 and y1 != y2:
            problems.append("non-orthogonal line")
        seg_box = (min(x1, x2), min(y1, y2) - 1, abs(x2 - x1), abs(y2 - y1) + 2)
        if x2 - x1 < 20:
            problems.append("line too short for arrowhead")
        for t in texts:
            if overlap(seg_box, t):
                problems.append("line through label")
        for b in boxes:
            if overlap((seg_box[0] + 1, seg_box[1], seg_box[2] - 2, seg_box[3]), b):
                problems.append("line through box")
    crossings = 0
    for i, (ax1, ay1, ax2, ay2) in enumerate(segs):
        for bx1, by1, bx2, by2 in segs[i + 1:]:
            if ay1 == by1 and max(ax1, bx1) < min(ax2, bx2):
                problems.append("shared segment")

    svg = "\n".join(s)
    for bad in ("\u2014", "\u2013"):
        assert bad not in svg, "em or en dash in output"
    SVG_OUT.write_text(svg, encoding="utf-8")
    subprocess.run([RSVG, "-w", str(W), "-o", str(PNG_OUT), str(SVG_OUT)], check=True)
    print(f"layout problems: {', '.join(problems) if problems else 'none'}")
    print(f"crossings: {crossings}")
    return not problems


if __name__ == "__main__":
    ok = build()
    print(SVG_OUT)
    print(PNG_OUT)
    sys.exit(0 if ok else 1)
