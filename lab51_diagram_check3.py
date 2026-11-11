import re, xml.etree.ElementTree as ET
path = r"F:\PORIDHI_JOB\labs\Data Quality for ML labs\lab 5.1\lab_5.1.md"
text = open(path, encoding="utf-8").read()
xml = re.findall(r"```xml\n(.*?)```", text, re.S)[0]
root = ET.fromstring(xml)
byid = {c.get("id"): c for c in root.findall(".//mxCell")}

LABELS = {c.get("id") for c in root.findall(".//mxCell")
          if c.get("vertex")=="1" and (c.get("parent") or "").startswith(("13","14"))}

def rects(i):
    g=byid[i].find("mxGeometry")
    if g is None or g.get("x") is None: return None
    x,y,w,h = float(g.get("x")),float(g.get("y")),float(g.get("width")),float(g.get("height"))
    return (x,y,x+w,y+h)

print("=== frame inset (frame 20,20 -> 1580,880) ===")
for i,c in byid.items():
    if c.get("vertex")!="1" or i=="101" or i in LABELS: continue
    r=rects(i)
    if r is None: continue
    if r[0]<20 or r[1]<20 or r[2]>1580 or r[3]>880:
        print(f"  {i} outside frame: {r}")
print("  (no output above = all content inside frame)")

print("\n=== edge crossing blocks ===")
BLOCKS=["107","109","111","121","123","127","129"]
for e in root.findall(".//mxCell"):
    if e.get("edge")!="1": continue
    s,t=e.get("source"),e.get("target")
    st=e.get("style") or ""
    ex=re.search(r"exitX=([0-9.]+)",st); ey=re.search(r"exitY=([0-9.]+)",st)
    nx=re.search(r"entryX=([0-9.]+)",st); ny=re.search(r"entryY=([0-9.]+)",st)
    rs,rt=rects(s),rects(t)
    sx = rs[2] if ex and float(ex.group(1))>=0.5 else rs[0]
    sy = rs[1]+(rs[3]-rs[1])*float(ey.group(1)) if ey else (rs[1]+rs[3])/2
    tx = rt[0] if nx and float(nx.group(1))<=0.5 else rt[2]
    ty = rt[1]+(rt[3]-rt[1])*float(ny.group(1)) if ny else (rt[1]+rt[3])/2
    hits=[]
    for b in BLOCKS:
        if b in (s,t): continue
        rb=rects(b)
        if min(sx,tx)<=rb[2] and max(sx,tx)>=rb[0]:
            for yy in (sy,ty):
                if rb[1]<=yy<=rb[3]: hits.append(b+"/h")
        if min(sy,ty)<=rb[3] and max(sy,ty)>=rb[1]:
            for xx in (sx,tx):
                if rb[0]<=xx<=rb[2]: hits.append(b+"/v")
    print(f"  {e.get('id')} {s}->{t}: {sorted(set(hits)) or 'none'}")

print("\n=== gap between zone 113 blocks and zone 125 zone ===")
print("  zone113:", rects("113"), " zone125:", rects("125"))
print("  121 report:", rects("121"), " 123 issues:", rects("123"))
print("  gap 123.bottom -> 125.top:", rects("123")[3], "->", rects("125")[1])
print("  zone113.right -> 121.left:", rects("113")[2], "->", rects("121")[0])

print("\n=== sibling spacing in zone 113 (need >=80px) ===")
for a,b in [("115","116"),("116","117"),("117","118"),("118","119"),("119","120")]:
    print(f"  {a}->{b}: {rects(b)[1]-rects(a)[3]}")

print("\n=== sibling spacing left column (107,109) ===")
print("  107.bottom->109.top:", rects("109")[1]-rects("107")[3])
print("  123.bottom->125.top:", rects("125")[1]-rects("123")[3])

print("\n=== text vs icon collision (spacingLeft=58 => text starts at x+58; icon ends at x+16+32) ===")
for b,i in [("107","108"),("109","110"),("111","112"),("121","122"),("123","124"),("127","128"),("129","130")]:
    rb,ri = rects(b),rects(i)
    print(f"  {b}: icon {ri[0]}..{ri[2]}  text starts {rb[0]+58}  icon-text gap {rb[0]+58-ri[2]}")
