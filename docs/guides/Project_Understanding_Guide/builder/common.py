import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

PAGE_W, PAGE_H = letter
MARGIN = 54
USABLE_W = PAGE_W - 2 * MARGIN # 504 pt
USABLE_H = PAGE_H - 2 * MARGIN # 684 pt

class PugNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages):
        self.saveState()
        
        # Cover page has pageNumber 1
        if self._pageNumber > 1:
            # Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#1E3A8A"))
            self.drawString(MARGIN, PAGE_H - 38, "DEVFORGE AI")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(MARGIN + 68, PAGE_H - 38, "— Complete Project Understanding Guide & MVP Blueprint")
            self.drawRightString(PAGE_W - MARGIN, PAGE_H - 38, "October 2026 | Guide v2.2.0")
            
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(MARGIN, PAGE_H - 44, PAGE_W - MARGIN, PAGE_H - 44)
            
            # Footer
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(MARGIN, 44, PAGE_W - MARGIN, 44)
            
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(MARGIN, 32, "Confidential — DevForge AI Engineering Core (Department of Computer Science)")
            page_text = f"Page {self._pageNumber} of {total_pages}"
            self.drawRightString(PAGE_W - MARGIN, 32, page_text)
            
        self.restoreState()

def get_pug_styles():
    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#0F172A")    # Slate 900
    c_secondary = colors.HexColor("#1E3A8A")  # Blue 900
    c_blue = colors.HexColor("#2563EB")       # Blue 600
    c_body = colors.HexColor("#1E293B")       # Slate 800
    c_muted = colors.HexColor("#64748B")      # Slate 500

    custom_styles = {
        'CoverTitle': ParagraphStyle(
            'CoverTitle',
            fontName='Helvetica-Bold',
            fontSize=24,
            leading=30,
            textColor=colors.white,
            spaceAfter=8
        ),
        'CoverSubtitle': ParagraphStyle(
            'CoverSubtitle',
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#93C5FD"),
            spaceAfter=8
        ),
        'CoverMeta': ParagraphStyle(
            'CoverMeta',
            fontName='Helvetica',
            fontSize=8.5,
            leading=13.5,
            textColor=colors.HexColor("#E2E8F0")
        ),
        'SecH1': ParagraphStyle(
            'SecH1',
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=c_secondary,
            spaceBefore=12,
            spaceAfter=5,
            keepWithNext=True
        ),
        'SecH2': ParagraphStyle(
            'SecH2',
            fontName='Helvetica-Bold',
            fontSize=10.5,
            leading=14.5,
            textColor=c_primary,
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True
        ),
        'SecH3': ParagraphStyle(
            'SecH3',
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=12.5,
            textColor=c_blue,
            spaceBefore=6,
            spaceAfter=3,
            keepWithNext=True
        ),
        'Body': ParagraphStyle(
            'Body',
            fontName='Helvetica',
            fontSize=8.2,
            leading=11.6,
            textColor=c_body,
            spaceAfter=4.5
        ),
        'Bullet': ParagraphStyle(
            'Bullet',
            fontName='Helvetica',
            fontSize=8.2,
            leading=11.6,
            textColor=c_body,
            leftIndent=11,
            spaceAfter=2.5
        ),
        'Callout': ParagraphStyle(
            'Callout',
            fontName='Helvetica-Oblique',
            fontSize=8.0,
            leading=11.2,
            textColor=colors.HexColor("#0F172A")
        ),
        'CodeSnippet': ParagraphStyle(
            'CodeSnippet',
            fontName='Courier',
            fontSize=7.2,
            leading=9.5,
            textColor=colors.HexColor("#0F172A")
        ),
        'TableHead': ParagraphStyle(
            'TableHead',
            fontName='Helvetica-Bold',
            fontSize=7.6,
            leading=10.0,
            textColor=colors.white
        ),
        'TableCell': ParagraphStyle(
            'TableCell',
            fontName='Helvetica',
            fontSize=7.2,
            leading=9.6,
            textColor=c_body
        ),
        'TableCellBold': ParagraphStyle(
            'TableCellBold',
            fontName='Helvetica-Bold',
            fontSize=7.2,
            leading=9.6,
            textColor=c_body
        ),
        'TableCellMuted': ParagraphStyle(
            'TableCellMuted',
            fontName='Helvetica',
            fontSize=6.8,
            leading=9.0,
            textColor=c_muted
        )
    }
    return custom_styles

def make_callout(text, styles, bg_hex="#EFF6FF", border_hex="#93C5FD"):
    p = Paragraph(text, styles['Callout'])
    t = Table([[p]], colWidths=[USABLE_W])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg_hex)),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor(border_hex)),
        ('PADDING', (0,0), (-1,-1), 5.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5.5),
    ]))
    return t

def make_table(header, rows, col_widths, styles, primary_color="#1E3A8A"):
    data = []
    head_row = [Paragraph(h, styles['TableHead']) for h in header]
    data.append(head_row)
    for r in rows:
        row_cells = []
        for c in r:
            if isinstance(c, str):
                row_cells.append(Paragraph(c, styles['TableCell']))
            else:
                row_cells.append(c)
        data.append(row_cells)
    
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(primary_color)),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    return t
