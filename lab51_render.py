"""Render the lab 5.1 draw.io XML to a PNG approximation for visual review."""
import re, xml.etree.ElementTree as ET, base64, html
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Circle, Ellipse, Polygon
import matplotlib.image as mpimg
import io, os

path = r"F:\PORIDHI_JOB\labs\Data Quality for ML labs\lab 5.1\lab_5.1.md"
text = open(path, encoding="utf-8").read()
xml = re.findall(r"```xml\n(.*?)```", text, re.S)[0]
root = ET.fromstring(xml)
byid = {c.get("id"): c for c in root.findall(".//mxCell")}

def style(c):
    return dict(kv.split("=",1) for kv in (c.get("style") or "").split(";") if "=" in kv)

def rects(i):
    g=byid[i].find("mxGeometry")
    x,y,w,h = float(g.get("x")),float(g.get("y")),float(g.get("width")),float(g.get("height"))
    return (x,y,x+w,y+h)

fig = plt.figure(figsize=(16,9), dpi=110)
ax = fig.add_axes([0,0,1,1]); ax.set_xlim(0,1600); ax.set_ylim(900,0); ax.axis("off")
ax.add_patch(Rectangle((0,0),1600,900,color="white",zorder=0))

LABELS = {c.get("id") for c in root.findall(".//mxCell")
          if c.get("vertex")=="1" and (c.get("parent") or "").startswith(("13","14"))}

def draw_icon(x, y, size, color):
    """Draw a generic outline 'file/document' icon at (x,y) 32x32 in canvas units."""
    s = size/24.0
    def P(pts):
        return [(x+px*s, y+py*s) for px,py in pts]
    # document outline
    ax.add_patch(Polygon(P([(5,1),(15,1),(19,5),(19,23),(5,23)]), closed=True,
                         fill=False, edgecolor=color, linewidth=1.6, zorder=6))
    ax.add_patch(Polygon(P([(15,1),(19,5),(15,5)]), closed=True,
                         fill=False, edgecolor=color, linewidth=1.6, zorder=6))
    for yy in (9,13,17):
        ax.plot([x+8*s, x+16*s],[y+yy*s, y+yy*s], color=color, linewidth=1.4, zorder=6)

for c in root.findall(".//mxCell"):
    if c.get("vertex")!="1": continue
    i=c.get("id")
    if i in LABELS: continue
    sc = c.get("style") or ""
    st=style(c); r=rects(i)
    x0,y0,x1,y1=r
    val=c.get("value") or ""
    m=re.search(r"image=data:image/svg\+xml,([^;\"']+)", sc)
    if m and i!="101":
        svg = base64.b64decode(m.group(1)).decode()
        stroke = re.search(r'stroke="([^"]+)"', svg).group(1)
        draw_icon(x0, y0, 32, stroke)
        continue
    fill = st.get("fillColor","#FFFFFF")
    if fill=="none": fill=None
    ec = st.get("strokeColor","#000000")
    if ec=="none": ec=None
    lw = float(st.get("strokeWidth",1))
    arc = int(st.get("arcSize","0"))
    if fill or ec:
        rs = 14 if arc>=12 else (8 if arc>=20 else 4)
        p=FancyBboxPatch((x0,y0),x1-x0,y1-y0,
            boxstyle=f"round,pad=0,rounding_size={rs}",
            linewidth=lw, facecolor=fill or "none", edgecolor=ec or "none",
            linestyle="--" if st.get("dashed")=="1" else "-", zorder=2)
        ax.add_patch(p)
    if val:
        fc = st.get("fontColor","#000000")
        fs = int(st.get("fontSize",12))
        bold = st.get("fontStyle")=="1"
        if c.get("html")=="1":
            t=re.match(r"<b>(.*?)</b><br><font[^>]*>(.*?)</font>", val)
            if t:
                title=html.unescape(t.group(1)); sub=html.unescape(t.group(2))
                ax.text(x0+58,y0+30,title,fontsize=fs,color=fc,weight="bold",va="center",zorder=7)
                ax.text(x0+58,y0+68,sub,fontsize=14,color="#E8EDF7",va="center",zorder=7)
            else:
                ax.text(x0+58,y0+(y1-y0)/2,html.unescape(val),fontsize=fs,color=fc,weight="bold",va="center",zorder=7)
        elif i in ("102","103","106","114","126"):
            ax.text(x0,y0+(y1-y0)/2,val,fontsize=fs,color=fc,
                    weight="bold" if bold else "normal",va="center",ha="left",zorder=7)
        else:
            ax.text(x0+(x1-x0)/2,y0+(y1-y0)/2,val,fontsize=fs,color=fc,
                    weight="bold" if bold else "normal",va="center",ha="center",zorder=7)

for e in root.findall(".//mxCell"):
    if e.get("edge")!="1": continue
    st=e.get("style") or ""
    s,t=e.get("source"),e.get("target")
    rs,rt=rects(s),rects(t)
    ex=re.search(r"exitX=([0-9.]+)",st); ey=re.search(r"exitY=([0-9.]+)",st)
    nx=re.search(r"entryX=([0-9.]+)",st); ny=re.search(r"entryY=([0-9.]+)",st)
    sx = rs[2] if ex and float(ex.group(1))>=0.5 else rs[0]
    sy = rs[1]+(rs[3]-rs[1])*float(ey.group(1)) if ey else (rs[1]+rs[3])/2
    tx = rt[0] if nx and float(nx.group(1))<=0.5 else rt[2]
    ty = rt[1]+(rt[3]-rt[1])*float(ny.group(1)) if ny else (rt[1]+rt[3])/2
    ls = (0,(5,4)) if "dashed=1" in st else "-"
    ax.add_patch(FancyArrowPatch((sx,sy),(tx,ty), connectionstyle="angle,angleA=0,angleB=90,rad=0",
        arrowstyle="-|>", mutation_scale=15, linewidth=1.6, color="#1F2937",
        linestyle=ls, zorder=3, shrinkA=0, shrinkB=0))
    lab=None
    for lc in root.findall(".//mxCell"):
        if lc.get("parent")==e.get("id"): lab=lc.get("value")
    if lab:
        ax.text((sx+tx)/2,(sy+ty)/2,lab,fontsize=16,color="#1F2937",ha="center",va="center",
                bbox=dict(boxstyle="square,pad=0.15",fc="white",ec="none"),zorder=8)

out = r"F:\PORIDHI_JOB\labs\lab51_diagram_preview.png"
fig.savefig(out, dpi=110, facecolor="white")
print("wrote", out)
