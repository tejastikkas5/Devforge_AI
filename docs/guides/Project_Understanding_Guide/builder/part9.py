from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib import colors
from .common import USABLE_W, make_callout, make_table

def build_pug_part9_pages(styles):
    pages = []
    
    # PAGE 25: SECTION 23 - COMPLETE ENGINEERING GLOSSARY FOR BEGINNERS
    p25 = []
    p25.append(Paragraph("Section 23: Complete Engineering Glossary for Beginners", styles['SecH1']))
    p25.append(Paragraph("23.1 Plain English Definitions of Core Technical Terms", styles['SecH2']))
    p25.append(Paragraph(
        "To help every teammate, evaluator, and non-technical stakeholder master project concepts, here are clear definitions:",
        styles['Body']
    ))

    glossary_items = [
        [Paragraph("Term", styles['TableHead']), Paragraph("Plain-English Definition & System Context", styles['TableHead'])],
        [Paragraph("<b>PRD</b>", styles['TableCellBold']), Paragraph("<b>Product Requirements Document:</b> The formal architectural blueprint detailing what a software system must do before writing code.", styles['TableCell'])],
        [Paragraph("<b>Supervisor</b>", styles['TableCellBold']), Paragraph("<b>Central Orchestrator:</b> The lead AI agent that breaks down tasks, schedules worker agents, and coordinates pipeline execution.", styles['TableCell'])],
        [Paragraph("<b>AST</b>", styles['TableCellBold']), Paragraph("<b>Abstract Syntax Tree:</b> A tree representation of code syntax. DevForge AI uses AST to extract function/class summaries without token bloat.", styles['TableCell'])],
        [Paragraph("<b>RAG</b>", styles['TableCellBold']), Paragraph("<b>Retrieval-Augmented Generation:</b> Feeding relevant codebase context (AST outlines + vector snippets) into the AI prompt before generating code.", styles['TableCell'])],
        [Paragraph("<b>Heterogeneous Routing</b>", styles['TableCellBold']), Paragraph("Assigning different specialized models (e.g. DeepSeek for planning, Codestral for coding) instead of using one generic model.", styles['TableCell'])],
        [Paragraph("<b>Ollama</b>", styles['TableCellBold']), Paragraph("A high-performance local AI runtime that executes open-source LLMs directly on your computer's GPU/CPU without internet.", styles['TableCell'])],
        [Paragraph("<b>PySide6</b>", styles['TableCellBold']), Paragraph("Official Python bindings for Qt 6, used to build our high-speed, native dark-themed desktop application.", styles['TableCell'])],
        [Paragraph("<b>EventBus</b>", styles['TableCellBold']), Paragraph("An internal messaging highway that allows backend agents to stream logs and status updates to the UI without freezing the screen.", styles['TableCell'])],
        [Paragraph("<b>GGUF</b>", styles['TableCellBold']), Paragraph("A compact file format used to store quantized (compressed) AI model weights for fast local inference.", styles['TableCell'])],
        [Paragraph("<b>Self-Healing Loop</b>", styles['TableCellBold']), Paragraph("An automated process where failed test compiler errors are fed to the Debugger agent to auto-fix code until tests pass.", styles['TableCell'])]
    ]
    p25.append(make_table(["Term", "Plain-English Definition & System Context"], glossary_items[1:], [110, 394], styles, "#1E3A8A"))
    pages.append(p25)

    # PAGE 26: SECTION 24 - FINAL PROJECT SUMMARY & IMMEDIATE ACTION ITEMS
    p26 = []
    p26.append(Paragraph("Section 24: Final Project Summary & Immediate Action Items", styles['SecH1']))
    p26.append(Paragraph("24.1 Two-Minute Executive Summary", styles['SecH2']))
    p26.append(Paragraph(
        "<b>• The Problem:</b> Cloud AI coding platforms leak confidential enterprise source code and generate huge recurring bills ($20k–$100k/yr). "
        "Meanwhile, simple local AI prototypes fail because they try to force a single small model to perform every phase of development without codebase context.",
        styles['Body']
    ))
    p26.append(Paragraph(
        "<b>• The Solution:</b> <b>DevForge AI</b>—an autonomous, 100% private, air-gapped software development desktop platform running on local Ollama LLMs. "
        "It features a centralized <b>Supervisor Orchestrator</b>, <b>Dynamic Heterogeneous Model Routing</b>, and <b>Production AST Code RAG</b>, "
        "verifying all code inside isolated local sandboxes (Python unittest, MinGW GCC, Node.js) with closed-loop self-healing.",
        styles['Body']
    ))
    p26.append(Spacer(1, 4))

    p26.append(Paragraph("24.2 Immediate Next Engineering Actions (Pre-Demo Checklist)", styles['SecH2']))
    next_actions = [
        "<b>1. Connect AST Parser to Supervisor:</b> Replace the basic directory walk in <code>src/agents/supervisor.py</code> with <code>CodeASTAnalyzer.analyze_source()</code> to inject structural symbol outlines into prompt contexts.",
        "<b>2. Bind Model Selectors in PySide6 UI:</b> Add model dropdowns to Panel 2 in <code>src/pyside_app.py</code> and bind them dynamically to <code>config/settings.py</code>.",
        "<b>3. Run 50-Task Verification Matrix:</b> Execute automated test suites across Python, C, and JS to record comparative Pass@1 and bug healing benchmarks.",
        "<b>4. Rehearse 5-Minute Pitch:</b> Follow the scripted demonstration checklist in Section 21 for technical evaluation panels."
    ]
    for na in next_actions:
        p26.append(Paragraph(na, styles['Bullet']))
        p26.append(Spacer(1, 2))
    p26.append(Spacer(1, 8))

    final_box_p26 = (
        "<b>Final Engineering Endorsement:</b><br/>"
        "DevForge AI represents a major leap forward in sovereign, enterprise-grade AI software development. "
        "With full documentation, mathematical rigor, and architectural clarity established in this guide, "
        "the platform is fully positioned for successful presentation and production delivery."
    )
    p26.append(make_callout(final_box_p26, styles, "#F0FDF4", "#16A34A"))
    pages.append(p26)

    return pages
