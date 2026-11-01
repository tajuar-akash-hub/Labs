import base64
import xml.etree.ElementTree as ET

ICONS = {
  "user":     '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-7 8-7s8 3 8 7"/>',
  "browser":  '<rect x="3" y="4" width="18" height="16" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><circle cx="7" cy="6.5" r="0.6"/><circle cx="9.5" cy="6.5" r="0.6"/>',
  "terminal": '<rect x="3" y="4" width="18" height="16" rx="3"/><polyline points="7,10 10,13 7,16"/><line x1="12" y1="16" x2="17" y2="16"/>',
  "server":   '<rect x="3" y="4" width="18" height="6" rx="1"/><rect x="3" y="14" width="18" height="6" rx="1"/><circle cx="7" cy="7" r="0.6"/><circle cx="7" cy="17" r="0.6"/>',
  "database": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
  "bucket":   '<path d="M4 8h16l-1.5 11a2 2 0 0 1-2 1.7H7.5a2 2 0 0 1-2-1.7z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
  "queue":    '<rect x="3" y="9" width="18" height="6" rx="1"/><line x1="7" y1="12" x2="2" y2="12"/><line x1="22" y1="12" x2="17" y2="12"/>',
  "lambda":   '<path d="M5 19l5-14h4l5 14"/><line x1="8" y1="14" x2="16" y2="14"/>',
  "lock":     '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
  "cloud":    '<path d="M7 18a4 4 0 0 1-1-7.9A6 6 0 0 1 18 9.5a4 4 0 0 1-1 7.5z"/>',
  "doc":      '<path d="M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 19,8"/>',
}

def icon_uri(name, color="#FFFFFF"):
    inner = ICONS[name]
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
           'fill="none" stroke="%s" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round">%s</svg>') % (color, inner)
    return "data:image/svg+xml," + base64.b64encode(svg.encode()).decode()

cells = []
_counter = [0]
def nid(prefix):
    _counter[0] += 1
    return "%s%d" % (prefix, _counter[0])

def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))

def add_cell(cid, value, style, x, y, w, h, parent="1", vertex=True, extra=""):
    cells.append((cid, value, style, x, y, w, h, parent, vertex, extra))

def block(cid, x, y, w, h, label, sublabel, kind, icon):
    """kind: primary | accent | paper | emphasis"""
    if kind == "primary":
        base = "rounded=1;arcSize=12;fillColor=#2F4AA6;strokeColor=#2F4AA6;fontFamily=Helvetica;fontSize=20;fontStyle=1;fontColor=#FFFFFF;"
        sub_color = "#FFFFFF"
        icon_color = "#FFFFFF"
    elif kind == "accent":
        base = "rounded=1;arcSize=12;fillColor=#0E7C95;strokeColor=#0E7C95;fontFamily=Helvetica;fontSize=20;fontStyle=1;fontColor=#FFFFFF;"
        sub_color = "#FFFFFF"
        icon_color = "#FFFFFF"
    elif kind == "emphasis":
        base = "rounded=1;arcSize=12;fillColor=#FFFFFF;strokeColor=#2F4AA6;strokeWidth=2;fontFamily=Helvetica;fontSize=20;fontStyle=1;fontColor=#1F2937;"
        sub_color = "#6B7280"
        icon_color = "#2F4AA6"
    else:  # paper
        base = "rounded=1;arcSize=12;fillColor=#FFFFFF;strokeColor=#7C8BA1;strokeWidth=1.5;fontFamily=Helvetica;fontSize=20;fontStyle=1;fontColor=#1F2937;"
        sub_color = "#6B7280"
        icon_color = "#2F4AA6"

    html = ('<div style="text-align:left;"><div style="font-family:Helvetica;font-size:20px;font-weight:bold;color:%s;">%s</div>'
            '<div style="font-family:Helvetica;font-size:16px;font-weight:normal;color:%s;margin-top:6px;">%s</div></div>'
            % (("#FFFFFF" if kind in ("primary", "accent") else "#1F2937"), esc(label),
               sub_color, esc(sublabel)))
    style = base + "verticalAlign=top;align=left;spacingLeft=14;spacingTop=12;spacingRight=12;" + "html=1;whiteSpace=wrap;"
    add_cell(cid, html, style, x, y, w, h)

    # icon inside block, top-left with margin
    add_cell(cid + "_icon", "", "shape=image;aspect=fixed;imageAspect=1;image=%s;" % icon_uri(icon, icon_color),
             x + 16, y + 14, 32, 32)

