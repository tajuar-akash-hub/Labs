#!/usr/bin/env python3
"""Build the Lab 5.1 architecture diagram as draw.io XML and SVG."""

from pathlib import Path
import base64
import html
import xml.dom.minidom as minidom

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parent / "lab 5.1"
DRAWIO = ROOT / "lab-5-1-architecture.drawio"
SVG = LAB / "assets" / "lab-5-1-architecture.svg"

P = {
    "canvas": "#FFFFFF",
    "ink": "#1F2937",
    "muted": "#6B7280",
    "frame": "#7C8BA1",
    "zone_fill": "#F2F5FA",
    "zone_edge": "#C9D3E2",
    "primary": "#2F4AA6",
    "accent": "#0E7C95",
    "paper": "#FFFFFF",
    "on_primary": "#FFFFFF",
    "on_primary_sub": "#E8EDF7",
}

ICONS = {
    "database": (
        '<ellipse cx="12" cy="5" rx="8" ry="3"/>'
        '<path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/>'
        '<path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>'
    ),
    "doc": (
        '<path d="M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/>'
        '<polyline points="14,2 14,8 19,8"/>'
    ),
    "terminal": (
        '<rect x="3" y="4" width="18" height="16" rx="3"/>'
        '<polyline points="7,10 10,13 7,16"/>'
        '<line x1="12" y1="16" x2="17" y2="16"/>'
    ),
}


def icon_uri(name, color):
    inner = ICONS[name]
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round">{inner}</svg>'
    )
    return "data:image/svg+xml," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


def chevron_uri(color):
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
        '<circle cx="12" cy="12" r="10" fill="#FFFFFF"/>'
        f'<path d="M9 6 L15 12 L9 18" fill="none" stroke="{color}" '
        'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
        '</svg>'
    )
    return "data:image/svg+xml," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


def esc(text):
    return html.escape(text, quote=False)


def value_html(lines, sub=None, sub_color=None):
    value = "<b>" + "<br>".join(esc(line) for line in lines) + "</b>"
    if sub:
        value += (
            f"<br><font style='font-size:16px' color='{sub_color}'>{esc(sub)}</font>"
        )
    return value


BLOCKS = [
    dict(id="raw", x=70, y=175, w=270, h=100, fill="paper", stroke="frame",
         text="ink", lines=["customers_raw.csv"], sub="raw customer data",
         sub_color="muted", icon="database", icon_color="primary"),
    dict(id="rules", x=70, y=315, w=270, h=100, fill="paper", stroke="frame",
         text="ink", lines=["quality_rules.yaml"], sub="the rulebook",
         sub_color="muted", icon="doc", icon_color="primary"),
    dict(id="audit", x=420, y=220, w=300, h=140, fill="primary", stroke="primary",
         text="on_primary", lines=["data_quality_audit.py"], sub="audit engine",
         sub_color="on_primary_sub", icon="terminal", icon_color="on_primary"),
    dict(id="report", x=1230, y=165, w=290, h=100, fill="paper", stroke="frame",
         text="ink", lines=["reports/", "quality_report.csv"],
         sub="dimension scorecard", sub_color="muted", icon="doc",
         icon_color="primary"),
    dict(id="issues", x=1230, y=335, w=290, h=100, fill="paper", stroke="frame",
         text="ink", lines=["reports/", "row_issues.csv"], sub="flagged rows",
         sub_color="muted", icon="doc", icon_color="primary"),
    dict(id="clean", x=1230, y=540, w=290, h=85, fill="accent", stroke="accent",
         text="on_primary", lines=["clean_data.py"], sub=None, icon="terminal",
         icon_color="on_primary"),
    dict(id="cleancsv", x=1230, y=655, w=290, h=85, fill="paper", stroke="frame",
         text="ink", lines=["customers_clean.csv"], sub=None, icon="database",
         icon_color="primary"),
]

DIMENSIONS = [
    "Completeness", "Uniqueness", "Validity",
    "Accuracy", "Consistency", "Timeliness",
]

