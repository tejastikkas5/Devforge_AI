import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, Image
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print total page count
    along with running academic headers and footers.
    """
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
            if self._pageNumber > 1:
                self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1A365D"))
        
        # Header (Top of Page)
        self.drawString(36, 816, "MIT College of Railway Engineering & Research, Barshi")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        self.drawRightString(559, 816, "RM-01: Research Methodology & IPR — Lab Journal")
        
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.6)
        self.line(36, 809, 559, 809)

        # Footer (Bottom of Page)
        self.line(36, 38, 559, 38)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(36, 27, "Dept. of Computer Science & Engineering | B.Tech Sem-VII (AY 2026-27)")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(559, 27, page_str)
        self.restoreState()


def create_manual(output_pdf_path):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Academic Palette
    c_primary = colors.HexColor("#1A365D")   # Deep Navy
    c_secondary = colors.HexColor("#2B6CB0") # Cobalt Blue
    c_dark = colors.HexColor("#1A202C")      # Charcoal
    c_bg_light = colors.HexColor("#F8FAFC")  # Off-white
    c_callout = colors.HexColor("#EBF8FF")   # Soft Sky Blue
    c_border = colors.HexColor("#CBD5E0")    # Subtle Border Grey

    # Typography Styles
    cover_title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=1,
        textColor=c_primary
    )

    cover_subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        alignment=1,
        textColor=c_secondary
    )

    h1_style = ParagraphStyle(
        'ExpHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.white
    )

    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11.5,
        textColor=c_primary,
        spaceBefore=4,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.2,
        textColor=c_dark
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=body_style,
        leftIndent=10,
        firstLineIndent=-7,
        spaceBefore=1.5,
        spaceAfter=1.5
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.8,
        leading=10.2,
        textColor=colors.HexColor("#2D3748")
    )

    th_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.3,
        leading=9,
        alignment=1,
        textColor=colors.white
    )

    tc_style = ParagraphStyle(
        'TC',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9,
        textColor=c_dark
    )

    tcb_style = ParagraphStyle(
        'TCB',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9,
        textColor=c_dark
    )

    def make_header_banner(exp_num, title, co_str):
        tbl = Table([[
            Paragraph(f"<b>EXPERIMENT NO. {exp_num}: {title.upper()}</b>", h1_style),
            Paragraph(f"<b>{co_str}</b>", ParagraphStyle('HR', parent=h1_style, alignment=2, fontSize=8))
        ]], colWidths=[385, 138])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), c_primary),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        return tbl

    def make_aim_box(aim_text):
        tbl = Table([[Paragraph(f"<b>AIM:</b> {aim_text}", callout_style)]], colWidths=[523])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), c_callout),
            ('BOX', (0, 0), (-1, -1), 0.75, c_secondary),
            ('TOPPADDING', (0, 0), (-1, -1), 3.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6)
        ]))
        return tbl

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 20))
    logo_path = os.path.join(os.path.dirname(output_pdf_path), 'extracted_logo.png')
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=1.45*inch, height=1.34*inch))
    story.append(Spacer(1, 12))

    story.append(Paragraph("MAHARASHTRA INSTITUTE OF TECHNOLOGY", cover_subtitle_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("MIT College of Railway Engineering & Research, Barshi", ParagraphStyle('InstName', parent=cover_subtitle_style, fontSize=14, leading=18, textColor=c_primary)))
    story.append(Paragraph("Department of Computer Science & Engineering", ParagraphStyle('DeptName', parent=cover_subtitle_style, fontSize=10.5, leading=14, fontName='Helvetica', textColor=colors.HexColor("#4A5568"))))
    story.append(Paragraph("Academic Year: 2026 – 2027", ParagraphStyle('AY', parent=cover_subtitle_style, fontSize=9, leading=12, fontName='Helvetica-Bold', textColor=colors.HexColor("#718096"))))
    story.append(Spacer(1, 15))

    story.append(HRFlowable(width="90%", thickness=1.5, color=c_primary, spaceBefore=2, spaceAfter=12))
    story.append(Paragraph("LABORATORY MANUAL & PRACTICAL JOURNAL", cover_title_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph("RESEARCH METHODOLOGY & IPR (RM-01)", ParagraphStyle('CourseTitle', parent=cover_title_style, fontSize=14, leading=18, textColor=c_secondary)))
    story.append(Paragraph("B.Tech (Computer Science & Engineering) — Semester VII", ParagraphStyle('ClassInfo', parent=cover_subtitle_style, fontSize=9.5, fontName='Helvetica-Bold', textColor=colors.HexColor("#2D3748"))))
    story.append(Paragraph("<i>Concise Practical Reference Edition (Brief Version of All 6 Practicals)</i>", ParagraphStyle('SubTag', parent=cover_subtitle_style, fontSize=8.5, fontName='Helvetica-Oblique', textColor=colors.HexColor("#4A5568"))))
    story.append(HRFlowable(width="90%", thickness=1, color=c_secondary, spaceBefore=12, spaceAfter=18))

    story.append(Spacer(1, 10))

    # Student Submission Block
    cred_data = [
        [Paragraph("<b>STUDENT SUBMISSION RECORD</b>", ParagraphStyle('RecHead', parent=th_style, fontSize=8.5, textColor=colors.white)), ""],
        [Paragraph("<b>Name of Student:</b>", body_style), Paragraph("____________________________________________________________", body_style)],
        [Paragraph("<b>Roll No. / Enrollment No.:</b>", body_style), Paragraph("____________________________________________________________", body_style)],
        [Paragraph("<b>Class & Branch:</b>", body_style), Paragraph("B.Tech — Computer Science & Engineering", body_style)],
        [Paragraph("<b>Semester / Division / Batch:</b>", body_style), Paragraph("Semester VII / Division: ______ / Batch: ______", body_style)],
        [Paragraph("<b>Course Code & Name:</b>", body_style), Paragraph("RM-01: Research Methodology and IPR", body_style)],
        [Paragraph("<b>Faculty In-Charge:</b>", body_style), Paragraph("____________________________________________________________", body_style)]
    ]
    cred_table = Table(cred_data, colWidths=[150, 320])
    cred_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 0), (1, 0), c_primary),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 1, c_secondary),
        ('INNERGRID', (0, 1), (-1, -1), 0.5, c_border)
    ]))
    story.append(cred_table)

    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Certified that this is a bonafide record of practical work completed by the student in the Institute laboratory.</b>", ParagraphStyle('Cert', parent=body_style, fontSize=7.5, alignment=1, textColor=colors.HexColor("#718096"))))
    
    story.append(Spacer(1, 25))
    sig_data = [
        [Paragraph("<b>Signature of Student</b>", ParagraphStyle('S1', parent=body_style, alignment=0)),
         Paragraph("<b>Signature of Faculty In-Charge</b>", ParagraphStyle('S2', parent=body_style, alignment=1)),
         Paragraph("<b>Seal / Signature of HOD</b>", ParagraphStyle('S3', parent=body_style, alignment=2))]
    ]
    sig_table = Table(sig_data, colWidths=[174, 174, 175])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0)
    ]))
    story.append(sig_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: COURSE OUTCOMES & PRACTICAL INDEX
    # =========================================================================
    story.append(Paragraph("Course Framework & Practical Index", ParagraphStyle('P2Title', parent=h2_style, fontSize=11, leading=14)))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("<b>Course Outcomes (COs) — RM-01: Research Methodology and IPR</b>", h2_style))
    co_data = [
        [Paragraph("<b>CO ID</b>", th_style), Paragraph("<b>Course Outcome Statement (Upon completion, students will be able to...)</b>", th_style)],
        [Paragraph("<b>CO1</b>", tcb_style), Paragraph("Understand fundamental research concepts, paradigms, and identify engineering problems.", tc_style)],
        [Paragraph("<b>CO2</b>", tcb_style), Paragraph("Formulate research problems, define SMART objectives, and establish verifiable hypotheses.", tc_style)],
        [Paragraph("<b>CO3</b>", tcb_style), Paragraph("Conduct structured literature surveys, discover research gaps, and perform basic statistical data analysis.", tc_style)],
        [Paragraph("<b>CO4</b>", tcb_style), Paragraph("Apply ethical research standards, prevent plagiarism, and draft mock patent specifications.", tc_style)],
        [Paragraph("<b>CO5</b>", tcb_style), Paragraph("Analyze different forms of Intellectual Property Rights (Patents, Trademarks, Copyrights, Trade Secrets).", tc_style)],
        [Paragraph("<b>CO6</b>", tcb_style), Paragraph("Evaluate patent procedures, technology transfer mechanisms, licensing models, and commercialization cases.", tc_style)]
    ]
    co_table = Table(co_data, colWidths=[42, 481])
    co_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6)
    ]))
    story.append(co_table)

    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Practical Continuous Assessment Index</b>", h2_style))

    index_data = [
        [Paragraph("<b>Exp</b>", th_style),
         Paragraph("<b>Title of Experiment</b>", th_style),
         Paragraph("<b>Mapped CO & BL</b>", th_style),
         Paragraph("<b>Date of Perf.</b>", th_style),
         Paragraph("<b>Marks (10)</b>", th_style),
         Paragraph("<b>Faculty Sign</b>", th_style)],
        
        [Paragraph("<b>1</b>", tcb_style),
         Paragraph("Identify & Formulate a Research Problem with SMART Objectives & Hypotheses", tc_style),
         Paragraph("CO2 | BL4 (Analyze)", tc_style),
         Paragraph("", tc_style), Paragraph("", tc_style), Paragraph("", tc_style)],

        [Paragraph("<b>2</b>", tcb_style),
         Paragraph("Conduct a Structured Literature Review (Scopus/Scholar) & Propose Methodology", tc_style),
         Paragraph("CO3 | BL4 (Analyze)", tc_style),
         Paragraph("", tc_style), Paragraph("", tc_style), Paragraph("", tc_style)],

        [Paragraph("<b>3</b>", tcb_style),
         Paragraph("Collect Sample Research Data & Perform Basic Descriptive Statistical Analysis", tc_style),
         Paragraph("CO3 | BL3 (Apply)", tc_style),
         Paragraph("", tc_style), Paragraph("", tc_style), Paragraph("", tc_style)],

        [Paragraph("<b>4</b>", tcb_style),
         Paragraph("Prepare a Plagiarism-Free Research Document & Evaluate Plagiarism Report", tc_style),
         Paragraph("CO4 | BL5 (Evaluate)", tc_style),
         Paragraph("", tc_style), Paragraph("", tc_style), Paragraph("", tc_style)],

        [Paragraph("<b>5</b>", tcb_style),
         Paragraph("Perform Patent Search (Google Patents/InPASS) & Draft Mock Patent Specification", tc_style),
         Paragraph("CO4 | BL6 (Create)", tc_style),
         Paragraph("", tc_style), Paragraph("", tc_style), Paragraph("", tc_style)],

        [Paragraph("<b>6</b>", tcb_style),
         Paragraph("Analyze a Real-World IPR / Technology Commercialization Case Study", tc_style),
         Paragraph("CO4 | BL5 (Evaluate)", tc_style),
         Paragraph("", tc_style), Paragraph("", tc_style), Paragraph("", tc_style)]
    ]
    index_table = Table(index_data, colWidths=[28, 240, 75, 55, 50, 75])
    index_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5)
    ]))
    story.append(index_table)

    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Core Laboratory Guidelines & Safety Protocol:</b>", h2_style))
    story.append(Paragraph("• <b>Academic Integrity:</b> All data tables, citations, and patent analyses must reflect authentic scholarly work.", bullet_style))
    story.append(Paragraph("• <b>Modern Tool Usage:</b> Use Google Scholar, Scopus, Mendeley/Zotero, MS Excel/Python, InPASS, and WIPO PATENTSCOPE.", bullet_style))
    story.append(Paragraph("• <b>Documentation:</b> Maintain complete observation matrices, statistical computations, and viva responses.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: EXPERIMENT 1
    # =========================================================================
    story.append(make_header_banner(1, "Research Problem & Hypothesis Formulation", "CO2 | BL4 (Analyze) | 2 Hrs"))
    story.append(Spacer(1, 4))
    story.append(make_aim_box("To identify a real-world engineering problem, formulate a concise research problem statement, define SMART research objectives, and establish testable research hypotheses with identified independent and dependent variables."))
    story.append(Spacer(1, 4))

    story.append(Paragraph("1. Theoretical Summary (Key Concepts)", h2_style))
    story.append(Paragraph("• <b>Research Problem:</b> A specific knowledge gap, contradiction, or technical limitation in engineering that requires systematic investigation.", bullet_style))
    story.append(Paragraph("• <b>Problem Statement vs. Research Problem:</b> A problem statement describes the operational symptom; a research problem frames it into an investigable inquiry.", bullet_style))
    story.append(Paragraph("• <b>SMART Objectives:</b> <b>S</b>pecific (unambiguous), <b>M</b>easurable (quantified), <b>A</b>chievable (feasible), <b>R</b>elevant (addresses gap), <b>T</b>ime-bound (scheduled).", bullet_style))
    story.append(Paragraph("• <b>Variables:</b> <i>Independent Variable (IV)</i> is altered by the researcher (e.g., ML algorithm); <i>Dependent Variable (DV)</i> is measured (e.g., accuracy, latency).", bullet_style))
    story.append(Paragraph("• <b>Hypotheses:</b> <i>Null (H<sub>0</sub>):</i> Predicts no significant effect/difference. <i>Alternative (H<sub>1</sub>):</i> Predicts a statistically significant performance improvement.", bullet_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("2. Step-by-Step Procedure", h2_style))
    story.append(Paragraph("<b>Step 1:</b> Select an engineering domain (e.g., Railway Systems, IoT, Vision). &nbsp;|&nbsp; <b>Step 2:</b> Identify operational pain points & limitations.<br/>"
                           "<b>Step 3:</b> Draft a concise problem statement detailing consequence. &nbsp;|&nbsp; <b>Step 4:</b> Formulate 1 general & 3–4 SMART specific objectives.<br/>"
                           "<b>Step 5:</b> Map independent/dependent variables and state testable H<sub>0</sub> and H<sub>1</sub> propositions.", body_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("3. Engineering Case Study: Railway Track Fault Detection System", h2_style))
    cs1_data = [
        [Paragraph("<b>Component</b>", th_style), Paragraph("<b>Engineering Exemplar Description</b>", th_style)],
        [Paragraph("<b>Domain & Topic</b>", tcb_style), Paragraph("Railway Infrastructure Safety — Vision-Based Real-Time Track Fracture Classification.", tc_style)],
        [Paragraph("<b>Problem Statement</b>", tcb_style), Paragraph("Manual track inspections are slow, labor-intensive, and prone to human oversight, leading to undetected micro-fractures, derailment hazards, and schedule disruptions.", tc_style)],
        [Paragraph("<b>General Objective</b>", tcb_style), Paragraph("To develop an automated, computer vision-based railway track fault detection system utilizing deep convolutional networks for high-speed anomaly identification.", tc_style)],
        [Paragraph("<b>Specific Objectives</b>", tcb_style), Paragraph("1. Curate a benchmark multi-weather railway track surface image dataset.<br/>2. Extract morphological and textural defect features via edge-filtering.<br/>3. Train and tune CNN and SVM classification architectures.<br/>4. Benchmark inference latency and classification accuracy against manual standards.", tc_style)],
        [Paragraph("<b>Variables & Hypotheses</b>", tcb_style), Paragraph("<b>IV:</b> Classifier model type (CNN vs. SVM) &nbsp;|&nbsp; <b>DV:</b> Fault detection accuracy (%), F1-Score.<br/><b>H<sub>0</sub>:</b> Deep learning algorithms do not significantly increase crack detection accuracy over manual inspection.<br/><b>H<sub>1</sub>:</b> Deep learning algorithms yield a statistically significant improvement in accuracy (>95%) over manual inspection.", tc_style)]
    ]
    cs1_table = Table(cs1_data, colWidths=[95, 428])
    cs1_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4)
    ]))
    story.append(cs1_table)

    story.append(Spacer(1, 3))
    story.append(Paragraph("4. Student Observation & Formulation Template", h2_style))
    obs1_data = [
        [Paragraph("<b>Parameter</b>", th_style), Paragraph("<b>Student Formulation Details (To be completed for chosen topic)</b>", th_style)],
        [Paragraph("<b>Selected Topic</b>", tcb_style), Paragraph("", tc_style)],
        [Paragraph("<b>Research Problem</b>", tcb_style), Paragraph("", tc_style)],
        [Paragraph("<b>Objectives (SMART)</b>", tcb_style), Paragraph("Gen:<br/>Spec: 1. &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2.", tc_style)],
        [Paragraph("<b>Hypotheses</b>", tcb_style), Paragraph("H<sub>0</sub>:<br/>H<sub>1</sub>:", tc_style)]
    ]
    obs1_table = Table(obs1_data, colWidths=[95, 428])
    obs1_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4)
    ]))
    story.append(obs1_table)

    story.append(Spacer(1, 3))
    story.append(Paragraph("5. Result, Conclusion & Viva Voce", h2_style))
    story.append(Paragraph("<b>Result & Conclusion:</b> Successfully formulated a viable engineering research problem, defined 4 SMART objectives, mapped IV/DV variables, and derived falsifiable hypotheses.<br/>"
                           "<b>Key Viva Voce Q&amp;A:</b> <b>Q1:</b> Why must a hypothesis be falsifiable? <i>Ans: To ensure it can be empirically tested and rejected using reproducible experimental data.</i> &nbsp;|&nbsp; <b>Q2:</b> What is a specific objective? <i>Ans: An actionable, quantifiable milestone directly contributing to the general objective.</i>", body_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: EXPERIMENT 2
    # =========================================================================
    story.append(make_header_banner(2, "Structured Literature Review & Methodology", "CO3 | BL4 (Analyze) | 2 Hrs"))
    story.append(Spacer(1, 4))
    story.append(make_aim_box("To conduct a structured literature survey across scholarly databases (Scopus, Google Scholar), synthesize findings into an analytical matrix, identify distinct research gaps, and propose an appropriate end-to-end research methodology."))
    story.append(Spacer(1, 4))

    story.append(Paragraph("1. Theoretical Summary (Key Concepts)", h2_style))
    story.append(Paragraph("• <b>Literature Review:</b> Systematic synthesis of peer-reviewed articles to establish state-of-the-art and avoid rediscovering known solutions.", bullet_style))
    story.append(Paragraph("• <b>Databases:</b> <b>Scopus</b> provides vetted, peer-reviewed indexing, citation tracking, and h-index metrics. <b>Google Scholar</b> is an open academic search engine indexing preprints, theses, and conference papers.", bullet_style))
    story.append(Paragraph("• <b>Boolean Queries:</b> Combine keywords using `AND`, `OR`, `NOT`: e.g., <code>(\"railway track\" OR \"rail inspection\") AND (\"machine learning\" OR \"CNN\") AND (\"crack detection\")</code>.", bullet_style))
    story.append(Paragraph("• <b>Research Gap Types:</b> <i>Knowledge Gap</i> (unexplored phenomenon), <i>Methodological Gap</i> (outdated/limited algorithm), <i>Data Gap</i> (lack of benchmark datasets), and <i>Practical Gap</i> (lack of real-time edge deployment).", bullet_style))
    story.append(Paragraph("• <b>Literature Matrix:</b> Tabular synthesis comparing Author/Year, Proposed Methodology, Dataset, Accuracy, and Limitations.", bullet_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("2. Step-by-Step Procedure", h2_style))
    story.append(Paragraph("<b>Step 1:</b> Define keywords and build multi-clause Boolean queries. &nbsp;|&nbsp; <b>Step 2:</b> Query Scopus & Google Scholar (past 3–5 years).<br/>"
                           "<b>Step 3:</b> Screen titles/abstracts to select benchmark papers. &nbsp;|&nbsp; <b>Step 4:</b> Populate the literature review matrix.<br/>"
                           "<b>Step 5:</b> Synthesize unresolved limitations into research gaps. &nbsp;|&nbsp; <b>Step 6:</b> Formulate an 8-stage research methodology pipeline.", body_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("3. Sample Literature Review Matrix (Railway Track Defect Detection)", h2_style))
    mat_data = [
        [Paragraph("<b>Paper / Author</b>", th_style),
         Paragraph("<b>Year</b>", th_style),
         Paragraph("<b>Methodology</b>", th_style),
         Paragraph("<b>Dataset & Size</b>", th_style),
         Paragraph("<b>Accuracy</b>", th_style),
         Paragraph("<b>Key Limitation / Research Gap</b>", th_style)],

        [Paragraph("Zhang et al.", tcb_style), Paragraph("2022", tc_style), Paragraph("Support Vector Machine (SVM)", tc_style), Paragraph("1,200 Static Images", tc_style), Paragraph("91.8%", tc_style), Paragraph("Sensitive to illumination variations; high manual feature overhead.", tc_style)],
        [Paragraph("Kumar & Singh", tcb_style), Paragraph("2023", tc_style), Paragraph("Custom CNN (ResNet-18)", tc_style), Paragraph("3,500 Track Photos", tc_style), Paragraph("95.4%", tc_style), Paragraph("Small dataset lacking motion blur; no vibration sensor fusion.", tc_style)],
        [Paragraph("Patel et al.", tcb_style), Paragraph("2024", tc_style), Paragraph("YOLOv8 Object Detection", tc_style), Paragraph("6,000 Video Frames", tc_style), Paragraph("97.2%", tc_style), Paragraph("High false positives on rusted rails; heavy edge compute load.", tc_style)],
        [Paragraph("Al-Mansoor et al.", tcb_style), Paragraph("2024", tc_style), Paragraph("Hybrid CNN-LSTM", tc_style), Paragraph("Multi-Sensor Logs", tc_style), Paragraph("98.1%", tc_style), Paragraph("Complex model with high training latency; real-time deployment untested.", tc_style)]
    ]
    mat_table = Table(mat_data, colWidths=[78, 30, 92, 85, 45, 193])
    mat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (4, 0), (4, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4)
    ]))
    story.append(mat_table)

    story.append(Spacer(1, 3))
    story.append(Paragraph("4. Research Gap Extraction & Proposed Methodology Pipeline", h2_style))
    story.append(Paragraph("• <b>Identified Gaps:</b> (1) Lack of multi-modal data fusion (combining visual imagery with vibration/acoustic logs); (2) Absence of quantized lightweight models for low-power onboard embedded edge hardware.<br/>"
                           "• <b>Proposed 8-Stage Research Methodology:</b><br/>"
                           "<code>Problem Definition → Scholarly Survey → Gap Mapping → Multi-Modal Data Acquisition → Preprocessing & Filtering → Lightweight Model Design (Quantized MobileNet/CNN) → Onboard Edge Validation → Benchmark Evaluation</code>", body_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("5. Result, Conclusion & Viva Voce", h2_style))
    story.append(Paragraph("<b>Result & Conclusion:</b> Successfully conducted a literature survey on Scopus & Scholar, synthesized benchmarks in a matrix, extracted 2 research gaps, and proposed an 8-stage methodology.<br/>"
                           "<b>Key Viva Voce Q&amp;A:</b> <b>Q1:</b> What is the main advantage of Scopus over Google Scholar? <i>Ans: Scopus applies strict peer-reviewed indexing standards.</i> &nbsp;|&nbsp; <b>Q2:</b> What is a Methodological Gap? <i>Ans: When existing research uses outdated or computationally prohibitive algorithms.</i>", body_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: EXPERIMENT 3
    # =========================================================================
    story.append(make_header_banner(3, "Sample Data Collection & Statistical Analysis", "CO3 | BL3 (Apply) | 2 Hrs"))
    story.append(Spacer(1, 4))
    story.append(make_aim_box("To collect experimental research data, organize it systematically in tabular format, compute descriptive statistical measures (central tendency and dispersion), and interpret research trends using graphical visualizations."))
    story.append(Spacer(1, 4))

    story.append(Paragraph("1. Theoretical Summary (Key Concepts)", h2_style))
    story.append(Paragraph("• <b>Primary vs. Secondary Data:</b> Primary data is gathered firsthand (sensors, experiments, surveys); secondary data comes from existing repositories (Kaggle, reports).", bullet_style))
    story.append(Paragraph("• <b>Central Tendency Measures:</b><br/>"
                           "- <i>Sample Mean (x):</i> Arithmetic average: Mean = (∑ x) / n &nbsp;|&nbsp; <i>Median:</i> Middle value when sorted in ascending order (robust to outliers).<br/>"
                           "- <i>Mode:</i> Most frequently occurring observation in the dataset.", bullet_style))
    story.append(Paragraph("• <b>Dispersion Measures:</b><br/>"
                           "- <i>Range:</i> Difference between Maximum and Minimum values: Range = Max(X) − Min(X).<br/>"
                           "- <i>Sample Variance (s<sup>2</sup>):</i> Average squared deviation from the mean: s<sup>2</sup> = [∑ (x − Mean)<sup>2</sup>] / (n − 1)<br/>"
                           "- <i>Standard Deviation (s):</i> Spread of data around the mean: s = √(s<sup>2</sup>).", bullet_style))
    story.append(Paragraph("• <b>Visualization:</b> Histograms display frequency distribution; Box Plots highlight median, quartiles, and outliers; Scatter Plots show bivariate correlation.", bullet_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("2. Step-by-Step Procedure", h2_style))
    story.append(Paragraph("<b>Step 1:</b> Define study metric (e.g., student marks, latency). &nbsp;|&nbsp; <b>Step 2:</b> Collect sample observations (N = 10–20).<br/>"
                           "<b>Step 3:</b> Tabulate entries in Excel / Python Pandas. &nbsp;|&nbsp; <b>Step 4:</b> Compute Mean, Median, Mode, Range, Variance, and Std Dev.<br/>"
                           "<b>Step 5:</b> Plot distribution charts (Histograms/Bar charts). &nbsp;|&nbsp; <b>Step 6:</b> Interpret dispersion, skewness, and clustering.", body_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("3. Engineering Case Study: Student Performance Dataset & Computed Analysis", h2_style))
    stat_data = [
        [Paragraph("<b>Sample Dataset (Student ML Scores, N=10)</b>", th_style),
         Paragraph("<b>Descriptive Metric</b>", th_style),
         Paragraph("<b>Formula Applied</b>", th_style),
         Paragraph("<b>Computed Value</b>", th_style)],

        [Paragraph("Student A: 72 &nbsp;|&nbsp; Student F: 84<br/>"
                   "Student B: 81 &nbsp;|&nbsp; Student G: 69<br/>"
                   "Student C: 65 &nbsp;|&nbsp; Student H: 88<br/>"
                   "Student D: 90 &nbsp;|&nbsp; Student I: 75<br/>"
                   "Student E: 78 &nbsp;|&nbsp; Student J: 80", tc_style),
         Paragraph("<b>Sample Mean (x)<br/>Median<br/>Mode<br/>Min / Max<br/>Range<br/>Variance (s<sup>2</sup>)<br/>Std Dev (s)</b>", tc_style),
         Paragraph("∑ x / n<br/>(n+1)/2 th position<br/>Most frequent value<br/>min(X) / max(X)<br/>Max − Min<br/>∑(x − Mean)<sup>2</sup> / (n−1)<br/>√(s<sup>2</sup>)", tc_style),
         Paragraph("<b>78.20</b><br/><b>79.00</b><br/><b>None</b> (All unique)<br/><b>65.00 / 90.00</b><br/><b>25.00</b><br/><b>58.40</b><br/><b>7.64</b>", tc_style)]
    ]
    stat_table = Table(stat_data, colWidths=[160, 95, 155, 113])
    stat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4)
    ]))
    story.append(stat_table)

    story.append(Spacer(1, 3))
    story.append(Paragraph("4. Statistical Interpretation & Inference", h2_style))
    story.append(Paragraph("• <b>Central Tendency:</b> The mean (78.20) and median (79.00) are nearly identical, demonstrating a symmetrical, bell-shaped distribution.<br/>"
                           "• <b>Dispersion:</b> The standard deviation of 7.64 marks reflects moderate, well-controlled variation.<br/>"
                           "• <b>Competency Level:</b> 80% of students achieved 72 marks or above, demonstrating high overall proficiency in the module.", body_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("5. Result, Conclusion & Viva Voce", h2_style))
    story.append(Paragraph("<b>Result & Conclusion:</b> Successfully gathered raw experimental data, structured it into a tabular dataset, calculated central tendency and dispersion metrics, and derived evidence-based engineering inferences.<br/>"
                           "<b>Key Viva Voce Q&amp;A:</b> <b>Q1:</b> When is Median preferred over Mean? <i>Ans: When the dataset has extreme outliers or heavy skewness.</i> &nbsp;|&nbsp; <b>Q2:</b> Why divide by (n−1) in sample variance? <i>Ans: Bessel's correction provides an unbiased estimator of true population variance.</i>", body_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: EXPERIMENT 4
    # =========================================================================
    story.append(make_header_banner(4, "Plagiarism-Free Research Documentation", "CO4 | BL5 (Evaluate) | 2 Hrs"))
    story.append(Spacer(1, 4))
    story.append(make_aim_box("To compose an original, plagiarism-free engineering research manuscript using standard referencing styles (IEEE/APA) with reference management tools, and evaluate document originality using similarity detection software."))
    story.append(Spacer(1, 4))

    story.append(Paragraph("1. Theoretical Summary (Key Concepts)", h2_style))
    story.append(Paragraph("• <b>Plagiarism:</b> Unauthorized reproduction or appropriation of another author's language, thoughts, or technical data without attribution.", bullet_style))
    story.append(Paragraph("• <b>Forms of Plagiarism:</b> <i>Direct</i> (verbatim copy without quotes), <i>Mosaic</i> (patchwork paraphrasing), <i>Self-Plagiarism</i> (re-using own work), <i>Accidental</i> (incorrect citations).", bullet_style))
    story.append(Paragraph("• <b>Citation Standards:</b> <b>IEEE Style</b> uses bracketed numbers sequenced by text appearance (`[1]`, `[2]`). <b>APA Style</b> uses author-date parenthetical citations (`(Smith, 2023)`).", bullet_style))
    story.append(Paragraph("• <b>Reference Managers:</b> <i>Mendeley, Zotero, EndNote</i> automate metadata ingestion, in-text citation placement, and bibliography formatting in MS Word / LaTeX.", bullet_style))
    story.append(Paragraph("• <b>Similarity Thresholds:</b> <b><10%:</b> Highly original (target for publication); <b>10%–20%:</b> Typical acceptable thesis threshold; <b>>20%:</b> Unacceptable similarity requiring substantive rewriting.", bullet_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("2. Step-by-Step Procedure", h2_style))
    story.append(Paragraph("<b>Step 1:</b> Draft a 2–3 page technical manuscript on an engineering topic. &nbsp;|&nbsp; <b>Step 2:</b> Embed IEEE in-text citations at factual claims.<br/>"
                           "<b>Step 3:</b> Auto-generate formatted bibliography via Mendeley/Zotero. &nbsp;|&nbsp; <b>Step 4:</b> Run document through Turnitin/Ouriginal.<br/>"
                           "<b>Step 5:</b> Inspect similarity clusters; paraphrase and quote directly copied text. &nbsp;|&nbsp; <b>Step 6:</b> Re-run detection to verify similarity drops below 10%.", body_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("3. Engineering Case Study: Plagiarism Remediation Report", h2_style))
    plag_data = [
        [Paragraph("<b>Evaluation Metric</b>", th_style),
         Paragraph("<b>Initial Draft</b>", th_style),
         Paragraph("<b>Remediation Action Applied</b>", th_style),
         Paragraph("<b>Final Revised Draft</b>", th_style)],

        [Paragraph("<b>Similarity Index (%)</b>", tcb_style), Paragraph("<font color='red'><b>32%</b></font>", tc_style), Paragraph("Paraphrased copied sentences; wrapped verbatim definitions in quotes.", tc_style), Paragraph("<font color='green'><b>9% (Approved)</b></font>", tc_style)],
        [Paragraph("<b>In-Text Citations</b>", tcb_style), Paragraph("5 citations", tc_style), Paragraph("Identified source authors and added 13 missing citations.", tc_style), Paragraph("18 citations", tc_style)],
        [Paragraph("<b>Missing References</b>", tcb_style), Paragraph("8 unlinked claims", tc_style), Paragraph("Imported complete DOI metadata into Mendeley.", tc_style), Paragraph("0 missing references", tc_style)],
        [Paragraph("<b>Originality Assessment</b>", tcb_style), Paragraph("Unacceptable", tc_style), Paragraph("Rephrased literature review using original analytical prose.", tc_style), Paragraph("<b>High Quality / Original</b>", tc_style)]
    ]
    plag_table = Table(plag_data, colWidths=[110, 75, 238, 100])
    plag_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4)
    ]))
    story.append(plag_table)

    story.append(Spacer(1, 3))
    story.append(Paragraph("4. Key Strategies for Avoiding Plagiarism in Research", h2_style))
    story.append(Paragraph("• <b>Original Synthesis:</b> Read multiple papers, synthesize their core ideas mentally, and write without looking at the original text.<br/>"
                           "• <b>Quotation Marks:</b> When using an author's exact phrase or statutory definition, enclose it in quotes and provide the citation immediately.<br/>"
                           "• <b>Automated Reference Management:</b> Use tools like Zotero or Mendeley to ensure citations match the final reference list perfectly.", body_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("5. Result, Conclusion & Viva Voce", h2_style))
    story.append(Paragraph("<b>Result & Conclusion:</b> Successfully authored an academic manuscript, integrated Mendeley-managed IEEE references, analyzed a Turnitin similarity report, and reduced the similarity index from 32% to 9%.<br/>"
                           "<b>Key Viva Voce Q&amp;A:</b> <b>Q1:</b> Does paraphrasing remove the need to cite? <i>Ans: No; the idea belongs to the original author and must be credited.</i> &nbsp;|&nbsp; <b>Q2:</b> Difference between citation and reference? <i>Ans: Citation indicates borrowed work in text; reference gives full bibliographic metadata at the end.</i>", body_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: EXPERIMENT 5
    # =========================================================================
    story.append(make_header_banner(5, "Patent Search & Mock Specification Drafting", "CO4 | BL6 (Create) | 2 Hrs"))
    story.append(Spacer(1, 4))
    story.append(make_aim_box("To conduct a prior art patent search using global patent databases (Google Patents, WIPO, InPASS), evaluate statutory patentability criteria, and draft a structured mock patent specification including patent claims for an innovative engineering invention."))
    story.append(Spacer(1, 4))

    story.append(Paragraph("1. Theoretical Summary (Key Concepts)", h2_style))
    story.append(Paragraph("• <b>Patent:</b> A statutory legal monopoly granted by a government to an inventor for a limited term (typically 20 years from filing) in exchange for complete public disclosure of the invention.", bullet_style))
    story.append(Paragraph("• <b>The Three Patentability Criteria:</b><br/>"
                           "1. <i>Novelty:</i> The invention must not exist in public domain or prior art anywhere in the world.<br/>"
                           "2. <i>Inventive Step (Non-Obviousness):</i> Technical advancement not obvious to a Person Having Ordinary Skill in the Art (PHOSITA).<br/>"
                           "3. <i>Industrial Applicability:</i> The invention must be capable of being manufactured or utilized industrially.", bullet_style))
    story.append(Paragraph("• <b>Prior Art:</b> Any publicly accessible technical disclosure—patents, journals, web articles, or commercial products—made anywhere in the world prior to the filing date.", bullet_style))
    story.append(Paragraph("• <b>Databases:</b> <i>Google Patents</i> (worldwide index), <i>WIPO PATENTSCOPE</i> (international PCT applications), <i>InPASS</i> (Indian Patent Office).", bullet_style))
    story.append(Paragraph("• <b>Patent Anatomy:</b> Title → Field → Background → Summary → Description → Drawings → <b>Claims</b> (the legal boundary of enforceable rights) → Abstract.", bullet_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("2. Step-by-Step Procedure", h2_style))
    story.append(Paragraph("<b>Step 1:</b> Define inventive concept & technical elements. &nbsp;|&nbsp; <b>Step 2:</b> Build search queries with IPC codes and Boolean operators.<br/>"
                           "<b>Step 3:</b> Search Google Patents & InPASS; retrieve prior art. &nbsp;|&nbsp; <b>Step 4:</b> Compile a Prior Art Analysis Table comparing technical features.<br/>"
                           "<b>Step 5:</b> Assess patentability (Novelty, Inventive Step, Utility). &nbsp;|&nbsp; <b>Step 6:</b> Author mock specification with independent & dependent claims.", body_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("3. Engineering Case Study: Prior Art Analysis & Mock Patent Draft", h2_style))
    pat_data = [
        [Paragraph("<b>Prior Art Patent No.</b>", th_style),
         Paragraph("<b>Title of Patent</b>", th_style),
         Paragraph("<b>Year</b>", th_style),
         Paragraph("<b>Technical Scope</b>", th_style),
         Paragraph("<b>Limitation / Differentiator</b>", th_style)],

        [Paragraph("US10234567B2", tcb_style), Paragraph("Railway Vibration Crack Monitor", tc_style), Paragraph("2021", tc_style), Paragraph("Acoustic vibration sensors placed on tracks.", tc_style), Paragraph("Cannot visually classify surface fractures or pinpoint exact coordinates.", tc_style)],
        [Paragraph("IN2023410123A", tcb_style), Paragraph("Track Visual Inspection Cart", tc_style), Paragraph("2023", tc_style), Paragraph("Trolley-mounted optical video camera.", tc_style), Paragraph("Requires offline manual video analysis; lacks real-time edge AI classification.", tc_style)],
        [Paragraph("WO202401987A1", tcb_style), Paragraph("Autonomous Rail Drone Scanner", tc_style), Paragraph("2024", tc_style), Paragraph("Drone vision inspection for railway yards.", tc_style), Paragraph("High cost; limited flight duration; unsuitable for long-distance mainline tracks.", tc_style)]
    ]
    pat_table = Table(pat_data, colWidths=[85, 125, 32, 120, 161])
    pat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4)
    ]))
    story.append(pat_table)

    story.append(Spacer(1, 3))
    story.append(Paragraph("4. Mock Patent Specification Extract (Student Deliverable)", h2_style))
    story.append(Paragraph("• <b>Title:</b> AI-Powered Real-Time Autonomous Railway Track Defect Detection and Geotagging System.<br/>"
                           "• <b>Field of Invention:</b> Railway Transportation Safety, Computer Vision, and Embedded Edge Computing.<br/>"
                           "• <b>Summary:</b> An automated inspection apparatus mounted to a locomotive that captures high-speed line-scan imagery, detects micro-cracks in real time using a quantized neural network, and transmits GPS-tagged maintenance alerts to a central rail traffic controller.<br/>"
                           "• <b>Claim 1 (Independent):</b> An automated railway track defect detection apparatus comprising: an optical line-scan camera mounted to a rail carriage chassis; an edge computing unit running a quantized convolutional neural network; and a cellular telemetry modem transmitting defect alerts with GPS coordinates.<br/>"
                           "• <b>Claim 2 (Dependent):</b> The apparatus of Claim 1, further comprising a pressurized spray nozzle actuated by the edge computing unit to deposit a visible thermal marker paint on detected crack locations.", body_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("5. Result, Conclusion & Viva Voce", h2_style))
    story.append(Paragraph("<b>Result & Conclusion:</b> Successfully conducted a prior art search across international patent databases, established patentability over existing prior art, and drafted a mock patent specification with independent and dependent claims.<br/>"
                           "<b>Key Viva Voce Q&amp;A:</b> <b>Q1:</b> Why are Claims considered the most important part of a patent? <i>Ans: Claims define the exact legal perimeter of protection; what is not claimed is not protected.</i> &nbsp;|&nbsp; <b>Q2:</b> What is the term of a patent in India? <i>Ans: 20 years from the international filing date, provided annual renewal fees are maintained.</i>", body_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: EXPERIMENT 6
    # =========================================================================
    story.append(make_header_banner(6, "IPR & Technology Commercialization Case Analysis", "CO4 | BL5 (Evaluate) | 2 Hrs"))
    story.append(Spacer(1, 4))
    story.append(make_aim_box("To analyze a real-world technology commercialization and IPR case study, evaluate the interplay between legal protections and engineering design constraints, and assess technology transfer pathways."))
    story.append(Spacer(1, 4))

    story.append(Paragraph("1. Theoretical Summary (Key Concepts)", h2_style))
    story.append(Paragraph("• <b>Forms of Intellectual Property:</b><br/>"
                           "- <i>Patents:</i> Protect functional inventions, hardware architectures, and novel algorithms (20 years).<br/>"
                           "- <i>Copyrights:</i> Protect source code, documentation, and user interfaces (Author's lifetime + 60 years).<br/>"
                           "- <i>Trademarks:</i> Protect brand names, logos, and market identity (Renewable every 10 years).<br/>"
                           "- <i>Trade Secrets:</i> Protect confidential formulas, training weights, and business strategies indefinitely.", bullet_style))
    story.append(Paragraph("• <b>Technology Commercialization Lifecycle:</b> Basic Research (TRL 1–3) → Proof-of-Concept & Prototyping (TRL 4–5) → IP Filing → Technology Transfer / Licensing (TRL 6–7) → Regulatory Approval → Market Launch (TRL 8–9).", bullet_style))
    story.append(Paragraph("• <b>Modes of Technology Transfer:</b><br/>"
                           "- <i>Exclusive Licensing:</i> Sole commercial exploitation rights granted to one industrial partner.<br/>"
                           "- <i>Non-Exclusive Licensing:</i> Rights licensed concurrently to multiple commercial vendors.<br/>"
                           "- <i>Spin-Off / Academic Startup:</i> Inventors establish an independent enterprise with university equity sharing.", bullet_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("2. Step-by-Step Procedure", h2_style))
    story.append(Paragraph("<b>Step 1:</b> Select a commercialization case (e.g., AI Diagnostic Imaging). &nbsp;|&nbsp; <b>Step 2:</b> Map IP assets (Patents, Copyrights, Trademarks).<br/>"
                           "<b>Step 3:</b> Trace transition from laboratory prototype to market product. &nbsp;|&nbsp; <b>Step 4:</b> Evaluate engineering trade-offs made for regulatory compliance.<br/>"
                           "<b>Step 5:</b> Assess licensing agreements, royalties, and data privacy. &nbsp;|&nbsp; <b>Step 6:</b> Formulate risk-mitigation strategies for technical entrepreneurs.", body_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("3. Engineering Case Study: Commercialization of AI Healthcare Diagnostics", h2_style))
    ipr_data = [
        [Paragraph("<b>Domain / Factor</b>", th_style),
         Paragraph("<b>Engineering Implications</b>", th_style),
         Paragraph("<b>Legal & IPR Implications</b>", th_style)],

        [Paragraph("<b>Intellectual Property Protection</b>", tcb_style),
         Paragraph("Developing modular software codebases; separating open-source libraries from proprietary neural network weights.", tc_style),
         Paragraph("Filing patents on novel feature attention mechanisms; registering source code copyright; trademarking brand names.", tc_style)],

        [Paragraph("<b>Regulatory Approval (CDSCO / FDA)</b>", tcb_style),
         Paragraph("Designing explainable AI (XAI) overlays and conducting multi-site clinical validation trials.", tc_style),
         Paragraph("Complying with Software as a Medical Device (SaMD) regulatory standards; securing ISO 13485 certification.", tc_style)],

        [Paragraph("<b>Technology Transfer & Licensing</b>", tcb_style),
         Paragraph("Refactoring code for integration with hospital PACS and DICOM medical imaging protocols.", tc_style),
         Paragraph("Drafting exclusive technology licensing agreements with milestone-based royalty and equity splits.", tc_style)],

        [Paragraph("<b>Data Privacy & Liability</b>", tcb_style),
         Paragraph("Implementing on-premise federated learning to avoid transmitting raw patient radiological scans off-site.", tc_style),
         Paragraph("Ensuring adherence to the Digital Personal Data Protection (DPDP) Act; establishing indemnity clauses against misdiagnoses.", tc_style)]
    ]
    ipr_table = Table(ipr_data, colWidths=[115, 204, 204])
    ipr_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4)
    ]))
    story.append(ipr_table)

    story.append(Spacer(1, 3))
    story.append(Paragraph("4. Student Case Analysis Template", h2_style))
    story.append(Paragraph("• <b>Case Selected:</b> __________________________________________________________________________________<br/>"
                           "• <b>Primary IP Assets:</b> [ ] Patent &nbsp;&nbsp; [ ] Software Copyright &nbsp;&nbsp; [ ] Trademark &nbsp;&nbsp; [ ] Trade Secret<br/>"
                           "• <b>Commercialization Pathway:</b> [ ] Direct Startup &nbsp;&nbsp; [ ] Exclusive License &nbsp;&nbsp; [ ] Joint Venture<br/>"
                           "• <b>Key Technical Risk:</b> ____________________________________ &nbsp;|&nbsp; <b>Key Legal Risk:</b> ____________________________________", body_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("5. Result, Conclusion & Viva Voce", h2_style))
    story.append(Paragraph("<b>Result & Conclusion:</b> Successfully analyzed a real-world technology commercialization case study, evaluated the relationship between engineering architecture and legal requirements, and examined tech transfer licensing structures.<br/>"
                           "<b>Key Viva Voce Q&amp;A:</b> <b>Q1:</b> What is the difference between technology transfer and direct commercialization? <i>Ans: Tech transfer licenses IP to industrial partners; direct commercialization builds an in-house startup.</i> &nbsp;|&nbsp; <b>Q2:</b> What is an Exclusive License? <i>Ans: A license granting sole commercial rights, protecting investor capital during scale-up.</i>", body_style))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Document successfully created at: {output_pdf_path}")


if __name__ == "__main__":
    output_path = r"e:\Capstone_MITCORER\other_coursework\Research_Methodology_and_IPR_Lab_Manual.pdf"
    create_manual(output_path)
