import re, xml.etree.ElementTree as ET

path = r"F:\PORIDHI_JOB\labs\Data Quality for ML labs\lab 5.1\lab_5.1.md"
text = open(path, encoding="utf-8").read()
xml = re.findall(r"```xml\n(.*?)```", text, re.S)[0]
root = ET.fromstring(xml)
cells = root.findall(".//mxCell")

def geom(c):
    g = c.find("mxGeometry")
    return (float(g.get("x", 0)), float(g.get("y", 0)),
            float(g.get("width", 0)), float(g.get("height", 0)))

verts = [c for c in cells if c.get("vertex") == "1"]

# Only treat "content" cells (skip frame 101, and skip zone 105/113/125 themselves)
ZONES = {"105", "113", "125"}
FRAME = {"101"}
def rects_of(c):
    x, y, w, h = geom(c)
    return (x, y, x+w, y+h)

def overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

print("=== containment check (icons/labels inside their blocks) ===")
BLOCKS = ["107","109","111","121","123","127","129"]
ICONS  = ["108","110","112","122","124","128","130"]
byid = {c.get("id"): c for c in cells}
for b in BLOCKS:
    rb = rects_of(byid[b])
    for i in ICONS:
        if byid[i].get("value") == "" and geom(byid[i])[0] >= 0:
            ri = rects_of(byid[i])
            # icon should be inside block bounds
            inside = ri[0] >= rb[0] and ri[1] >= rb[1] and ri[2] <= rb[2] and ri[3] <= rb[3]
            # horizontal: icon at left of text, text starts after spacingLeft=58 from block left
            print(f"  icon {i} in block {b}: inside={inside}  icon_x={ri[0]} block_x={rb[0]}")

print("\n=== zone membership ===")
for z in ZONES:
    rz = rects_of(byid[z])
    inside = []
    for c in verts:
        i = c.get("id")
        if i in ZONES or i in FRAME or i in {"102","103","104","106"}: continue
        r = rects_of(c)
        if r[0] >= rz[0]-2 and r[1] >= rz[1]-2 and r[2] <= rz[2]+2 and r[3] <= rz[3]+2:
            inside.append(i)
    print(f"  zone {z} {rects_of(byid[z])} contains {inside}")

print("\n=== block-block overlap (content cells only) ===")
content = [c for c in verts if c.get("id") not in ZONES|FRAME|{"102","103","104","106"} and not (c.get("value")=="")]
for i in range(len(content)):
    for j in range(i+1, len(content)):
        a, b = content[i], content[j]
        if overlap(rects_of(a), rects_of(b)):
            print(f"  OVERLAP {a.get('id')} <-> {b.get('id')}")

print("\n=== contrast ===")
def lum(hexs):
    hexs = hexs.lstrip('#')
    r,g,b = [int(hexs[i:i+2],16)/255 for i in (0,2,4)]
    def f(c): return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    r,g,b = f(r),f(g),f(b)
    return 0.2126*r+0.7152*g+0.0722*b
def cr(a,b):
    l1,l2 = lum(a),lum(b)
    if l1<l2: l1,l2 = l2,l1
    return (l1+0.05)/(l2+0.05)

pairs = [
    ("#1F2937","#FFFFFF","ink on paper"),
    ("#6B7280","#FFFFFF","muted on paper"),
    ("#FFFFFF","#2F4AA6","white on primary"),
    ("#FFFFFF","#0E7C95","white on accent"),
    ("#1F2937","#F2F5FA","ink on zone-fill"),
    ("#E8EDF7","#FFFFFF","sub-label white on paper"),
    ("#1F2937","#FFFFFF","edge label ink"),
]
for a,b,n in pairs:
    print(f"  {n:30s} {a} on {b} = {cr(a,b):.2f}:1")

print("\n=== icon SVG decode ===")
for c in verts:
    st = c.get("style") or ""
    m = re.search(r"image=data:image/svg\+xml,([^;\"']+)", st)
    if m:
        import base64
        svg = base64.b64decode(m.group(1)).decode()
        paths = re.findall(r"<path|<circle|<rect|<line|<ellipse|<polyline", svg)
        stroke = re.search(r'stroke="([^"]+)"', svg)
        fill = re.search(r'fill="([^"]+)"', svg)
        print(f"  id={c.get('id')} shapes={len(paths)} stroke={stroke.group(1) if stroke else None} fill={fill.group(1) if fill else None} sw={re.search(r'stroke-width=.([0-9.]+)', svg).group(1) if re.search(r'stroke-width=.([0-9.]+)', svg) else None}")
