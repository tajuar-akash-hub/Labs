#!/usr/bin/env python
"""Convert a Poridhi Lab markdown file to a styled PDF using ReportLab."""

import sys
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted, PageBreak,
    Table, TableStyle, KeepTogether
)
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def find_courier_font():
    """Find a monospace font for code blocks."""
    candidates = [
        ("CourierNew", "/usr/share/fonts/truetype/msttcorefonts/Courier_New.ttf"),
        ("CourierNew", "C:/Windows/Fonts/cour.ttf"),
        ("CourierNew", "C:/Windows/Fonts/consola.ttf"),
        ("Courier", "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"),
        ("DejaVuSansMono", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
        ("Courier", "/usr/share/fonts/TTF/DejaVuSansMono.ttf"),
    ]
    for name, path in candidates:
        try:
            pdfmetrics.registerFont(TTFont(name, path))
            return name
        except Exception:
            continue
    return "Courier"


def parse_inline(text, code_style):
    """Convert inline markdown (bold/italic/code) into ReportLab <inline> tags."""
    # Escape HTML-sensitive chars first
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Inline code: `text`
    parts = re.split(r"(`[^`\n]+`)", text)
    out = []
    for part in parts:
        if part.startswith("`") and part.endswith("`"):
            inner = part[1:-1]
            out.append(f'<font face="{code_style.fontName}" size="{code_style.fontSize}">{inner}</font>')
        else:
            # Bold: **text**
            sub_parts = re.split(r"(\*\*[^*\n]+\*\*)", part)
            for sp in sub_parts:
                if sp.startswith("**") and sp.endswith("**"):
                    out.append(f"<b>{sp[2:-2]}</b>")
                else:
                    out.append(sp)
    return "".join(out)


def md_to_flowables(md_text, styles, code_font):
    """Convert markdown text to a list of ReportLab flowables."""
    flow = []
    lines = md_text.split("\n")
    i = 0
    in_code = False
    code_buf = []
    code_lang = ""

    def flush_code():
        nonlocal code_buf, code_lang
        if not code_buf:
            return
        body = "\n".join(code_buf)
        # Shrink code slightly to fit
        style = ParagraphStyle(
            "codeblock",
            parent=styles["Code"],
            fontName=code_font,
            fontSize=7.5,
            leading=9,
            leftIndent=8,
            rightIndent=8,
            backColor=colors.HexColor("#1F2A44"),
            textColor=colors.HexColor("#E0E0E0"),
            borderColor=colors.HexColor("#5A8FCE"),
            borderWidth=0.5,
            borderPadding=6,
            spaceBefore=4,
            spaceAfter=8,
        )
        flow.append(Preformatted(body, style))
        code_buf = []
        code_lang = ""

    code_style = ParagraphStyle("code_inline", fontName=code_font, fontSize=9)

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Code fence
        if stripped.startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
                code_lang = stripped[3:].strip()
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # Heading
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            style_name = f"Heading{lvl_map(level)}"
            if style_name in styles:
                flow.append(Paragraph(parse_inline(text, code_style), styles[style_name]))
            else:
                flow.append(Paragraph(parse_inline(text, code_style), styles["Heading4"]))
            flow.append(Spacer(1, 4))
            i += 1
            continue

        # Horizontal rule
        if stripped == "---":
            flow.append(Spacer(1, 4))
            i += 1
            continue

        # Table detection
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s|:-]+\|\s*$", lines[i + 1].strip()):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                tbl.append(row)
                i += 1
            # Skip separator row
            data = [r for r in tbl if not re.match(r"^[\s|:-]+$", "|".join(r))]
            if data:
                col_count = max(len(r) for r in data)
                normalized = [r + [""] * (col_count - len(r)) for r in data]
                # Build paragraphs for cell wrapping
                cell_style = ParagraphStyle("cell", fontSize=8, leading=10, fontName="Helvetica")
                head_style = ParagraphStyle("cellh", fontSize=8, leading=10, fontName="Helvetica-Bold", textColor=colors.white)
                table_data = []
                for r_idx, row in enumerate(normalized):
                    table_data.append([Paragraph(parse_inline(c, code_style), head_style if r_idx == 0 else cell_style) for c in row])
                avail_w = A4[0] - 4 * cm
                col_w = avail_w / col_count
                t = Table(table_data, colWidths=[col_w] * col_count, repeatRows=1)
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2A44")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#5A8FCE")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ] + [("BACKGROUND", (0, r), (-1, r), colors.HexColor("#F2F4F8")) for r in range(1, len(normalized)) if r % 2 == 0]))
                flow.append(t)
                flow.append(Spacer(1, 8))
            continue

        # Bulleted list
        if re.match(r"^[\*\-]\s+", stripped):
            bullet_text = re.sub(r"^[\*\-]\s+", "", stripped)
            indent_level = (len(line) - len(line.lstrip())) // 2
            bullet_char = "•" if indent_level == 0 else "–"
            style = ParagraphStyle(
                "bullet",
                parent=styles["BodyText"],
                leftIndent=14 + indent_level * 12,
                bulletIndent=4 + indent_level * 12,
                spaceAfter=2,
            )
            flow.append(Paragraph(f"{bullet_char}  {parse_inline(bullet_text, code_style)}", style))
            i += 1
            continue

        # Numbered list
        if re.match(r"^\d+\.\s+", stripped):
            num_match = re.match(r"^(\d+)\.\s+(.*)$", stripped)
            style = ParagraphStyle(
                "numbered",
                parent=styles["BodyText"],
                leftIndent=20,
                bulletIndent=4,
                spaceAfter=2,
            )
            flow.append(Paragraph(f"{num_match.group(1)}.  {parse_inline(num_match.group(2), code_style)}", style))
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            text = stripped.lstrip(">").strip()
            style = ParagraphStyle(
                "quote",
                parent=styles["BodyText"],
                leftIndent=20,
                textColor=colors.HexColor("#555555"),
                fontName="Helvetica-Oblique",
            )
            flow.append(Paragraph(parse_inline(text, code_style), style))
            i += 1
            continue

        # Blank line
        if not stripped:
            flow.append(Spacer(1, 4))
            i += 1
            continue

        # Paragraph: collect contiguous non-empty non-special lines
        para_lines = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i]
            nxt_s = nxt.strip()
            if (not nxt_s or nxt_s.startswith("#") or nxt_s.startswith("```")
                    or nxt_s.startswith("|") or re.match(r"^[\*\-]\s+", nxt_s)
                    or re.match(r"^\d+\.\s+", nxt_s) or nxt_s == "---"
                    or nxt_s.startswith(">")):
                break
            para_lines.append(nxt)
            i += 1
        para = " ".join(l.strip() for l in para_lines)
        flow.append(Paragraph(parse_inline(para, code_style), styles["BodyText"]))
        flow.append(Spacer(1, 3))

    flush_code()
    return flow