EDGES = [
    dict(id="e_read", src="raw", tgt="audit", label="read rows",
         points=[(340, 225), (380, 225), (380, 270.4), (420, 270.4)],
         exit=(1, 0.5), entry=(0, 0.36), dashed=False,
         label_at=(380, 211), mid=(380, 247.7), mid_dir="down"),
    dict(id="e_apply", src="rules", tgt="audit", label="apply",
         points=[(340, 365), (380, 365), (380, 320.8), (420, 320.8)],
         exit=(1, 0.5), entry=(0, 0.72), dashed=False,
         label_at=(382, 351), mid=(380, 330), mid_dir="up"),
    dict(id="e_evaluate", src="audit", tgt="dims", label="evaluate",
         points=[(720, 290), (760, 290), (760, 360), (800, 360)],
         exit=(1, 0.5), entry=(0, 0.5), dashed=False,
         label_at=(760, 276), mid=(760, 325), mid_dir="down"),
    dict(id="e_scorecard", src="dims", tgt="report", label="scorecard",
         points=[(1140, 215), (1230, 215)],
         exit=(1, (215 - 145) / 430), entry=(0, 0.5), dashed=False,
         label_at=(1185, 197), mid=(1185, 215), mid_dir="right"),
    dict(id="e_flagged", src="dims", tgt="issues", label="row issues",
         points=[(1140, 385), (1230, 385)],
         exit=(1, (385 - 145) / 430), entry=(0, 0.5), dashed=False,
         label_at=(1187, 367), mid=(1185, 385), mid_dir="right"),
    dict(id="e_fix", src="issues", tgt="clean", label="fix flagged rows",
         points=[(1375, 435), (1375, 540)],
         exit=(0.5, 1), entry=(0.5, 0), dashed=False,
         label_at=(1390, 475), anchor="start", mid=(1375, 487.5), mid_dir="down"),
    dict(id="e_repair", src="clean", tgt="cleancsv", label="repair",
         points=[(1375, 625), (1375, 655)],
         exit=(0.5, 1), entry=(0.5, 0), dashed=False,
         label_at=(1390, 640), anchor="start", mid=(1375, 640), mid_dir="down"),
    dict(id="e_reaudit", src="cleancsv", tgt="dims", label="re-audit",
         points=[(1230, 697.5), (970, 697.5), (970, 575)],
         exit=(0, 0.5), entry=((970 - 800) / 340, 1), dashed=True,
         label_at=(1060, 681), mid=(970, 636), mid_dir="up"),
]


def drawio_vertex(cid, value, style, x, y, w, h):
    return (
        f'<mxCell id="{cid}" value="{esc(value)}" style="{style}" '
        f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" '
        f'width="{w}" height="{h}" as="geometry"/></mxCell>'
    )


def drawio_text(cid, value, x, y, w, h, size, bold, color):
    style = (
        "text;html=1;fillColor=none;strokeColor=none;align=left;"
        "verticalAlign=middle;fontFamily=Helvetica;"
        f"fontSize={size};fontStyle={bold};fontColor={color};"
    )
    return drawio_vertex(cid, value, style, x, y, w, h)


def drawio_zone(cid, x, y, w, h):
    style = (
        "rounded=1;absoluteArcSize=1;arcSize=14;"
        f"fillColor={P['zone_fill']};strokeColor={P['zone_edge']};"
        "strokeWidth=1.5;dashed=1;dashPattern=8 6;"
    )
    return drawio_vertex(cid, "", style, x, y, w, h)


def drawio_block(b):
    chip = "align=center;verticalAlign=middle;spacingLeft=12;spacingRight=12;"
    regular = "align=left;verticalAlign=middle;spacingLeft=52;spacingRight=16;"
    style = (
        f"rounded=1;absoluteArcSize=1;arcSize=12;"
        f"fillColor={P[b['fill']]};strokeColor={P[b['stroke']]};strokeWidth=1.5;"
        "fontFamily=Helvetica;fontSize=20;fontStyle=1;"
        f"fontColor={P[b['text']]};{chip if b.get('chip') else regular}"
        "html=1;whiteSpace=wrap;"
    )
    if b.get("chip"):
        value = b["lines"][0]
    else:
        value = value_html(b["lines"], b.get("sub"), P.get(b.get("sub_color", "muted")))
    cells = [drawio_vertex(b["id"], value, style, b["x"], b["y"], b["w"], b["h"])]
    if b.get("icon"):
        cells.append(
            f'<mxCell id="{b["id"]}_icon" style="shape=image;aspect=fixed;'
            f'imageAspect=1;image={icon_uri(b["icon"], P[b["icon_color"]])};" '
            f'vertex="1" parent="{b["id"]}"><mxGeometry x="16" y="16" '
            'width="32" height="32" as="geometry"/></mxCell>'
        )
    return cells


