"""
Generates the country source submission template PDF.
Output: docs/country_source_template.pdf
Run: python scripts/generate_source_template.py
"""

from fpdf import FPDF
from fpdf.enums import XPos, YPos

SILVER = (180, 180, 185)
DARK = (30, 30, 40)
ACCENT = (45, 106, 79)       # brand green
LIGHT_GREEN = (237, 247, 241)
LIGHT_GRAY = (248, 248, 250)
MID_GRAY = (220, 220, 225)
WHITE = (255, 255, 255)
LABEL_GRAY = (100, 100, 110)

SECTORS = [
    ("GOV", "gov_agencies", "Government bodies, regulatory authorities"),
    ("ASC", "associations",  "Industry associations, trade bodies"),
    ("CUS", "customers",     "Known or target customers"),
    ("PAR", "partners",      "Technology / service partners"),
    ("COM", "competitors",   "Direct competitors"),
    ("GEN", "general_news",  "General industry news outlets"),
]

def _safe(text):
    return text.replace("-", "-").replace("-", "-").replace("‘", "'").replace("’", "'")

DOMAINS = [
    ("BER", "Built Environment & Real Estate"),
    ("EDU", "Education & EdTech"),
    ("MFG", "Manufacturing & Industry 4.0"),
    ("HLS", "Healthcare & Life Sciences"),
    ("RCC", "Retail, Commerce & Consumer Goods"),
    ("CTE", "Culture, Tourism & Events"),
    ("PSS", "Public Sector & Smart Cities"),
]

NUM_ROWS = 15


class SourceTemplate(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "I", 7.5)
        self.set_text_color(*LABEL_GRAY)
        self.cell(0, 5, "Silversea Media  ·  Market Intelligence Pipeline  ·  Source Submission Template", align="C")