def lvl_map(level):
    return {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}.get(level, 4)


def main():
    if len(sys.argv) < 3:
        print("Usage: md_to_pdf.py <input.md> <output.pdf>")
        sys.exit(1)

    src, dst = sys.argv[1], sys.argv[2]

    with open(src, "r", encoding="utf-8") as f:
        md = f.read()

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "Title2",
        parent=styles["Title"],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#FF6B1A"),
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        "H1Poridhi",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#FF6B1A"),
        spaceBefore=14,
        spaceAfter=8,
    ))
    styles["Heading2"].fontSize = 16
    styles["Heading2"].textColor = colors.HexColor("#1F2A44")
    styles["Heading2"].spaceBefore = 10
    styles["Heading2"].spaceAfter = 6
    styles["Heading3"].fontSize = 13
    styles["Heading3"].textColor = colors.HexColor("#1F2A44")
    styles["Heading3"].spaceBefore = 8
    styles["Heading3"].spaceAfter = 4
    styles["Heading4"].fontSize = 11
    styles["Heading4"].textColor = colors.HexColor("#1F2A44")
    styles["Heading4"].spaceBefore = 6
    styles["Heading4"].spaceAfter = 3
    styles["BodyText"].fontSize = 10
    styles["BodyText"].leading = 13
    styles["BodyText"].spaceAfter = 4
    styles["Code"].fontSize = 8

    code_font = find_courier_font()

    doc = SimpleDocTemplate(
        dst,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Poridhi Lab 2",
        author="Poridhi Lab Creation Skill",
    )

    flow = md_to_flowables(md, styles, code_font)
    doc.build(flow)
    print(f"PDF written: {dst}")


if __name__ == "__main__":
    main()