def drawio_edge(e):
    style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;"
        f"strokeColor={P['ink']};strokeWidth=1.5;"
        "endArrow=block;endFill=1;startArrow=oval;startFill=0;"
        "startSize=8;endSize=8;jettySize=auto;"
        f"exitX={e['exit'][0]};exitY={e['exit'][1]};exitDx=0;exitDy=0;"
        f"entryX={e['entry'][0]};entryY={e['entry'][1]};entryDx=0;entryDy=0;"
        + ("dashed=1;dashPattern=8 6;" if e["dashed"] else "")
    )
    cells = [
        f'<mxCell id="{e["id"]}" edge="1" parent="1" source="{e["src"]}" '
        f'target="{e["tgt"]}" style="{style}"><mxGeometry relative="1" '
        'as="geometry"/></mxCell>'
    ]
    if e["label"]:
        lx, ly = e["label_at"]
        anchor = e.get("anchor", "middle")
        width = 180
        height = 24
        x = lx if anchor == "start" else lx - width / 2
        align = "left" if anchor == "start" else "center"
        label_style = (
            "text;html=1;fillColor=none;strokeColor=none;"
            f"align={align};verticalAlign=middle;fontFamily=Helvetica;"
            "fontSize=17;fontStyle=1;fontColor=#1F2937;"
        )
        cells.append(
            f'<mxCell id="{e["id"]}_label" value="{esc(e["label"])}" '
            f'style="{label_style}" vertex="1" connectable="0" parent="1">'
            f'<mxGeometry x="{x}" y="{ly - height / 2}" width="{width}" '
            f'height="{height}" as="geometry"/></mxCell>'
        )
    if e.get("mid"):
        mx, my = e["mid"]
        rotation = {"right": 0, "down": 90, "left": 180, "up": 270}[e["mid_dir"]]
        cells.append(
            f'<mxCell id="{e["id"]}_flow" style="shape=image;aspect=fixed;'
            f'imageAspect=1;image={chevron_uri(P["ink"])};rotation={rotation};" '
            f'vertex="1" parent="1"><mxGeometry x="{mx - 8}" y="{my - 8}" '
            'width="16" height="16" as="geometry"/></mxCell>'
        )
    return cells


def build_drawio():
    cells = [
        '<mxCell id="0" />',
        '<mxCell id="1" parent="0" />',
        drawio_vertex(
            "frame", "",
            "rounded=1;absoluteArcSize=1;arcSize=20;"
            f"fillColor={P['paper']};strokeColor={P['frame']};strokeWidth=2;",
            20, 20, 1560, 860,
        ),
        drawio_zone("vm", 50, 50, 1500, 800),
        drawio_text(
            "vm_label", "Poridhi Lab VM: ~/poridhi-lab-5-1",
            70, 36, 560, 28, 18, 1, P["ink"],
        ),
        drawio_zone("dims", 800, 145, 340, 430),
        drawio_text(
            "dims_label", "Six quality dimensions",
            820, 131, 300, 28, 18, 1, P["ink"],
        ),
        drawio_zone("rem", 1200, 505, 320, 250),
        drawio_text(
            "rem_label", "Remediation loop",
            1210, 491, 240, 28, 18, 1, P["ink"],
        ),
    ]

    for b in BLOCKS:
        cells.extend(drawio_block(b))

    for index, name in enumerate(DIMENSIONS):
        cells.extend(drawio_block(dict(
            id=f"dim{index}", x=820, y=187 + index * 60, w=300, h=48,
            fill="paper", stroke="primary", text="ink", lines=[name],
            sub=None, chip=True,
        )))

    for e in EDGES:
        cells.extend(drawio_edge(e))

    body = "\n        ".join(cells)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<mxfile host="app.diagrams.net" type="device">\n'
        '  <diagram id="lab51" name="Lab 5.1 architecture">\n'
        '    <mxGraphModel dx="1600" dy="900" grid="0" gridSize="10" '
        'guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" '
        'pageScale="1" pageWidth="1600" pageHeight="900" background="#FFFFFF" '
        'math="0" shadow="0">\n'
        '      <root>\n'
        f'        {body}\n'
        '      </root>\n'
        '    </mxGraphModel>\n'
        '  </diagram>\n'
        '</mxfile>\n'
    )


