from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib import colors
from .common import USABLE_W, make_callout, make_table

def build_pug_part4_pages(styles):
    pages = []
    
    # PAGE 10: SECTION 8 - SCREENS 4 TO 6 DETAILED WALKTHROUGH
    p10 = []
    p10.append(Paragraph("Section 8: Screens 4 to 6 Detailed Engineering Walkthrough", styles['SecH1']))
    
    p10.append(Paragraph("Panel 4: Monospace Code Inspector", styles['SecH2']))
    p10.append(Paragraph(
        "<b>• Purpose:</b> Provides a clean, syntax-focused monospace viewer to inspect both existing codebase files and newly synthesized agent code.<br/>"
        "<b>• Key Widgets:</b> Read-only <code>QPlainTextEdit</code> styled with dark navy background (`#0A0E17`), light text (`#E2E8F0`), line numbering margins, and an explicit Consolas/Fira Code monospace font stack.<br/>"
        "<b>• User Interaction:</b> Clicking any file in the Panel 3 File Tree instantly loads the file into this inspector. When the Coder agent writes a file, the file is automatically selected and rendered.",
        styles['Body']
    ))
    p10.append(Spacer(1, 4))

    p10.append(Paragraph("Panel 5: Sandboxed Multi-Language Output Terminal", styles['SecH2']))
    p10.append(Paragraph(
        "<b>• Purpose:</b> Displays real-time compiler, interpreter, and test execution console output.<br/>"
        "<b>• Key Widgets:</b> Terminal-styled <code>QPlainTextEdit</code> with ANSI color-coding and automatic scroll-to-bottom behavior.<br/>"
        "<b>• Information Displayed:</b> The exact command executed (e.g. <code>gcc utils.c test_main.c -o test.exe</code>), duration in milliseconds, exit code (0 = success, 1+ = failure), and any stdout / stderr output.<br/>"
        "<b>• Role in Self-Healing:</b> Whenever red compiler errors appear in this terminal, the user watches the Debugger agent immediately activate to resolve them.",
        styles['Body']
    ))
    p10.append(Spacer(1, 4))

    p10.append(Paragraph("Panel 6: Agent Pipeline Status & Telemetry Cards", styles['SecH2']))
    p10.append(Paragraph(
        "<b>• Purpose:</b> Visual dashboard showing the exact status and deliverables of every agent in the pipeline.<br/>"
        "<b>• Key Widgets:</b> Four visual cards: (1) Planner Card, (2) Coder Card, (3) Tester Card, and (4) Debugger Card. Each card displays an animated status badge (Idle / Thinking / Success / Failed), the active model name, execution duration, and key output summaries.<br/>"
        "<b>• Developer Value:</b> Completely eliminates the 'black box' mystery of AI agents by showing exactly who is doing what in real time.",
        styles['Body']
    ))
    pages.append(p10)

    # PAGE 11: SECTION 9 - SYSTEM ARCHITECTURE EXPLAINED SIMPLY
    p11 = []
    p11.append(Paragraph("Section 9: System Architecture Explained Simply", styles['SecH1']))
    p11.append(Paragraph("9.1 Decoupled Multi-Tier Topology", styles['SecH2']))
    p11.append(Paragraph(
        "To ensure robust software engineering, DevForge AI is decoupled into five distinct layers:",
        styles['Body']
    ))

    arch_layers = [
        "<b>1. Client UI Tier (PySide6 / Qt):</b> High-performance desktop presentation layer; communicates with backend workers via thread-safe signals and slots.",
        "<b>2. Supervisor Orchestrator Core:</b> State machine managing lifecycle, task scheduling, prompt intent routing, and self-healing loops.",
        "<b>3. Agent Workforce:</b> Discrete agent instances (Planner, Coder, Tester, Debugger) operating with specialized system prompts and assigned models.",
        "<b>4. Production Code RAG Layer:</b> AST structural syntax extraction (`src/rag/ast_parser.py`) plus local vector embedding retrieval.",
        "<b>5. Sandboxed Execution Runtime:</b> Subprocess runner (`src/core/runner.py`) executing Python, C/C++ (MinGW GCC), and Node.js with strict 15s timeouts."
    ]
    for al in arch_layers:
        p11.append(Paragraph(al, styles['Bullet']))
    p11.append(Spacer(1, 8))

    p11.append(Paragraph("9.2 Asynchronous EventBus Architecture (`src/core/event_bus.py`)", styles['SecH2']))
    p11.append(Paragraph(
        "A major problem with desktop AI applications is UI freezing during heavy inference. DevForge AI completely prevents this by decoupling "
        "the Supervisor from the UI using a lightweight in-memory <b>EventBus</b>. The Supervisor runs in a separate daemon thread, posting events "
        "such as <code>pipeline_start</code>, <code>agent_activated</code>, <code>token_stream</code>, <code>file_written</code>, and <code>sandbox_execution</code>. "
        "The Qt UI subscribes to these events and updates its interface via Qt Signal bridges without ever blocking the main event loop.",
        styles['Body']
    ))
    pages.append(p11)

    # PAGE 12: SECTION 10 - SUPERVISOR / ORCHESTRATOR CORE MECHANISM
    p12 = []
    p12.append(Paragraph("Section 10: The Supervisor / Orchestrator Core Mechanism", styles['SecH1']))
    p12.append(Paragraph("10.1 Finite State Machine (FSM) Lifecycle", styles['SecH2']))
    p12.append(Paragraph(
        "The <code>Supervisor</code> class (`src/agents/supervisor.py`) enforces an orderly, deterministic lifecycle across nine discrete states:",
        styles['Body']
    ))

    fsm_table = [
        [Paragraph("Step / State", styles['TableHead']), Paragraph("Trigger Condition", styles['TableHead']), Paragraph("Orchestrator Operation & Event Dispatched", styles['TableHead'])],
        [Paragraph("<b>1. IDLE</b>", styles['TableCellBold']), Paragraph("Application launch", styles['TableCell']), Paragraph("Awaiting user prompt; EventBus initialized; UI controls active.", styles['TableCell'])],
        [Paragraph("<b>2. CLASSIFY</b>", styles['TableCellBold']), Paragraph("User clicks 'Run'", styles['TableCell']), Paragraph("Evaluates `_is_coding_task()`. Greetings route to conversational chat; code goals initiate pipeline.", styles['TableCell'])],
        [Paragraph("<b>3. RAG ENRICH</b>", styles['TableCellBold']), Paragraph("Coding task confirmed", styles['TableCell']), Paragraph("Queries `ast_parser.py` to analyze workspace files and appends structural outline to user prompt.", styles['TableCell'])],
        [Paragraph("<b>4. PLAN</b>", styles['TableCellBold']), Paragraph("Context enriched", styles['TableCell']), Paragraph("Dispatches goal to `PlannerAgent`; posts `agent_activated('Planner')`; receives architectural spec.", styles['TableCell'])],
        [Paragraph("<b>5. CODE</b>", styles['TableCellBold']), Paragraph("Plan generated", styles['TableCell']), Paragraph("Dispatches spec to `CoderAgent`; extracts files from markdown; writes files via `CodeRunner`.", styles['TableCell'])],
        [Paragraph("<b>6. TEST GEN</b>", styles['TableCellBold']), Paragraph("Files persisted", styles['TableCell']), Paragraph("Dispatches code to `TesterAgent`; receives test suite; writes `test_suite.py` or `test_main.c`.", styles['TableCell'])],
        [Paragraph("<b>7. EXECUTE</b>", styles['TableCellBold']), Paragraph("Test files written", styles['TableCell']), Paragraph("Invokes `CodeRunner.execute_any()`; captures stdout/stderr; posts `test_run_result`.", styles['TableCell'])],
        [Paragraph("<b>8. DEBUG</b>", styles['TableCellBold']), Paragraph("Test failed (exit != 0)", styles['TableCell']), Paragraph("Invokes `DebuggerAgent`; applies in-place code patch; re-executes tests (up to 3 retries).", styles['TableCell'])],
        [Paragraph("<b>9. COMPLETE</b>", styles['TableCellBold']), Paragraph("Tests pass or max retries", styles['TableCell']), Paragraph("Posts `pipeline_finished`; re-enables UI prompt input and buttons.", styles['TableCell'])]
    ]
    p12.append(make_table(["Step / State", "Trigger Condition", "Orchestrator Operation & Event Dispatched"], fsm_table[1:], [80, 110, 314], styles, "#1E3A8A"))
    pages.append(p12)

    return pages
