from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib import colors
from .common import USABLE_W, make_callout, make_table

def build_part1_pages(styles):
    pages = []
    
    # PAGE 1: COVER PAGE
    p1 = []
    cover_table_data = [
        [
            Paragraph("DEVFORGE AI", styles['CoverTitle']),
        ],
        [
            Paragraph("Autonomous, Enterprise-Grade Multi-Agent Software Development Platform<br/>"
                      "with Dynamic Heterogeneous Model Routing & Production Hybrid Code RAG", styles['CoverSubtitle'])
        ],
        [
            Spacer(1, 15)
        ],
        [
            Paragraph(
                "<b>Document Classification:</b> Official Product Requirements Document (PRD) & Blueprint<br/>"
                "<b>Authoring Engineering Team:</b> Tejas Tikkas, Rohan Umbarkar, Hrutik Sawant, Vivek Ingole<br/>"
                "<b>Institutional Affiliation:</b> Capstone Project — MITCORER (Department of Computer Science)<br/>"
                "<b>Target Release Cycle:</b> Production Release v2.2.0 (Air-Gapped Workstation Edition)<br/>"
                "<b>Primary Runtime Dependencies:</b> Local Ollama Engine, PySide6 / Qt Native UI, AST Parser, PostGIS / Vector Index<br/>"
                "<b>Evaluation Benchmark:</b> Multi-Model Specialization vs. Monolithic LLM Baseline",
                styles['CoverMeta']
            )
        ]
    ]
    t_cover = Table(cover_table_data, colWidths=[USABLE_W])
    t_cover.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0F172A")),
        ('LEFTPADDING', (0,0), (-1,-1), 22),
        ('RIGHTPADDING', (0,0), (-1,-1), 22),
        ('TOPPADDING', (0,0), (-1,-1), 32),
        ('BOTTOMPADDING', (0,0), (-1,-1), 32),
        ('BOX', (0,0), (-1,-1), 2, colors.HexColor("#1E3A8A")),
    ]))
    p1.append(t_cover)
    p1.append(Spacer(1, 25))
    
    p1.append(Paragraph("Document Scope & Executive Statement", styles['SecH2']))
    p1.append(Paragraph(
        "This authoritative Product Requirements Document (PRD) establishes the complete technical specification, "
        "architectural contracts, algorithmic formulas, and operational workflows for <b>DevForge AI</b>. "
        "DevForge AI transforms modern software engineering by moving away from cost-prohibitive, privacy-invasive cloud AI services "
        "(such as Devin, Cursor, and GitHub Copilot) to an air-gapped, on-premise multi-agent platform powered entirely by local open-weight LLMs. "
        "Crucially, this document formalizes the resolution of the core engineering bottleneck ('the catch'): the architectural shift "
        "from a single-model baseline to a heterogeneous multi-model orchestrator integrating production AST and vector code retrieval.",
        styles['Body']
    ))
    p1.append(Spacer(1, 15))
    
    # Quick metadata summary table
    summary_data = [
        [Paragraph("Target Architecture", styles['TableCellBold']), Paragraph("Hierarchical Supervisor with Sub-Agent Pipeline", styles['TableCell'])],
        [Paragraph("Supported Languages", styles['TableCellBold']), Paragraph("Python (unittest), C/C++ (MinGW GCC), JavaScript (Node.js)", styles['TableCell'])],
        [Paragraph("Inference Engine", styles['TableCellBold']), Paragraph("Local Ollama Daemon (HTTP REST + SSE Streaming on 127.0.0.1)", styles['TableCell'])],
        [Paragraph("Context Layer", styles['TableCellBold']), Paragraph("Hybrid Abstract Syntax Tree (AST) + Local Semantic Embeddings", styles['TableCell'])],
        [Paragraph("Hardware Profile", styles['TableCellBold']), Paragraph("4GB VRAM (GTX 1650) to 24GB+ Multi-GPU Workstations", styles['TableCell'])]
    ]
    p1.append(make_table(["System Dimension", "Engineering Specification"], summary_data, [150, 354], styles, "#1E3A8A"))
    pages.append(p1)

    # PAGE 2: TABLE OF CONTENTS & RUBRIC
    p2 = []
    p2.append(Paragraph("Complete Table of Contents", styles['SecH1']))
    p2.append(Paragraph("DevForge AI Technical & Functional Specification Hierarchy", styles['Body']))
    p2.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=8))
    
    toc_data = [
        [Paragraph("<b>Section 1: Executive Summary & System Identity</b>", styles['TableCell']), Paragraph("Core mission, private local AI paradigm, high-level value proposition.", styles['TableCellMuted']), Paragraph("Page 3", styles['TableCellBold'])],
        [Paragraph("<b>Section 2: Problem Statement & Quantified Evidence</b>", styles['TableCell']), Paragraph("Cloud costs, enterprise IP compliance, and the 'catch' in single-model setups.", styles['TableCellMuted']), Paragraph("Page 4", styles['TableCellBold'])],
        [Paragraph("<b>Section 3: Comprehensive As-Is vs. To-Be Workflow</b>", styles['TableCell']), Paragraph("Contrasting legacy cloud/manual workflows with DevForge AI automated loop.", styles['TableCellMuted']), Paragraph("Page 5", styles['TableCellBold'])],
        [Paragraph("<b>Section 4: Market Analysis & Competitor Differentiation</b>", styles['TableCell']), Paragraph("Detailed competitive matrix against Copilot, Cursor, Devin, and OpenHands.", styles['TableCellMuted']), Paragraph("Page 6", styles['TableCellBold'])],
        [Paragraph("<b>Section 5: User Personas & Target Stakeholders</b>", styles['TableCell']), Paragraph("Enterprise Architect, Embedded Engineer, and AI Researcher personas.", styles['TableCellMuted']), Paragraph("Page 7", styles['TableCellBold'])],
        [Paragraph("<b>Section 6: Complete End-to-End System Architecture</b>", styles['TableCell']), Paragraph("Decoupled 5-tier architecture: UI, Supervisor, Agents, RAG, and Sandbox.", styles['TableCellMuted']), Paragraph("Page 8", styles['TableCellBold'])],
        [Paragraph("<b>Section 7: Supervisor / Orchestrator Core Mechanism</b>", styles['TableCell']), Paragraph("State machine, event bus dispatcher, async background threading, pipeline flow.", styles['TableCellMuted']), Paragraph("Page 9", styles['TableCellBold'])],
        [Paragraph("<b>Section 8: Dynamic Heterogeneous Model Routing</b>", styles['TableCell']), Paragraph("Resolving the catch: per-agent model assignment and capability matrix.", styles['TableCellMuted']), Paragraph("Page 10", styles['TableCellBold'])],
        [Paragraph("<b>Section 9: Production Code RAG Layer (AST + Vector)</b>", styles['TableCell']), Paragraph("Python AST extraction, symbol tables, chunking, and local vector embeddings.", styles['TableCellMuted']), Paragraph("Page 11", styles['TableCellBold'])],
        [Paragraph("<b>Section 10: Closed-Loop Automated Execution & Healing</b>", styles['TableCell']), Paragraph("Local sandboxes (Python unittest, GCC, Node), exit-code handling, auto-debugging.", styles['TableCellMuted']), Paragraph("Page 12", styles['TableCellBold'])],
        [Paragraph("<b>Section 11: Complete Application Screen Architecture</b>", styles['TableCell']), Paragraph("PySide6 6-panel desktop layout, file tree, code viewer, and terminals.", styles['TableCellMuted']), Paragraph("Page 13", styles['TableCellBold'])],
        [Paragraph("<b>Section 12: Screens 1 to 3 Detailed Specifications</b>", styles['TableCell']), Paragraph("Project Hub, Natural Language Prompt Input, and Interactive File Explorer.", styles['TableCellMuted']), Paragraph("Page 14", styles['TableCellBold'])],
        [Paragraph("<b>Section 13: Screens 4 to 6 Detailed Specifications</b>", styles['TableCell']), Paragraph("Code Inspector, Multi-Language Sandbox Terminal, and Agent Pipeline Cards.", styles['TableCellMuted']), Paragraph("Page 15", styles['TableCellBold'])],
        [Paragraph("<b>Section 14: Functional Requirements Triage (P0 Core)</b>", styles['TableCell']), Paragraph("Mandatory MVP capabilities (FR-P0-01 to FR-P0-06) and acceptance criteria.", styles['TableCellMuted']), Paragraph("Page 16", styles['TableCellBold'])],
        [Paragraph("<b>Section 15: Functional Requirements (P1 & P2 Roadmap)</b>", styles['TableCell']), Paragraph("Dynamic model UI, vector search, diff inspector, and multi-GPU clustering.", styles['TableCellMuted']), Paragraph("Page 17", styles['TableCellBold'])],
        [Paragraph("<b>Section 16: Non-Functional Requirements (NFRs)</b>", styles['TableCell']), Paragraph("Performance, VRAM safety, zero-telemetry air-gapped security, and reliability.", styles['TableCellMuted']), Paragraph("Page 18", styles['TableCellBold'])],
        [Paragraph("<b>Section 17: Data Contracts & IPC Message Schemas</b>", styles['TableCell']), Paragraph("Pydantic models, JSON request/response contracts, and EventBus topics.", styles['TableCellMuted']), Paragraph("Page 19", styles['TableCellBold'])],
        [Paragraph("<b>Section 18: End-to-End User Journey Walkthrough</b>", styles['TableCell']), Paragraph("Chronological execution walkthrough: Pune Capstone palindrome/reverse string task.", styles['TableCellMuted']), Paragraph("Page 20", styles['TableCellBold'])],
        [Paragraph("<b>Section 19: Seven-Phase Implementation Roadmap</b>", styles['TableCell']), Paragraph("13-month timeline from model benchmarking to commercial pilot deployments.", styles['TableCellMuted']), Paragraph("Page 21", styles['TableCellBold'])],
        [Paragraph("<b>Section 20: Comprehensive Verification & Test Suite</b>", styles['TableCell']), Paragraph("Edge-case matrix, syntax verification, compiler timeouts, and regression tests.", styles['TableCellMuted']), Paragraph("Page 22", styles['TableCellBold'])],
        [Paragraph("<b>Section 21: Quantitative Benchmarks & KPIs</b>", styles['TableCell']), Paragraph("Pass@k rates, auto-healing success, token compression, and cost metrics.", styles['TableCellMuted']), Paragraph("Page 23", styles['TableCellBold'])],
        [Paragraph("<b>Section 22: Hardware Profile & Resource Sizing</b>", styles['TableCell']), Paragraph("VRAM tiers (4GB, 8GB, 16GB, 24GB+), GGUF quantization, and swap logic.", styles['TableCellMuted']), Paragraph("Page 24", styles['TableCellBold'])],
        [Paragraph("<b>Section 23: Risks, Assumptions & Mitigation Strategies</b>", styles['TableCell']), Paragraph("Model hallucination, infinite debugging loops, and local storage exhaustion.", styles['TableCellMuted']), Paragraph("Page 25", styles['TableCellBold'])],
        [Paragraph("<b>Section 24: Enterprise Monetization & Budget Model</b>", styles['TableCell']), Paragraph("On-prem licensing ($150/dev/mo), appliance ($499/mo), and $250k seed budget.", styles['TableCellMuted']), Paragraph("Page 26", styles['TableCellBold'])],
        [Paragraph("<b>Section 25: Comprehensive Engineering Glossary</b>", styles['TableCell']), Paragraph("Clear definitions of AST, RAG, Ollama, FIM, PySide6, IPC, and Quantization.", styles['TableCellMuted']), Paragraph("Page 27", styles['TableCellBold'])],
        [Paragraph("<b>Section 26: Academic Citations & References</b>", styles['TableCell']), Paragraph("Formal literature citations: MetaGPT, SWE-bench, Qwen2.5, DeepSeek, Codestral.", styles['TableCellMuted']), Paragraph("Page 28", styles['TableCellBold'])],
        [Paragraph("<b>Section 27: Final Executive Project Synthesis</b>", styles['TableCell']), Paragraph("Summary of core contributions and immediate development actions.", styles['TableCellMuted']), Paragraph("Page 29", styles['TableCellBold'])]
    ]
    p2.append(make_table(["Document Section", "Detailed Technical Scope", "Loc."], toc_data, [160, 294, 50], styles, "#0F172A"))
    pages.append(p2)

    # PAGE 3: SECTION 1 - EXECUTIVE SUMMARY & SYSTEM IDENTITY
    p3 = []
    p3.append(Paragraph("Section 1: Executive Summary & System Identity", styles['SecH1']))
    p3.append(Paragraph("1.1 Product Vision & High-Level Purpose", styles['SecH2']))
    p3.append(Paragraph(
        "Software engineering is undergoing a generational inflection point driven by Large Language Models (LLMs). "
        "However, current industry leaders—such as GitHub Copilot, Cursor AI, Devin by Cognition, and OpenHands—are built almost "
        "exclusively as cloud-dependent SaaS solutions. They mandate shipping proprietary source code, internal schemas, and intellectual property "
        "to third-party remote API endpoints (e.g., OpenAI, Anthropic, or proprietary cloud servers).",
        styles['Body']
    ))
    p3.append(Paragraph(
        "For enterprises operating in high-security, highly-regulated verticals (banking, fintech, defense aerospace, healthcare, and critical infrastructure), "
        "this architectural paradigm is an absolute non-starter. Stringent regulatory mandates (SOC2 Type II, GDPR, HIPAA, ITAR, and enterprise NDA agreements) "
        "strictly forbid code leakage beyond enterprise corporate perimeters. Furthermore, token-based cloud pricing escalates uncontrollably "
        "when autonomous multi-agent systems iteratively index full repositories and execute multiple rounds of self-debugging.",
        styles['Body']
    ))
    p3.append(Paragraph(
        "<b>DevForge AI</b> is engineered to eliminate this compromise. It is an **autonomous, 100% private, on-premise software engineering platform** "
        "modeled after modern AI IDEs (such as Antigravity and Codex), designed to execute locally on consumer laptop and workstation hardware "
        "via <b>Ollama</b> without relying on external cloud APIs.",
        styles['Body']
    ))
    
    p3.append(Paragraph("1.2 Core Architectural Innovations", styles['SecH2']))
    innovations = [
        "<b>1. Hierarchical Supervisor/Orchestrator:</b> A centralized orchestrator coordinates specialized agents (Planner, Coder, Tester, Debugger) across a structured state machine with non-blocking async execution.",
        "<b>2. Dynamic Heterogeneous Model Routing:</b> Rather than forcing one model to do everything, the orchestrator routes specific tasks to specialized open-weight models (Qwen2.5-Coder for system planning, Codestral for synthesis, CodeGemma for unit tests, Devstral for bug healing).",
        "<b>3. Production Hybrid Code RAG:</b> Combines deterministic Abstract Syntax Tree (AST) structural parsing with local dense vector embeddings, feeding compact, relevant context windows and saving 65%–85% of token overhead.",
        "<b>4. Closed-Loop Execution Sandbox:</b> Integrates local compilers and test runners (Python unittest, MinGW GCC C/C++, Node.js). If tests fail, the runtime automatically feeds execution traces into a self-healing debugging loop.",
        "<b>5. Hardware-Accelerated Local UI:</b> Native PySide6 / Qt desktop interface with draggable splitters, live OS file tree tracking, multi-tab monospace code inspectors, and real-time execution terminals."
    ]
    for inn in innovations:
        p3.append(Paragraph(inn, styles['Bullet']))
    p3.append(Spacer(1, 6))

    callout_p3 = (
        "<b>Key Fiduciary Takeaway:</b> DevForge AI replaces unpredictable cloud SaaS operational expenditures (OpEx) "
        "with zero-marginal-cost local GPU compute, while guaranteeing 100% intellectual property containment inside the enterprise firewall."
    )
    p3.append(make_callout(callout_p3, styles, "#F0FDF4", "#86EFAC"))
    pages.append(p3)

    return pages