def orth_path(points, radius=6):
    if len(points) == 2:
        (x1, y1), (x2, y2) = points
        return f"M {x1},{y1} L {x2},{y2}"
    parts = [f"M {points[0][0]},{points[0][1]}"]
    for i in range(1, len(points) - 1):
        px, py = points[i - 1]
        cx, cy = points[i]
        nx, ny = points[i + 1]
        v1 = (cx - px, cy - py)
        v2 = (nx - cx, ny - cy)
        l1 = max((v1[0] ** 2 + v1[1] ** 2) ** 0.5, 0.001)
        l2 = max((v2[0] ** 2 + v2[1] ** 2) ** 0.5, 0.001)
        r = min(radius, l1 / 2, l2 / 2)
        ax = cx - v1[0] / l1 * r
        ay = cy - v1[1] / l1 * r
        bx = cx + v2[0] / l2 * r
        by = cy + v2[1] / l2 * r
        parts.append(f"L {ax:.2f},{ay:.2f}")
        parts.append(f"Q {cx},{cy} {bx:.2f},{by:.2f}")
    parts.append(f"L {points[-1][0]},{points[-1][1]}")
    return " ".join(parts)


def svg_text(x, y, text, size, color, weight="400", anchor="start"):
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
        f'fill="{color}" text-anchor="{anchor}" dominant-baseline="central">'
        f'{esc(text)}</text>'
    )


def svg_halo_text(x, y, text, size, color, weight="400", anchor="middle"):
    halo = (
        f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
        'fill="#FFFFFF" stroke="#FFFFFF" stroke-width="4" stroke-linejoin="round" '
        f'text-anchor="{anchor}" dominant-baseline="central">{esc(text)}</text>'
    )
    main = svg_text(x, y, text, size, color, weight, anchor)
    return [halo, main]


def svg_icon(name, x, y, size, color):
    scale = size / 24
    return (
        f'<g transform="translate({x},{y}) scale({scale:.4f})" fill="none" '
        f'stroke="{color}" stroke-width="{2 / scale:.3f}" stroke-linecap="round" '
        f'stroke-linejoin="round">{ICONS[name]}</g>'
    )


def svg_rect(x, y, w, h, fill, stroke, sw, rx, dashed=False):
    dash = ' stroke-dasharray="8 6"' if dashed else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}/>'
    )


def svg_block(b):
    chip = b.get("chip")
    out = [svg_rect(
        b["x"], b["y"], b["w"], b["h"], P[b["fill"]], P[b["stroke"]], 1.5,
        12,
    )]
    if b.get("icon"):
        out.append(svg_icon(b["icon"], b["x"] + 16, b["y"] + 16, 32, P[b["icon_color"]]))
    if chip:
        out.append(svg_text(
            b["x"] + b["w"] / 2, b["y"] + b["h"] / 2, b["lines"][0], 20,
            P[b["text"]], "700", "middle",
        ))
        return out
    lines = [(line, 20, P[b["text"]], "700") for line in b["lines"]]
    if b.get("sub"):
        lines.append((b["sub"], 16, P[b["sub_color"]], "400"))
    heights = [24 if size >= 20 else 20 for (_, size, _, _) in lines]
    total = sum(heights)
    cursor = b["y"] + b["h"] / 2 - total / 2
    for (text, size, color, weight), line_height in zip(lines, heights):
        out.append(svg_text(
            b["x"] + 52, cursor + line_height / 2, text, size, color, weight,
        ))
        cursor += line_height
    return out


