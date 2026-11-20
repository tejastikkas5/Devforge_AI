import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.lib import colors
from .common import USABLE_W, make_callout, make_table

def build_part3_pages(styles):
    pages = []
    
    # PAGE 7: SECTION 5 - USER PERSONAS & STAKEHOLDERS
    p7 = []
    p7.append(Paragraph("Section 5: User Personas & Target Stakeholders", styles['SecH1']))
    p7.append(Paragraph("5.1 Target Operational Profiles", styles['SecH2']))
    p7.append(Paragraph(
        "To ensure DevForge AI directly addresses enterprise workflows, the platform is designed around three primary personas:",
        styles['Body']
    ))
    
    personas_data = [
        [
            Paragraph("<b>Persona 1: Enterprise Systems Architect</b><br/>"
                      "<i>Name: Arjun Sharma</i><br/>"
                      "<b>Organization:</b> Tier-1 Investment Bank / FinTech<br/>"
                      "<b>Primary Objective:</b> Build secure internal microservices and ledger reconciliation tools.<br/>"
                      "<b>Core Pain Point:</b> Bank compliance prohibits any code from leaving on-premise servers. Tools like Copilot/Cursor are completely blocked by corporate firewalls.<br/>"
                      "<b>DevForge AI Value:</b> Provides 100% private, air-gapped agentic development on internal GPU servers with zero data exfiltration risk.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Persona 2: Embedded & Systems Software Engineer</b><br/>"
                      "<i>Name: Priya Nair</i><br/>"
                      "<b>Organization:</b> Industrial Automation & Embedded Systems Consultancy<br/>"
                      "<b>Primary Objective:</b> Develop robust C/C++ drivers, Python test suites, and low-level CLI utilities.<br/>"
                      "<b>Core Pain Point:</b> Cloud AI tools produce generic Python snippets that hallucinate header files or fail to compile under GCC with strict compiler warnings (`-Wall -Werror`).<br/>"
                      "<b>DevForge AI Value:</b> Integrated MinGW GCC sandbox that immediately compiles C code, catches compiler errors, and triggers the Debugger for instant syntax auto-correction.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Persona 3: Academic & AI/ML Software Researcher</b><br/>"
                      "<i>Name: Rohan Deshmukh</i><br/>"
                      "<b>Organization:</b> Department of Computer Science & Autonomous Agent Lab<br/>"
                      "<b>Primary Objective:</b> Benchmark multi-agent collaboration patterns and evaluate single-model vs heterogeneous model performance.<br/>"
                      "<b>Core Pain Point:</b> Existing agent frameworks (MetaGPT, ChatDev) are tightly coupled to cloud OpenAI keys or lack real-time local GUI visualization.<br/>"
                      "<b>DevForge AI Value:</b> Native PySide6 interface with hot-swappable local Ollama models, live EventBus telemetry, and reproducible benchmarking suites.", styles['TableCell'])
        ]
    ]
    t_pers = Table(personas_data, colWidths=[USABLE_W])
    t_pers.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    p7.append(t_pers)
    pages.append(p7)

    # PAGE 8: SECTION 6 - COMPLETE END-TO-END SYSTEM ARCHITECTURE
    p8 = []
    p8.append(Paragraph("Section 6: Complete End-to-End System Architecture", styles['SecH1']))
    p8.append(Paragraph("6.1 Architectural System Diagram & Multi-Tier Topology", styles['SecH2']))
    p8.append(Paragraph(
        "DevForge AI is structured into five decoupled layers: (1) Native Desktop Presentation Tier, (2) Supervisor Orchestrator Core, "
        "(3) Specialized Multi-Agent Workforce, (4) Production Code RAG Layer, and (5) Local Execution Sandbox.",
        styles['Body']
    ))
    
    flow_img_path = r"E:\Capstone_MITCORER\docs\prd\Flow.png"
    if os.path.exists(flow_img_path):
        img_flow = RLImage(flow_img_path, width=210, height=302)
        desc_box = [
            Paragraph("<b>Figure 6.1: Supervisor & Agent Pipeline Flow</b>", styles['SecH3']),
            Paragraph("• <b>User Prompt:</b> Ingests natural language developer goals via the PySide6 UI.<br/>"
                      "• <b>Supervisor / Orchestrator:</b> Central controller running in background thread; handles intent classification and step dispatch.<br/>"
                      "• <b>Specialized Workforce:</b> Planner (architecture), Researcher (syntax analysis), Coder (implementation), Tester (unit testing), Debugger (auto-repair).<br/>"
                      "• <b>Production RAG Layer:</b> AST class/method extraction + dense vector embeddings.<br/>"
                      "• <b>Dynamic Model Selection:</b> Routes tasks to optimal local Ollama LLMs.<br/>"
                      "• <b>Final Verified Software:</b> Executed in sandboxes and committed to disk.", styles['Body'])
        ]
        t_arch = Table([[img_flow, desc_box]], colWidths=[220, 284])
        t_arch.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (1,0), (1,0), 8),
            ('PADDING', (0,0), (0,0), 0),
        ]))
        p8.append(t_arch)
    pages.append(p8)

    # PAGE 9: SECTION 7 - SUPERVISOR / ORCHESTRATOR CORE MECHANISM
    p9 = []
    p9.append(Paragraph("Section 7: Supervisor / Orchestrator Core Mechanism", styles['SecH1']))
    p9.append(Paragraph("7.1 Centralized Pipeline Coordination & State Machine", styles['SecH2']))
    p9.append(Paragraph(
        "The <code>Supervisor</code> class (located in <code>src/agents/supervisor.py</code>) represents the central operational nervous system "
        "of DevForge AI. Rather than allowing agents to execute arbitrarily or flood each other with uncontrolled prompts, the Supervisor "
        "enforces a strict, predictable finite-state machine (FSM):",
        styles['Body']
    ))
    
    states = [
        "<b>1. IDLE / READY:</b> Awaiting user prompt; listening for UI events on the thread-safe <code>EventBus</code>.",
        "<b>2. INTENT CLASSIFICATION:</b> Inspects user prompt (<code>_is_coding_task</code>) to distinguish casual conversational greetings from technical engineering tasks.",
        "<b>3. CONTEXT ENRICHMENT (RAG):</b> Executes AST symbol parsing and workspace file inspection to generate structural context.",
        "<b>4. PLANNING PHASE:</b> Activates the Planner agent to generate a step-by-step technical implementation specification.",
        "<b>5. CODING PHASE:</b> Dispatches implementation instructions to the Coder agent; extracts generated files and writes them to the workspace.",
        "<b>6. TESTING PHASE:</b> Triggers the Tester agent to synthesize comprehensive unit test cases (Python unittest, C test harness, or JS assertions).",
        "<b>7. SANDBOX EXECUTION:</b> Invokes <code>CodeRunner</code> to compile and execute the test suite in an isolated subprocess.",
        "<b>8. CONDITIONAL DEBUGGING:</b> If execution fails (exit code != 0), the Supervisor intercepts stderr and passes it to the Debugger in a self-healing loop (up to 3 attempts).",
        "<b>9. PIPELINE COMPLETION:</b> Posts final pipeline telemetry and updates UI status cards to successful completion."
    ]
    for st in states:
        p9.append(Paragraph(st, styles['Bullet']))
    p9.append(Spacer(1, 6))

    p9.append(Paragraph("7.2 Non-Blocking Asynchronous Threading", styles['SecH2']))
    p9.append(Paragraph(
        "A critical engineering requirement (NFR-PERF-01) is that the desktop GUI must never freeze or drop frames during heavy local LLM inference. "
        "The Supervisor executes all inference, compilation, and file I/O operations inside a dedicated background worker thread "
        "(<code>start_pipeline_async</code>). The Supervisor communicates with the PySide6 UI exclusively via an asynchronous, thread-safe "
        "publish-subscribe <code>EventBus</code> (<code>src/core/event_bus.py</code>), posting events such as <code>agent_activated</code>, "
        "<code>token_stream</code>, <code>file_written</code>, and <code>sandbox_execution</code>.",
        styles['Body']
    ))
    pages.append(p9)

    return pages