def zone(cid, x, y, w, h, label):
    style = "rounded=1;arcSize=4;fillColor=#F2F5FA;strokeColor=#C9D3E2;strokeWidth=1.5;dashed=1;html=1;"
    add_cell(cid, "", style, x, y, w, h)
    add_cell(cid + "_label", esc(label),
             "fontFamily=Helvetica;fontSize=18;fontStyle=1;fillColor=none;strokeColor=none;fontColor=#1F2937;align=left;verticalAlign=middle;html=1;",
             x + 16, y - 14, 260, 28)

EDGE_BASE = "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#1F2937;strokeWidth=1.5;jettySize=auto;"
FLOW = EDGE_BASE + "endArrow=block;endFill=1;startArrow=oval;startFill=0;"
TWOWAY = EDGE_BASE + "endArrow=block;endFill=1;startArrow=block;startFill=1;"
DASH = EDGE_BASE + "endArrow=block;endFill=1;startArrow=oval;startFill=0;dashed=1;dashPattern=6 4;"

edges = []
def edge(eid, source, target, label, style=FLOW, points=None, dx=0.0, dy=-0.0):
    edges.append((eid, source, target, label, style, points, dx, dy))

def build_xml():
    out = []
    out.append('<mxfile host="app.diagrams.net">')
    out.append('  <diagram name="Lab 7.4 architecture">')
    out.append('    <mxGraphModel dx="1600" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1600" pageHeight="900" background="#FFFFFF" math="0" shadow="0">')
    out.append('      <root>')
    out.append('        <mxCell id="0" />')
    out.append('        <mxCell id="1" parent="0" />')

    # Outer frame
    out.append('        <mxCell id="frame" value="" style="rounded=1;arcSize=4;fillColor=#FFFFFF;strokeColor=#7C8BA1;strokeWidth=2;html=1;" vertex="1" parent="1">')
    out.append('          <mxGeometry x="20" y="20" width="1560" height="860" as="geometry" />')
    out.append('        </mxCell>')

    # Frame title
    out.append('        <mxCell id="frame_title" value="Lab 7.4: Streaming Ingestion" style="fontFamily=Helvetica;fontSize=28;fontStyle=1;fillColor=none;strokeColor=none;fontColor=#1F2937;align=left;verticalAlign=middle;html=1;" vertex="1" parent="1">')
    out.append('          <mxGeometry x="56" y="44" width="560" height="38" as="geometry" />')
    out.append('        </mxCell>')

    # Subtitle
    out.append('        <mxCell id="frame_sub" value="Push features directly to the online store with feast.push()" style="fontFamily=Helvetica;fontSize=18;fillColor=none;strokeColor=none;fontColor=#6B7280;align=left;verticalAlign=middle;html=1;" vertex="1" parent="1">')
    out.append('          <mxGeometry x="56" y="84" width="700" height="26" as="geometry" />')
    out.append('        </mxCell>')

    # Chip
    out.append('        <mxCell id="chip" value="Lab 7.4" style="rounded=1;arcSize=50;fillColor=#2F4AA6;strokeColor=none;fontFamily=Helvetica;fontSize=14;fontStyle=1;fontColor=#FFFFFF;align=center;verticalAlign=middle;html=1;" vertex="1" parent="1">')
    out.append('          <mxGeometry x="1430" y="52" width="100" height="28" as="geometry" />')
    out.append('        </mxCell>')

    for cid, value, style, x, y, w, h, parent, vertex, extra in cells:
        v = value if value else ""
        out.append('        <mxCell id="%s" value="%s" style="%s" vertex="1" parent="%s">' % (cid, esc(v), style, parent))
        out.append('          <mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry" />' % (x, y, w, h))
        out.append('        </mxCell>')

    for eid, source, target, label, style, points, dx, dy in edges:
        out.append('        <mxCell id="%s" value="%s" style="%s" edge="1" parent="1" source="%s" target="%s">' % (eid, esc(label), style, source, target))
        out.append('          <mxGeometry relative="1" as="geometry">')
        if points:
            out.append('            <Array as="points">')
            for px, py in points:
                out.append('              <mxPoint x="%d" y="%d" />' % (px, py))
            out.append('            </Array>')
        out.append('            <mxPoint x="0" y="0" as="offset" />')
        out.append('          </mxGeometry>')
        out.append('        </mxCell>')

    out.append('      </root>')
    out.append('    </mxGraphModel>')
    out.append('  </diagram>')
    out.append('</mxfile>')
    return "\n".join(out)