def build_svg():
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" '
        'viewBox="0 0 1600 900" role="img" aria-labelledby="diagram-title '
        'diagram-desc" font-family="Helvetica, Arial, sans-serif">',
        '<title id="diagram-title">Data Quality Fundamentals architecture</title>',
        '<desc id="diagram-desc">Customer data and the quality rulebook flow into '
        'the audit engine, which evaluates six quality dimensions and writes a '
        'scorecard and flagged rows. clean_data.py repairs the rows, and the clean '
        'dataset is re-audited by the same engine.</desc>',
        '<defs>',
        '<marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" '
        'markerWidth="8" markerHeight="8" orient="auto" '
        'markerUnits="userSpaceOnUse"><path d="M0,0 L10,5 L0,10 z" '
        f'fill="{P["ink"]}"/></marker>',
        '</defs>',
        svg_rect(0, 0, 1600, 900, P["canvas"], "none", 0, 0),
    ]

    out.append(svg_rect(20, 20, 1560, 860, P["paper"], P["frame"], 2, 20))

    out.append(svg_rect(50, 50, 1500, 800, P["zone_fill"], P["zone_edge"], 1.5, 14, True))
    out.extend(svg_halo_text(70, 50, "Poridhi Lab VM: ~/poridhi-lab-5-1", 18, P["ink"], "700", "start"))

    out.append(svg_rect(800, 145, 340, 430, P["zone_fill"], P["zone_edge"], 1.5, 14, True))
    out.extend(svg_halo_text(820, 145, "Six quality dimensions", 18, P["ink"], "700", "start"))

    out.append(svg_rect(1200, 505, 320, 250, P["zone_fill"], P["zone_edge"], 1.5, 14, True))
    out.extend(svg_halo_text(1210, 505, "Remediation loop", 18, P["ink"], "700", "start"))

    for b in BLOCKS:
        out.extend(svg_block(b))
    for index, name in enumerate(DIMENSIONS):
        out.extend(svg_block(dict(
            id=f"dim{index}", x=820, y=187 + index * 60, w=300, h=48,
            fill="paper", stroke="primary", text="ink", lines=[name],
            sub=None, chip=True,
        )))

    for e in EDGES:
        dash = ' stroke-dasharray="8 6"' if e["dashed"] else ""
        out.append(
            f'<path d="{orth_path(e["points"])}" fill="none" stroke="{P["ink"]}" '
            f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"'
            f'{dash} marker-end="url(#arrow)"/>'
        )
        sx, sy = e["points"][0]
        out.append(
            f'<circle cx="{sx}" cy="{sy}" r="3" fill="#FFFFFF" '
            f'stroke="{P["ink"]}" stroke-width="1.5"/>'
        )

    for e in EDGES:
        if e.get("mid"):
            mx, my = e["mid"]
            angle = {"right": 0, "down": 90, "left": 180, "up": 270}[e["mid_dir"]]
            out.append(
                f'<g transform="translate({mx},{my})">'
                '<circle r="7" fill="#FFFFFF"/>'
                f'<path d="M-3,-4 L3,0 L-3,4" fill="none" stroke="{P["ink"]}" '
                'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
                f'transform="rotate({angle})"/></g>'
            )

    for e in EDGES:
        out.append(
            f'<circle r="3.5" fill="{P["ink"]}" stroke="#FFFFFF" stroke-width="2">'
            f'<animateMotion dur="2.4s" repeatCount="indefinite" '
            f'path="{orth_path(e["points"])}"/></circle>'
        )

    for e in EDGES:
        lx, ly = e["label_at"]
        out.extend(svg_halo_text(
            lx, ly, e["label"], 17, P["ink"], "700", e.get("anchor", "middle"),
        ))

    out.append("</svg>")
    return "\n".join(out)


def main():
    xml = build_drawio()
    pretty = minidom.parseString(xml).toprettyxml(indent="  ")
    pretty = pretty.replace(
        '<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>', 1
    )
    pretty = "\n".join(line for line in pretty.splitlines() if line.strip()) + "\n"
    DRAWIO.write_text(pretty, encoding="utf-8", newline="\n")
    SVG.parent.mkdir(parents=True, exist_ok=True)
    SVG.write_text(build_svg(), encoding="utf-8", newline="\n")
    print(f"wrote {DRAWIO}")
    print(f"wrote {SVG}")


if __name__ == "__main__":
    main()
