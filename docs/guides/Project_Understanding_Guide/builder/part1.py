from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib import colors
from .common import USABLE_W, make_callout, make_table

def build_pug_part1_pages(styles):
    pages = []
    
    # PAGE 1: COVER PAGE
    p1 = []
    cover_data = [
        [
            Paragraph("DEVFORGE AI: Complete Project Understanding Guide & MVP Blueprint", styles['CoverTitle'])
        ],
        [
            Paragraph("Comprehensive Technical Reference, Algorithmic Deconstructions, Screen-by-Screen Engineering Specs, "
                      "and Verification Protocols for Pair Programmers, Developers & Evaluators", styles['CoverSubtitle'])
        ],
        [
            Spacer(1, 10)
        ],
        [
            Paragraph(
                "<b>Project Name:</b> DevForge AI (Air-Gapped Multi-Agent SE Platform)<br/>"
                "<b>Domain:</b> Autonomous Agentic Engineering, Heterogeneous LLM Routing & AST Code RAG<br/>"
                "<b>Document Classification:</b> Complete Pre-Coding Project Understanding & Blueprint (Guide v2.2.0)<br/>"
                "<b>Engineering Core Authors:</b> Tejas Tikkas, Rohan Umbarkar, Hrutik Sawant, Vivek Ingole<br/>"
                "<b>Institutional Affiliation:</b> Capstone Project — MITCORER (Department of Computer Science)<br/>"
                "<b>Primary Runtime Stack:</b> Local Ollama Daemon, PySide6 / Qt Native UI, Python AST, MinGW GCC, Node.js<br/>"
                "<b>Date:</b> October 2026 | Companion to <code>DevForge_AI_PRD.pdf</code>",
                styles['CoverMeta']
            )
        ]
    ]
    t_cover = Table(cover_data, colWidths=[USABLE_W])
    t_cover.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0F172A")),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
        ('TOPPADDING', (0,0), (-1,-1), 26),
        ('BOTTOMPADDING', (0,0), (-1,-1), 26),
        ('BOX', (0,0), (-1,-1), 2, colors.HexColor("#1E3A8A")),
    ]))
    p1.append(t_cover)
    p1.append(Spacer(1, 18))
    
    p1.append(Paragraph("Executive Summary & Guide Purpose", styles['SecH2']))
    p1.append(Paragraph(
        "This authoritative guide serves as the shared technical manual for the entire development team, capstone mentors, and "
        "competition evaluators before reviewing or executing the codebase. It translates the formal Product Requirements Document (PRD) "
        "and underlying multi-agent artificial intelligence research into simple, clear, unambiguous engineering prose. "
        "Whether you are configuring the PySide6 hardware-accelerated desktop canvas, implementing the Supervisor finite-state machine, "
        "connecting the Abstract Syntax Tree (AST) parser to prompt contexts, managing local quantized Ollama model lifecycles, or presenting "
        "progress to technical judges, this document explains what we are building, why it matters, how the architectural components collaborate, "
        "and what each module must deliver.",
        styles['Body']
    ))
    p1.append(Spacer(1, 10))

    summary_table = [
        [Paragraph("Core Architecture", styles['TableCellBold']), Paragraph("Hierarchical Orchestrator (Supervisor) with EventBus Decoupling", styles['TableCell'])],
        [Paragraph("Model Strategy", styles['TableCellBold']), Paragraph("Heterogeneous Local Routing (Qwen, DeepSeek, Codestral, Devstral, CodeGemma)", styles['TableCell'])],
        [Paragraph("Codebase Context", styles['TableCellBold']), Paragraph("Two-Tier Hybrid RAG: Python AST Symbol Outlines + Vector Similarity Search", styles['TableCell'])],
        [Paragraph("Verification Sandboxes", styles['TableCellBold']), Paragraph("Local isolated runners for Python unittest, MinGW GCC (C/C++), and Node.js", styles['TableCell'])],
        [Paragraph("Hardware Envelope", styles['TableCellBold']), Paragraph("Quantized 4-bit/8-bit GGUF models tailored to 4GB VRAM laptops up to multi-GPU nodes", styles['TableCell'])]
    ]
    p1.append(make_table(["Architectural Dimension", "Engineering Implementation Target"], summary_table, [150, 354], styles, "#1E3A8A"))
    pages.append(p1)

    # PAGE 2: TABLE OF CONTENTS (24 SECTIONS)
    p2 = []
    p2.append(Paragraph("Table of Contents", styles['SecH1']))
    p2.append(Paragraph("Comprehensive 24-Section Technical Hierarchy & Navigation Index", styles['Body']))
    p2.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=6))
    
    toc_data = [
        [Paragraph("<b>Section 1: Project Overview & Executive Mission</b>", styles['TableCell']), Paragraph("Identity, core purpose, and problem we solve in simple English.", styles['TableCellMuted']), Paragraph("Page 3", styles['TableCellBold'])],
        [Paragraph("<b>Section 2: Understanding the Actual Problem & Root Causes</b>", styles['TableCell']), Paragraph("Cloud costs, privacy exfiltration, context choking, and enterprise risks.", styles['TableCellMuted']), Paragraph("Page 4", styles['TableCellBold'])],
        [Paragraph("<b>Section 3: The Project 'Catch' Explained Plainly</b>", styles['TableCell']), Paragraph("Why single-model setups fail and how heterogeneous routing solves it.", styles['TableCellMuted']), Paragraph("Page 5", styles['TableCellBold'])],
        [Paragraph("<b>Section 4: Existing Solutions vs. DevForge AI</b>", styles['TableCell']), Paragraph("Direct architectural comparison with Copilot, Cursor, Devin, OpenHands.", styles['TableCellMuted']), Paragraph("Page 6", styles['TableCellBold'])],
        [Paragraph("<b>Section 5: Our Proposed Solution & End-to-End Workflow</b>", styles['TableCell']), Paragraph("8-stage pipeline from user prompt to sandboxed verified execution.", styles['TableCellMuted']), Paragraph("Page 7", styles['TableCellBold'])],
        [Paragraph("<b>Section 6: Complete Desktop Application Screens (PySide6)</b>", styles['TableCell']), Paragraph("Draggable 6-panel layout, file tree, inspector, terminal, and cards.", styles['TableCellMuted']), Paragraph("Page 8", styles['TableCellBold'])],
        [Paragraph("<b>Section 7: Screens 1 to 3 Detailed Engineering Walkthrough</b>", styles['TableCell']), Paragraph("Project Hub, Natural Language Prompt Console, and OS File Explorer.", styles['TableCellMuted']), Paragraph("Page 9", styles['TableCellBold'])],
        [Paragraph("<b>Section 8: Screens 4 to 6 Detailed Engineering Walkthrough</b>", styles['TableCell']), Paragraph("Monospace Code Inspector, Sandboxed Terminal, and Agent State Cards.", styles['TableCellMuted']), Paragraph("Page 10", styles['TableCellBold'])],
        [Paragraph("<b>Section 9: System Architecture Explained Simply</b>", styles['TableCell']), Paragraph("Decoupled multi-tier blueprint, IPC event bus, and async worker loops.", styles['TableCellMuted']), Paragraph("Page 11", styles['TableCellBold'])],
        [Paragraph("<b>Section 10: The Supervisor / Orchestrator Core Mechanism</b>", styles['TableCell']), Paragraph("Finite state machine (FSM), intent classification, and task dispatching.", styles['TableCellMuted']), Paragraph("Page 12", styles['TableCellBold'])],
        [Paragraph("<b>Section 11: Dynamic Heterogeneous Model Routing Explained</b>", styles['TableCell']), Paragraph("Why different tasks demand different models; the routing matrix.", styles['TableCellMuted']), Paragraph("Page 13", styles['TableCellBold'])],
        [Paragraph("<b>Section 12: Production Code RAG in Simple English</b>", styles['TableCell']), Paragraph("Why standard RAG fails on code; AST syntax outlines vs vector chunks.", styles['TableCellMuted']), Paragraph("Page 14", styles['TableCellBold'])],
        [Paragraph("<b>Section 13: Concrete CodeASTAnalyzer & Vector Walkthrough</b>", styles['TableCell']), Paragraph("Code walkthrough of `src/rag/ast_parser.py` and token savings math.", styles['TableCellMuted']), Paragraph("Page 15", styles['TableCellBold'])],
        [Paragraph("<b>Section 14: Closed-Loop Automated Sandboxes & Self-Healing</b>", styles['TableCell']), Paragraph("Compilers (MinGW GCC), unittests, stderr capture, and Debugger loop.", styles['TableCellMuted']), Paragraph("Page 16", styles['TableCellBold'])],
        [Paragraph("<b>Section 15: The Self-Healing Algorithm & Recovery Limits</b>", styles['TableCell']), Paragraph("3-pass repair threshold, syntax patching, and loop prevention.", styles['TableCellMuted']), Paragraph("Page 17", styles['TableCellBold'])],
        [Paragraph("<b>Section 16: Data Models, Pydantic Schemas & IPC Contracts</b>", styles['TableCell']), Paragraph("EventBus topics, payload structures, and JSON serialization schemas.", styles['TableCellMuted']), Paragraph("Page 18", styles['TableCellBold'])],
        [Paragraph("<b>Section 17: End-to-End User Journey Walkthrough</b>", styles['TableCell']), Paragraph("Step-by-step Pune Capstone scenario: C Palindrome & String Reverse.", styles['TableCellMuted']), Paragraph("Page 19", styles['TableCellBold'])],
        [Paragraph("<b>Section 18: Concrete Execution Traces & Code Artifacts</b>", styles['TableCell']), Paragraph("Actual generated `utils.h`, `utils.c`, `test_main.c`, and GCC outputs.", styles['TableCellMuted']), Paragraph("Page 20", styles['TableCellBold'])],
        [Paragraph("<b>Section 19: MVP Engineering Development Plan (6 Phases)</b>", styles['TableCell']), Paragraph("Milestones 1 to 6, tech dependencies, deliverables, and deferrals.", styles['TableCellMuted']), Paragraph("Page 21", styles['TableCellBold'])],
        [Paragraph("<b>Section 20: Edge-Case Test Suite & Verification Matrix</b>", styles['TableCell']), Paragraph("Automated assertions for chat intent, AST crashes, GCC errors, and OOM.", styles['TableCellMuted']), Paragraph("Page 22", styles['TableCellBold'])],
        [Paragraph("<b>Section 21: Live Evaluation & Demonstration Checklist</b>", styles['TableCell']), Paragraph("Scripted 5-minute competition walkthrough for judges and panels.", styles['TableCellMuted']), Paragraph("Page 23", styles['TableCellBold'])],
        [Paragraph("<b>Section 22: Hardware Resource Sizing & Storage Guide</b>", styles['TableCell']), Paragraph("VRAM tiers (4GB/8GB/16GB/24GB), GGUF quantization, `E:/OllamaModels`.", styles['TableCellMuted']), Paragraph("Page 24", styles['TableCellBold'])],
        [Paragraph("<b>Section 23: Complete Engineering Glossary for Beginners</b>", styles['TableCell']), Paragraph("Simple definitions of AST, RAG, Ollama, FIM, PySide6, IPC, and GGUF.", styles['TableCellMuted']), Paragraph("Page 25", styles['TableCellBold'])],
        [Paragraph("<b>Section 24: Final Project Summary & Immediate Action Items</b>", styles['TableCell']), Paragraph("2-minute executive pitch and next engineering steps.", styles['TableCellMuted']), Paragraph("Page 26", styles['TableCellBold'])]
    ]
    p2.append(make_table(["Guide Section", "Detailed Technical Scope & Description", "Loc."], toc_data, [155, 304, 45], styles, "#0F172A"))
    pages.append(p2)

    # PAGE 3: SECTION 1 - PROJECT OVERVIEW
    p3 = []
    p3.append(Paragraph("Section 1: Project Overview & Executive Mission", styles['SecH1']))
    p3.append(Paragraph("1.1 What is DevForge AI?", styles['SecH2']))
    p3.append(Paragraph(
        "<b>DevForge AI</b> is a 100% private, air-gapped, on-premise software engineering platform modeled after modern AI development environments "
        "(such as Google Antigravity and OpenAI Codex). It runs on local consumer laptops and workstation hardware (tested down to a modest "
        "GTX 1650 GPU with 4GB VRAM and 16GB–24GB RAM) using local open-weight Large Language Models via <b>Ollama</b>, completely eliminating "
        "the need to transmit proprietary enterprise code to remote cloud APIs.",
        styles['Body']
    ))
    p3.append(Paragraph(
        "Instead of forcing a human developer to manually copy and paste code between an AI chat window and a code editor, DevForge AI acts as "
        "an autonomous software engineering team. A central <b>Supervisor / Orchestrator</b> ingests a natural language prompt, coordinates "
        "specialized sub-agents (Planner, Coder, Tester, Debugger), indexes project code via an Abstract Syntax Tree (AST) RAG engine, "
        "compiles and runs unit tests in a local sandbox (Python, C/C++, JavaScript), and automatically heals runtime bugs in a closed loop.",
        styles['Body']
    ))
    
    p3.append(Paragraph("1.2 Simple One-Paragraph Explanation (For Non-Technical Audiences)", styles['SecH2']))
    callout_p3 = (
        "<i>\"Imagine hiring a team of four specialized software engineers—an architect who drafts the system blueprint, a programmer who writes "
        "the code, a quality assurance tester who writes test cases, and a debugger who diagnoses crashes. Now imagine that entire team lives "
        "directly inside your laptop, runs completely offline without sending your company's secret code to the internet, and works together "
        "in under 60 seconds to build, compile, and verify your program for zero dollars in API costs. That is DevForge AI.\"</i>"
    )
    p3.append(make_callout(callout_p3, styles, "#F0FDF4", "#86EFAC"))
    p3.append(Spacer(1, 8))

    p3.append(Paragraph("1.3 Short Pitch for Competition Judges & Evaluators", styles['SecH2']))
    pitch_text = (
        "<i>\"Enterprise dev teams burn $20k to $100k annually on cloud AI tokens, while regulated industries in defense, finance, and healthcare "
        "are legally prohibited from leaking proprietary code to third-party APIs like OpenAI. Current local multi-agent tools fail because they "
        "use a single small model for every task and lack codebase context. DevForge AI solves this by introducing a 100% air-gapped desktop "
        "engine that pairs a Hierarchical Supervisor with Dynamic Heterogeneous Model Routing and Production AST Code RAG. We assign optimal open-weight "
        "models to their proven strengths—DeepSeek for planning, Codestral for coding, CodeGemma for testing, and Devstral for debugging—delivering "
        "verified, compiling software in an automated self-healing loop at zero marginal API cost.\"</i>"
    )
    p3.append(make_callout(pitch_text, styles, "#EFF6FF", "#93C5FD"))
    pages.append(p3)

    return pages