# ------------------------------------------------------------------ layout
# Zones
zone("z_producers", 70, 250, 300, 420, "Producers")
zone("z_vm", 430, 200, 560, 620, "Poridhi Lab VM")
zone("z_store", 1050, 330, 300, 280, "Online Store")

# Zone 1 blocks
block("python_producer", 95, 320, 250, 110,
      "Python Producer", "store.push() via SDK", "accent", "terminal")
block("http_client", 95, 480, 250, 110,
      "HTTP Client", "POST /push via curl", "accent", "terminal")

# Zone 2 blocks
block("feature_server", 470, 250, 220, 110,
      "Feast Feature Server", "port 6566", "primary", "server")
block("registry", 730, 250, 230, 110,
      "Feast Registry + Repo", "registry.db, feature_store.yaml", "paper", "doc")
block("featureview", 470, 430, 220, 110,
      "FeatureView: driver_stats_stream", "source = PushSource", "emphasis", "database")
block("pushsource", 730, 430, 230, 110,
      "PushSource: driver_stats_push", "batch_source = FileSource", "paper", "queue")
block("offline", 600, 630, 230, 110,
      "Offline Batch Source", "data/driver_stats.parquet", "paper", "bucket")

# Zone 3 blocks
block("redis", 1075, 400, 250, 110,
      "Poridhi Managed Redis", "hash per entity", "primary", "database")

# Outside zones
block("reader", 1370, 400, 180, 110,
      "Online Reader", "get_online_features()", "paper", "browser")

# ------------------------------------------------------------------ edges
edge("e1", "python_producer", "featureview", "push()", FLOW,
     points=[(400, 375), (400, 485)])
edge("e2", "http_client", "feature_server", "POST /push", FLOW,
     points=[(385, 535), (385, 305)])
edge("e3", "feature_server", "featureview", "push()", FLOW,
     points=[(580, 395)])
edge("e4", "pushsource", "offline", "OFFLINE mode", DASH,
     points=[(845, 560), (845, 685)])
edge("e5", "featureview", "redis", "ONLINE mode", FLOW,
     points=[(1030, 485), (1030, 455)])
edge("e6", "redis", "reader", "get_online_features()", TWOWAY)
edge("e7", "featureview", "registry", "definitions", DASH,
     points=[(715, 400), (715, 305)])

xml = build_xml()

# ------------------------------------------------------------------ validate
root = ET.fromstring(xml)
assert root.tag == "mxfile"
diag = root.find("diagram")
assert diag.get("name") == "Lab 7.4 architecture"
model = diag.find("mxGraphModel")
assert model.get("pageWidth") == "1600" and model.get("pageHeight") == "900"
assert model.get("background") == "#FFFFFF" and model.get("grid") == "0"
r = model.find("root")
ids = set()
for c in r.findall("mxCell"):
    ids.add(c.get("id"))
    if c.get("edge") == "1":
        assert c.get("source") in ids or c.get("source") in {
            "python_producer","http_client","feature_server","registry","featureview",
            "pushsource","offline","redis","reader"}, (c.get("id"), c.get("source"))
        assert c.get("target") in {
            "python_producer","http_client","feature_server","registry","featureview",
            "pushsource","offline","redis","reader"}, (c.get("id"), c.get("target"))
for c in r.findall("mxCell"):
    if c.get("edge") == "1":
        assert c.get("source") in ids, c.get("source")
        assert c.get("target") in ids, c.get("target")
print("OK valid; cells=%d edges=%d" % (len(ids), sum(1 for c in r.findall('mxCell') if c.get('edge')=='1')))
print(xml)