def draw_header(pdf):
    # Dark banner
    pdf.set_fill_color(*DARK)
    pdf.rect(0, 0, 210, 28, style="F")

    pdf.set_xy(14, 7)
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(*WHITE)
    pdf.cell(120, 8, "Market Intelligence", new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*SILVER)
    pdf.cell(0, 5, "Source Submission Template  ·  Silversea Media", new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def draw_intro(pdf):
    pdf.set_xy(14, 32)

    # Country field
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*LABEL_GRAY)
    pdf.cell(20, 5, "COUNTRY / MARKET")
    pdf.set_xy(14, 37)
    pdf.set_fill_color(*LIGHT_GRAY)
    pdf.set_draw_color(*MID_GRAY)
    pdf.rect(14, 37, 80, 8, style="FD")
    pdf.set_xy(14, 32)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*DARK)
    pdf.set_xy(16, 38.5)
    pdf.cell(76, 5, "")   # blank input area

    # Submitted by field
    pdf.set_xy(110, 32)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*LABEL_GRAY)
    pdf.cell(30, 5, "SUBMITTED BY")
    pdf.set_fill_color(*LIGHT_GRAY)
    pdf.set_draw_color(*MID_GRAY)
    pdf.rect(110, 37, 86, 8, style="FD")

    # Instructions box
    pdf.set_xy(14, 50)
    pdf.set_fill_color(*LIGHT_GREEN)
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.4)
    pdf.rect(14, 50, 182, 26, style="FD")

    pdf.set_xy(17, 52)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 5, "HOW TO FILL THIS FORM", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    instructions = [
        "1.  Source Name - Short display name of the organisation (e.g. \"Ministry of Education Malaysia\").",
        "2.  URL - Link to the newsroom, press-release, or blog page - NOT the homepage.",
        "3.  Description - One sentence: what the organisation does and why it is relevant to Silversea.",
        "4.  Sector - Write the 3-letter code from the legend below that best describes the relationship to Silversea.",
        "5.  Domain (optional) - Write the 3-letter code from the legend that best describes the industry covered.",
    ]
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(*DARK)
    for line in instructions:
        pdf.set_x(17)
        pdf.cell(0, 4, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_line_width(0.2)


def draw_legend(pdf, y):
    pdf.set_xy(14, y)

    # Sector legend
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(*LABEL_GRAY)
    pdf.cell(0, 4, "SECTOR CODES", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(14)

    col_w = 60
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*DARK)
    for i, (code, name, desc) in enumerate(SECTORS):
        col = i % 3
        row = i // 3
        x = 14 + col * col_w
        ly = y + 5 + row * 5
        pdf.set_xy(x, ly)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*ACCENT)
        pdf.cell(8, 4, code)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*DARK)
        pdf.cell(col_w - 8, 4, f"{name}  -  {desc}")

    legend_h = 5 + (len(SECTORS) // 3) * 5 + 4

    # Domain legend
    dom_y = y + legend_h + 2
    pdf.set_xy(14, dom_y)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(*LABEL_GRAY)
    pdf.cell(0, 4, "DOMAIN CODES  (optional)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(14)

    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*DARK)
    dom_cols = 2
    col_w2 = 91
    for i, (code, desc) in enumerate(DOMAINS):
        col = i % dom_cols
        row = i // dom_cols
        x = 14 + col * col_w2
        dy = dom_y + 5 + row * 5
        pdf.set_xy(x, dy)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*ACCENT)
        pdf.cell(8, 4, code)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*DARK)
        pdf.cell(col_w2 - 8, 4, desc)

    return dom_y + 5 + ((len(DOMAINS) + dom_cols - 1) // dom_cols) * 5 + 2


def draw_table(pdf, start_y):
    # Column definitions: (label, x, w)
    cols = [
        ("#",           14,   8),
        ("SOURCE NAME", 22,   42),
        ("URL",         64,   58),
        ("DESCRIPTION", 122,  46),
        ("SECTOR",      168,  12),
        ("DOMAIN",      180,  16),
    ]

    row_h = 12
    header_h = 7

    # Table header
    pdf.set_fill_color(*DARK)
    pdf.rect(14, start_y, 182, header_h, style="F")

    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_text_color(*WHITE)
    for label, x, w in cols:
        pdf.set_xy(x + 1.5, start_y + 1.5)
        pdf.cell(w - 1.5, header_h - 2, label)

    # Rows
    for i in range(NUM_ROWS):
        y = start_y + header_h + i * row_h
        fill = LIGHT_GRAY if i % 2 == 0 else WHITE

        pdf.set_fill_color(*fill)
        pdf.set_draw_color(*MID_GRAY)
        pdf.set_line_width(0.15)
        pdf.rect(14, y, 182, row_h, style="FD")

        # Row number
        pdf.set_xy(14 + 1, y + 3.5)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*LABEL_GRAY)
        pdf.cell(8 - 2, 5, str(i + 1), align="C")

        # Vertical dividers between cells
        pdf.set_draw_color(*MID_GRAY)
        for _, x, w in cols[1:]:
            pdf.line(x, y, x, y + row_h)

        # Sector checkbox hints (tiny legend inside cell)
        sec_x = 168 + 1
        pdf.set_xy(sec_x, y + 1)
        pdf.set_font("Helvetica", "", 5.5)
        pdf.set_text_color(*LABEL_GRAY)
        pdf.cell(11, 3, "GOV ASC CUS", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(sec_x)
        pdf.cell(11, 3, "PAR COM GEN")

    # Outer border
    pdf.set_draw_color(*DARK)
    pdf.set_line_width(0.4)
    table_h = header_h + NUM_ROWS * row_h
    pdf.rect(14, start_y, 182, table_h, style="D")


def generate():
    pdf = SourceTemplate(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(False)
    pdf.add_page()

    draw_header(pdf)
    draw_intro(pdf)

    # Legend sits below intro box (which ends at y≈76)
    legend_end_y = draw_legend(pdf, 79)

    draw_table(pdf, legend_end_y + 2)

    # Page 2 - continuation
    pdf.add_page()
    draw_header(pdf)

    pdf.set_xy(14, 32)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*LABEL_GRAY)
    pdf.cell(0, 6, "Continuation sheet - attach as many pages as needed.")

    draw_table(pdf, 40)

    out = "docs/country_source_template.pdf"
    pdf.output(out)
    print(f"Generated: {out}")


if __name__ == "__main__":
    generate()

