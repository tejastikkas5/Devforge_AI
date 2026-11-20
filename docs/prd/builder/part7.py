import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.lib import colors
from .common import USABLE_W, make_callout, make_table

def build_part7_pages(styles):
    pages = []
    
    # PAGE 19: SECTION 17 - DATA CONTRACTS & IPC MESSAGE SCHEMAS
    p19 = []
    p19.append(Paragraph("Section 17: Data Contracts & IPC Message Schemas", styles['SecH1']))
    p19.append(Paragraph("17.1 Inter-Agent Communication & EventBus Protocol", styles['SecH2']))
    p19.append(Paragraph(
        "Communication between the UI, the Supervisor, and sub-agents is decoupled via a typed publish-subscribe <code>EventBus</code>. "
        "The following event schemas govern pipeline transitions:",
        styles['Body']
    ))
    
    events_data = [
        [
            Paragraph("Event Topic", styles['TableHead']),
            Paragraph("Payload Schema", styles['TableHead']),
            Paragraph("Trigger & Purpose", styles['TableHead'])
        ],
        [
            Paragraph("<code>pipeline_start</code>", styles['TableCellBold']),
            Paragraph("<code>{\"goal\": str, \"workspace\": str}</code>", styles['TableCell']),
            Paragraph("Dispatched by UI when user clicks 'Run'. Initializes agent state cards and resets logs.", styles['TableCell'])
        ],
        [
            Paragraph("<code>agent_activated</code>", styles['TableCellBold']),
            Paragraph("<code>{\"agent\": str}</code> (e.g. 'Planner')", styles['TableCell']),
            Paragraph("Dispatched when a specific agent begins thinking. Highlights active agent card in UI.", styles['TableCell'])
        ],
        [
            Paragraph("<code>token_stream</code>", styles['TableCellBold']),
            Paragraph("<code>{\"agent\": str, \"token\": str}</code>", styles['TableCell']),
            Paragraph("Dispatched in real-time as Ollama streams tokens. Updates terminal / code view dynamically.", styles['TableCell'])
        ],
        [
            Paragraph("<code>file_written</code>", styles['TableCellBold']),
            Paragraph("<code>{\"filename\": str, \"filepath\": str, \"content\": str}</code>", styles['TableCell']),
            Paragraph("Dispatched when Coder or Debugger persists a file. Triggers OS file tree view refresh.", styles['TableCell'])
        ],
        [
            Paragraph("<code>sandbox_execution</code>", styles['TableCellBold']),
            Paragraph("<code>{\"message\": str}</code>", styles['TableCell']),
            Paragraph("Dispatched when CodeRunner executes a compiler or test suite command.", styles['TableCell'])
        ],
        [
            Paragraph("<code>test_run_result</code>", styles['TableCellBold']),
            Paragraph("<code>{\"success\": bool, \"stdout\": str, \"stderr\": str, \"exit_code\": int}</code>", styles['TableCell']),
            Paragraph("Dispatched upon test completion. Triggers Debugger if success is false.", styles['TableCell'])
        ],
        [
            Paragraph("<code>pipeline_finished</code>", styles['TableCellBold']),
            Paragraph("<code>{\"status\": str, \"workspace\": str}</code>", styles['TableCell']),
            Paragraph("Dispatched upon successful verification or final termination. Re-enables UI input controls.", styles['TableCell'])
        ]
    ]
    p19.append(make_table(["Event Topic", "Payload Schema", "Trigger & Purpose"], events_data[1:], [110, 160, 234], styles, "#1E3A8A"))
    pages.append(p19)

    # PAGE 20: SECTION 18 - END-TO-END USER JOURNEY WALKTHROUGH
    p20 = []
    p20.append(Paragraph("Section 18: End-to-End User Journey Walkthrough", styles['SecH1']))
    p20.append(Paragraph("18.1 Concrete Execution Case: The Pune Capstone Task", styles['SecH2']))
    p20.append(Paragraph(
        "To verify all technical components in a realistic scenario, consider a developer instructing DevForge AI: "
        "<i>'Build a modular C string reversal and palindrome checking utility with header files and automated unit tests.'</i>",
        styles['Body']
    ))
    
    journey_steps = [
        "<b>Step 1 (Ingestion & Routing):</b> Developer inputs prompt into Panel 2. The Supervisor analyzes prompt intent, confirms a coding task, and queries <code>src/rag/ast_parser.py</code> to inspect existing files in <code>workspace/</code>.",
        "<b>Step 2 (Architectural Planning):</b> Supervisor invokes <code>PlannerAgent</code> (powered by <code>deepseek-coder-v2:16b</code>). The Planner outputs a 3-part specification: (1) <code>utils.h</code> declaring function prototypes, (2) <code>utils.c</code> implementing logic, and (3) <code>test_main.c</code> containing unit test assertions.",
        "<b>Step 3 (Code Synthesis):</b> <code>CoderAgent</code> (powered by <code>codestral:22b</code>) generates the header and implementation files. The Supervisor extracts markdown code blocks and invokes <code>CodeRunner.write_file()</code>.",
        "<b>Step 4 (Automated Testing):</b> <code>TesterAgent</code> (powered by <code>codegemma:7b</code>) synthesizes the test harness. The Supervisor writes <code>test_main.c</code>.",
        "<b>Step 5 (Sandboxed Compilation & Execution):</b> <code>CodeRunner</code> invokes MinGW GCC: <code>gcc -Wall utils.c test_main.c -o test.exe</code> followed by execution. The terminal panel displays live GCC compiler output.",
        "<b>Step 6 (Closed-Loop Debugging):</b> If GCC reports a compiler warning or assertion failure (e.g. missing <code>#include &lt;stdbool.h&gt;</code>), the Supervisor intercepts <code>stderr</code>, activates <code>DebuggerAgent</code> (<code>devstral:24b</code>), applies the in-place fix, and re-executes tests until green.",
        "<b>Step 7 (Final Delivery):</b> All tests pass. The UI file explorer shows the green status, and the developer can immediately inspect the code in Panel 4."
    ]
    for js in journey_steps:
        p20.append(Paragraph(js, styles['Bullet']))
    pages.append(p20)

    # PAGE 21: SECTION 19 - SEVEN-PHASE IMPLEMENTATION ROADMAP
    p21 = []
    p21.append(Paragraph("Section 19: Seven-Phase Implementation Roadmap", styles['SecH1']))
    p21.append(Paragraph("19.1 Project Phases & Engineering Timeline", styles['SecH2']))
    p21.append(Paragraph(
        "The project follows a structured 7-phase timeline covering 13+ months from initial literature research through commercial pilots:",
        styles['Body']
    ))

    phases_img_path = r"E:\Capstone_MITCORER\docs\prd\phases.png"
    if os.path.exists(phases_img_path):
        img_phases = RLImage(phases_img_path, width=504, height=220)
        p21.append(img_phases)
        p21.append(Spacer(1, 8))

    phases_detail = [
        "<b>Phase 1: Literature Survey & Research (Month 1):</b> Study existing frameworks (MetaGPT, Devin, SWE-bench); define local multi-agent research questions.",
        "<b>Phase 2: Ollama Model Benchmarking (Months 2–3):</b> Evaluate Qwen, Codestral, DeepSeek, and Devstral on local hardware across HumanEval & MBPP.",
        "<b>Phase 3: Multi-Agent Architecture (Months 4–5):</b> Formalize Supervisor state machine, inter-agent communication, and PySide6 EventBus.",
        "<b>Phase 4: RAG Implementation (Months 6–7):</b> Implement AST syntax parsing, local vector embeddings, and token-saving context injection.",
        "<b>Phase 5: Platform Development (Months 8–10):</b> Build PySide6 dark UI, native splitters, OS file explorer, and multi-language compiler runners.",
        "<b>Phase 6: Experiments & Evaluation (Months 11–12):</b> Conduct comparative trials: Single-Model vs. Heterogeneous Multi-Model across 100 coding tasks.",
        "<b>Phase 7: Analysis & Research Paper (Month 13+):</b> Document findings, publish academic paper, and launch open-source enterprise package."
    ]
    for pd in phases_detail:
        p21.append(Paragraph(pd, styles['Bullet']))
    pages.append(p21)

    return pages
