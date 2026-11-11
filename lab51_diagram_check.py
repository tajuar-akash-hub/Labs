import re, xml.etree.ElementTree as ET

path = r"F:\PORIDHI_JOB\labs\Data Quality for ML labs\lab 5.1\lab_5.1.md"
text = open(path, encoding="utf-8").read()

blocks = re.findall(r"```xml\n(.*?)```", text, re.S)
print("xml blocks:", len(blocks))
xml = blocks[0]
root = ET.fromstring(xml)
cells = root.findall(".//mxCell")
print("total cells:", len(cells))

verts = [c for c in cells if c.get("vertex") == "1"]
edges = [c for c in cells if c.get("edge") == "1"]
print("vertices:", len(verts), "edges:", len(edges))

def geom(c):
    g = c.find("mxGeometry")
    if g is None:
        return None
    return (float(g.get("x", 0)), float(g.get("y", 0)),
            float(g.get("width", 0)), float(g.get("height", 0)))

# report vertices with geometry
print("\n--- vertices ---")
for c in verts:
    g = geom(c)
    style = c.get("style", "")
    val = (c.get("value") or "").replace("\n", " ")[:60]
    print(f"id={c.get('id'):>4} geom={g} html={c.get('html')} value={val!r}")
    if "imageAspect" in style or "shape=image" in style:
        print(f"      ICON")
    m = re.search(r"fontSize=(\d+)", style)
    if m and c.get("value"):
        fs = int(m.group(1))
        if fs < 16:
            print(f"      !! fontSize {fs} < 16")
    if re.search(r"fontSize=(\d+)", style) and c.get("value"):
        fs = int(re.search(r"fontSize=(\d+)", style).group(1))
        if fs in (18,19,20,28) and "strokeColor=none" not in style and "fillColor=none" not in style:
            print(f"      (block/label)")

print("\n--- edges ---")
ids = {c.get("id") for c in verts}
for c in edges:
    g = geom(c)
    src, tgt = c.get("source"), c.get("target")
    ok = src in ids and tgt in ids
    print(f"id={c.get('id'):>4} {src}->{tgt} valid={ok} dashed={'dashed=1' in (c.get('style') or '')}")
    if not ok:
        print("   !! dangling edge")

# label cells
print("\n--- edge label cells (parent=edge) ---")
for c in verts:
    p = c.get("parent")
    if p and p.startswith(("13","14")) and p not in ids:
        print(f"id={c.get('id')} parent={p} value={c.get('value')!r} style={c.get('style')}")
