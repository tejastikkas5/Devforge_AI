import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "DevForge AI — Product Requirements Document (PRD)")
            self.drawRightString(612 - 54, 755, "Heterogeneous Multi-Agent Architecture & RAG")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 612 - 54, 747)
            
        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawString(54, 36, "Confidential — DevForge AI Engineering Team")
        self.drawRightString(612 - 54, 36, page_str)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 612 - 54, 48)
        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#0F172A")      # Slate 900
    c_secondary = colors.HexColor("#1E40AF")    # Blue 800
    c_accent = colors.HexColor("#2563EB")       # Blue 600
    c_dark = colors.HexColor("#1E293B")         # Slate 800
    c_muted = colors.HexColor("#475569")        # Slate 600
    c_bg_light = colors.HexColor("#F8FAFC")     # Slate 50
    c_border = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=c_primary,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_secondary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_dark,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12.5,
        textColor=c_dark
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=c_dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=c_dark
    )

    story = []

    # Title Block
    story.append(Paragraph("DEVFORGE AI — PRODUCT REQUIREMENTS DOCUMENT", title_style))
    story.append(Paragraph("Autonomous, Enterprise-Grade Multi-Agent Software Development Platform with Heterogeneous Model Routing & Production RAG", subtitle_style))
    
    # Metadata Table
    meta_data = [
        [
            Paragraph("<b>Project:</b> DevForge AI", table_cell_style),
            Paragraph("<b>Date:</b> October 2026", table_cell_style),
            Paragraph("<b>Status:</b> Complete Engineering PRD", table_cell_style)
        ],
        [
            Paragraph("<b>Authors:</b> Tejas Tikkas, Rohan Umbarkar, Hrutik Sawant, Vivek Ingole", table_cell_style),
            Paragraph("<b>Domain:</b> Multi-Agent Systems & Local Code RAG", table_cell_style),
            Paragraph("<b>Target Runtime:</b> Local Ollama & Workstations", table_cell_style)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[200, 150, 154])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary & Core Identity", h1_style))
    story.append(Paragraph(
        "Modern cloud-based AI code assistants (GitHub Copilot, Cursor, Devin) rely on centralized APIs like GPT-4o and Claude 3.5. "
        "This creates prohibitive operational barriers for enterprises: exponential token costs ($20k-$100k+/year), zero code privacy "
        "in regulated environments (Finance, Defense, Healthcare), and severe attention loss across large multi-file projects. "
        "<b>DevForge AI</b> is a 100% private, air-gapped software engineering desktop platform powered by local open-weight LLMs via <b>Ollama</b>. "
        "It introduces a native <b>Supervisor/Orchestrator architecture</b> that manages an autonomous pipeline: Planner, Coder, Tester, and Debugger.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # 2. The Catch & Technical Realities
    story.append(Paragraph("2. The Problem Statement & The \"Catch\" in Current Implementations", h1_style))
    story.append(Paragraph(
        "<b>The Catch in Current Code:</b> In the baseline prototype of DevForge AI, all specialized agents (Planner, Coder, Tester, Debugger) "
        "are hardcoded to a single small model (<code>qwen2.5-coder:1.5b</code>). Furthermore, workspace context is passed via basic directory walks, "
        "leaving the built-in Abstract Syntax Tree (AST) analyzer unlinked and vector retrieval unimplemented.",
        body_style
    ))
    
    catch_box = [
        [Paragraph("<b>Identified Engineering Bottlenecks & Required Evolution:</b><br/>"
                   "• <b>The Single-Model Inefficiency:</b> A 1.5B/7B model lacks multi-file architectural reasoning for planning, while a large 16B/24B model is too slow for simple unit test boilerplate.<br/>"
                   "• <b>Missing RAG Synthesis:</b> Without structural AST skeletons and semantic vector search, agents hallucinate cross-file symbols and duplicate classes.<br/>"
                   "• <b>The Solution:</b> Decouple model assignment to enable <b>Dynamic Heterogeneous Routing</b> (e.g. Qwen2.5 for planning, Codestral for synthesis, CodeGemma for tests, Devstral for bug-fixing) and embed production <b>AST + Vector RAG</b> into the Supervisor pipeline.",
                   callout_style)]
    ]
    t_catch = Table(catch_box, colWidths=[504])
    t_catch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#93C5FD")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_catch)
    story.append(Spacer(1, 10))

    # 3. System Architecture & Flow Diagram
    story.append(Paragraph("3. System Architecture & Multi-Agent Flow", h1_style))
    story.append(Paragraph(
        "The core orchestrator receives the developer prompt, gathers workspace intelligence through the RAG layer, dynamically routes "
        "tasks to specialized agents running tailored Ollama models, and closes the loop with an automated execution sandbox.",
        body_style
    ))

    flow_img_path = r"E:\Capstone_MITCORER\docs\prd\Flow.png"
    if os.path.exists(flow_img_path):
        # Image is 422x607. Scale to width 230pt (height ~331pt)
        img_flow = RLImage(flow_img_path, width=220, height=316)
        
        arch_desc = [
            Paragraph("<b>Supervisor & Agent Flow Breakdown:</b>", h2_style),
            Paragraph("<b>1. User Prompt:</b> Enters through the high-performance PySide6 desktop interface.", body_style),
            Paragraph("<b>2. Supervisor / Orchestrator:</b> Central brain that classifies intent (chat vs coding), enriches context, and coordinates downstream agents.", body_style),
            Paragraph("<b>3. Specialized Agents:</b><br/>"
                      "• <b>Planning Agent:</b> Decomposes task into implementation steps.<br/>"
                      "• <b>Research Agent:</b> Scours project AST and docs.<br/>"
                      "• <b>Coding Agent:</b> Synthesizes modular, clean source code.<br/>"
                      "• <b>Testing Agent:</b> Generates automated unit test suites.<br/>"
                      "• <b>Review Agent:</b> Checks security and style compliance.<br/>"
                      "• <b>Debugging Agent:</b> Auto-fixes test failures.", body_style),
            Paragraph("<b>4. RAG Layer:</b> AST structural extraction + local embeddings.", body_style),
            Paragraph("<b>5. Model Selection:</b> Routes tasks to optimal local Ollama LLMs.", body_style),
            Paragraph("<b>6. Final Software:</b> Executed, verified, and saved to disk.", body_style)
        ]
        
        layout_data = [[img_flow, arch_desc]]
        t_layout = Table(layout_data, colWidths=[230, 274])
        t_layout.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (1,0), (1,0), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(t_layout)
    story.append(Spacer(1, 10))

    # Page Break for Phase Roadmap & Detailed Specs
    story.append(PageBreak())

    # 4. Project Phases & Timeline
    story.append(Paragraph("4. Project Phases & Implementation Timeline", h1_style))
    story.append(Paragraph(
        "The project follows a structured 7-phase execution roadmap from initial literature survey through to platform deployment and research paper publication.",
        body_style
    ))

    phases_img_path = r"E:\Capstone_MITCORER\docs\prd\phases.png"
    if os.path.exists(phases_img_path):
        # Image is 861x381. Scale to fit width 504 (height ~223)
        img_phases = RLImage(phases_img_path, width=504, height=223)
        story.append(img_phases)
        story.append(Spacer(1, 8))

    # 5. Heterogeneous Model Routing Matrix
    story.append(Paragraph("5. Dynamic Heterogeneous Model Routing Matrix", h1_style))
    story.append(Paragraph(
        "To achieve maximum software engineering performance on local hardware, DevForge AI dynamically assigns distinct models "
        "tailored to task requirements rather than utilizing a single monolithic model.",
        body_style
    ))

    model_table_data = [
        [
            Paragraph("Agent Role", table_header_style),
            Paragraph("Optimal Model", table_header_style),
            Paragraph("Lightweight Model", table_header_style),
            Paragraph("Task Focus & Capability Justification", table_header_style)
        ],
        [
            Paragraph("<b>Supervisor / Router</b>", table_cell_style),
            Paragraph("qwen2.5-coder:7b", table_cell_bold),
            Paragraph("qwen2.5-coder:1.5b", table_cell_style),
            Paragraph("Fast classification, zero-latency intent detection, prompt routing.", table_cell_style)
        ],
        [
            Paragraph("<b>Planner Agent</b>", table_cell_style),
            Paragraph("deepseek-coder-v2:16b", table_cell_bold),
            Paragraph("qwen2.5-coder:7b", table_cell_style),
            Paragraph("Long-range system decomposition, multi-file dependency structuring.", table_cell_style)
        ],
        [
            Paragraph("<b>Coder Agent</b>", table_cell_style),
            Paragraph("codestral:22b", table_cell_bold),
            Paragraph("qwen2.5-coder:7b", table_cell_style),
            Paragraph("High FIM (Fill-In-The-Middle) accuracy, clean markdown syntax, zero hallucinations.", table_cell_style)
        ],
        [
            Paragraph("<b>Tester Agent</b>", table_cell_style),
            Paragraph("codegemma:7b", table_cell_bold),
            Paragraph("qwen2.5-coder:1.5b", table_cell_style),
            Paragraph("High-throughput assertion synthesis, boundary condition coverage, mocking.", table_cell_style)
        ],
        [
            Paragraph("<b>Debugger Agent</b>", table_cell_style),
            Paragraph("devstral:24b", table_cell_bold),
            Paragraph("qwen2.5-coder:7b", table_cell_style),
            Paragraph("Deep compiler trace diagnosis, in-place AST refactoring, diff healing.", table_cell_style)
        ]
    ]

    t_models = Table(model_table_data, colWidths=[95, 105, 95, 209])
    t_models.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_models)
    story.append(Spacer(1, 10))

    # 6. Production Code RAG
    story.append(Paragraph("6. Production Code RAG: AST + Vector Hybrid Architecture", h1_style))
    story.append(Paragraph(
        "Standard RAG chunking breaks on source code because arbitrary token splits truncate functions and classes. "
        "DevForge AI implements a <b>hybrid syntax-aware retrieval engine</b>:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Structural AST Extraction:</b> <code>CodeASTAnalyzer</code> (built on Python's <code>ast</code> module) extracts class names, docstrings, method parameter signatures, and imported symbols into a compressed outline requiring &lt;15% of raw source tokens.<br/>"
        "• <b>Semantic Vector Chunker:</b> Chunks code along function/class boundaries and indexes them using local Ollama embeddings (<code>nomic-embed-text</code>), enabling semantic search across multi-file repositories.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # Page Break for Requirements & Acceptance Criteria
    story.append(PageBreak())

    # 7. Functional Requirements & Acceptance Criteria
    story.append(Paragraph("7. Functional Requirements & Engineering Triage (P0 / P1 / P2)", h1_style))
    
    fr_table_data = [
        [
            Paragraph("ID", table_header_style),
            Paragraph("Feature Name", table_header_style),
            Paragraph("Technical Specification", table_header_style),
            Paragraph("Testable Acceptance Criteria", table_header_style),
            Paragraph("Tier", table_header_style)
        ],
        [
            Paragraph("<b>FR-P0-01</b>", table_cell_style),
            Paragraph("Supervisor Orchestration", table_cell_bold),
            Paragraph("Coordinates Planner, Coder, Tester, Debugger via async thread.", table_cell_style),
            Paragraph("Executes end-to-end pipeline without blocking UI; dispatches status events.", table_cell_style),
            Paragraph("P0", table_cell_bold)
        ],
        [
            Paragraph("<b>FR-P0-02</b>", table_cell_style),
            Paragraph("Local Ollama Integration", table_cell_bold),
            Paragraph("REST HTTP client to local server (11434) with streaming support.", table_cell_style),
            Paragraph("Handles timeouts gracefully; supports token streaming with &lt;50ms latency.", table_cell_style),
            Paragraph("P0", table_cell_bold)
        ],
        [
            Paragraph("<b>FR-P0-03</b>", table_cell_style),
            Paragraph("AST Syntax Extraction", table_cell_bold),
            Paragraph("Parses workspace Python files into classes, functions, and imports.", table_cell_style),
            Paragraph("Extracts full symbol tree in &lt;100ms; feeds structural outline to Supervisor.", table_cell_style),
            Paragraph("P0", table_cell_bold)
        ],
        [
            Paragraph("<b>FR-P0-04</b>", table_cell_style),
            Paragraph("Sandboxed Code Runner", table_cell_bold),
            Paragraph("Executes code locally: Python (unittest), C (gcc), JS (node).", table_cell_style),
            Paragraph("Captures stdout, stderr, and exit codes; isolates workspace directory.", table_cell_style),
            Paragraph("P0", table_cell_bold)
        ],
        [
            Paragraph("<b>FR-P0-05</b>", table_cell_style),
            Paragraph("Closed-Loop Auto Healing", table_cell_bold),
            Paragraph("Captures test failures and triggers Debugger for automated fixes.", table_cell_style),
            Paragraph("Iteratively debugs code up to 3 times until test suite passes.", table_cell_style),
            Paragraph("P0", table_cell_bold)
        ],
        [
            Paragraph("<b>FR-P0-06</b>", table_cell_style),
            Paragraph("PySide6 Desktop GUI", table_cell_bold),
            Paragraph("Hardware-accelerated dark navy desktop UI with QSplitter & file tree.", table_cell_style),
            Paragraph("Displays live code inspector, execution terminal, and agent state cards.", table_cell_style),
            Paragraph("P0", table_cell_bold)
        ],
        [
            Paragraph("<b>FR-P1-01</b>", table_cell_style),
            Paragraph("Dynamic Model Selector", table_cell_bold),
            Paragraph("Allows assigning distinct Ollama models per agent from UI dropdowns.", table_cell_style),
            Paragraph("Queries installed models dynamically; updates config settings at runtime.", table_cell_style),
            Paragraph("P1", table_cell_bold)
        ],
        [
            Paragraph("<b>FR-P1-02</b>", table_cell_style),
            Paragraph("Vector Semantic Retrieval", table_cell_bold),
            Paragraph("Indexes code chunks via local embeddings for similarity search.", table_cell_style),
            Paragraph("Retrieves top-k relevant snippets in &lt;250ms for prompt augmentation.", table_cell_style),
            Paragraph("P1", table_cell_bold)
        ],
        [
            Paragraph("<b>FR-P2-01</b>", table_cell_style),
            Paragraph("Git Worktree Isolation", table_cell_bold),
            Paragraph("Isolates agent code synthesis in dedicated temporary Git worktrees.", table_cell_style),
            Paragraph("Auto-commits on verified tests; instant rollback on failed attempts.", table_cell_style),
            Paragraph("P2", table_cell_bold)
        ]
    ]

    t_fr = Table(fr_table_data, colWidths=[50, 95, 140, 189, 30])
    t_fr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_fr)
    story.append(Spacer(1, 10))

    # 8. Success Metrics & KPIs
    story.append(Paragraph("8. Success Metrics & Quantitative Benchmarks", h1_style))
    
    kpi_data = [
        [
            Paragraph("Metric Category", table_header_style),
            Paragraph("Metric Name", table_header_style),
            Paragraph("Baseline (Single Model)", table_header_style),
            Paragraph("Target (DevForge AI Heterogeneous)", table_header_style)
        ],
        [
            Paragraph("Synthesis Quality", table_cell_bold),
            Paragraph("First-Pass Test Success Rate", table_cell_style),
            Paragraph("42.0% (Single 1.5B/7B Model)", table_cell_style),
            Paragraph("<b>≥ 78.0%</b> (Heterogeneous Routing)", table_cell_style)
        ],
        [
            Paragraph("Self-Correction", table_cell_bold),
            Paragraph("Automated Bug Healing Rate", table_cell_style),
            Paragraph("35.0% within 3 iterations", table_cell_style),
            Paragraph("<b>≥ 82.0%</b> (Devstral/DeepSeek Debugger)", table_cell_style)
        ],
        [
            Paragraph("Operating Cost", table_cell_bold),
            Paragraph("Cloud API Cost per 1k Tasks", table_cell_style),
            Paragraph("$1,500 – $3,500 (Cloud GPT-4o)", table_cell_style),
            Paragraph("<b>$0.00</b> (100% Local GPU Compute)", table_cell_style)
        ],
        [
            Paragraph("Context Efficiency", table_cell_bold),
            Paragraph("Context Window Compression", table_cell_style),
            Paragraph("0% (Raw File Dump)", table_cell_style),
            Paragraph("<b>65% – 85%</b> Token Reduction via AST RAG", table_cell_style)
        ]
    ]

    t_kpi = Table(kpi_data, colWidths=[90, 130, 140, 144])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 10))

    # 9. Non-Functional Requirements & Security
    story.append(Paragraph("9. Non-Functional Requirements (NFRs) & Compliance", h1_style))
    story.append(Paragraph(
        "• <b>NFR-SEC-01 (Zero Telemetry & 100% Air-Gapped):</b> All prompt tokenization, inference, and file processing remain strictly bound to <code>127.0.0.1</code>. Zero outbound requests.<br/>"
        "• <b>NFR-PERF-01 (60 FPS Desktop UI):</b> Background threading prevents UI lockups during inference. Streaming token events render in real time.<br/>"
        "• <b>NFR-SAFE-01 (Sandbox Isolation):</b> Execution commands are constrained within <code>workspace_dir</code> with a mandatory 15-second subprocess execution timeout.",
        body_style
    ))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF at: {filename}")

if __name__ == "__main__":
    out_pdf = r"E:\Capstone_MITCORER\docs\prd\DevForge_AI_PRD.pdf"
    build_pdf(out_pdf)
