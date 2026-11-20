from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib import colors
from .common import USABLE_W, make_callout, make_table

def build_pug_part3_pages(styles):
    pages = []
    
    # PAGE 7: SECTION 5 - PROPOSED SOLUTION & WORKFLOW
    p7 = []
    p7.append(Paragraph("Section 5: Our Proposed Solution & End-to-End Workflow", styles['SecH1']))
    p7.append(Paragraph("5.1 The 8-Stage Autonomous Engineering Pipeline", styles['SecH2']))
    p7.append(Paragraph(
        "DevForge AI transforms software engineering from disconnected manual prompt-and-paste cycles into an automated, "
        "reproducible eight-stage intelligence pipeline:",
        styles['Body']
    ))

    stages_data = [
        [Paragraph("Stage", styles['TableHead']), Paragraph("Active Engine / Agent", styles['TableHead']), Paragraph("Operational Process & Deliverable", styles['TableHead'])],
        [Paragraph("<b>1. Ingestion</b>", styles['TableCellBold']), Paragraph("PySide6 UI Console", styles['TableCell']), Paragraph("User inputs goal prompt; select target project workspace folder on disk.", styles['TableCell'])],
        [Paragraph("<b>2. Classification</b>", styles['TableCellBold']), Paragraph("Supervisor Router", styles['TableCell']), Paragraph("Evaluates prompt intent (`_is_coding_task`). Directs chit-chat to assistant or initiates engineering pipeline.", styles['TableCell'])],
        [Paragraph("<b>3. Context RAG</b>", styles['TableCellBold']), Paragraph("CodeASTAnalyzer", styles['TableCell']), Paragraph("Extracts AST syntax trees (classes, methods, imports) across existing workspace files.", styles['TableCell'])],
        [Paragraph("<b>4. Architecture</b>", styles['TableCellBold']), Paragraph("Planner Agent", styles['TableCell']), Paragraph("Generates step-by-step modular specification including required files, interfaces, and dependencies.", styles['TableCell'])],
        [Paragraph("<b>5. Synthesis</b>", styles['TableCellBold']), Paragraph("Coder Agent", styles['TableCell']), Paragraph("Synthesizes source code files according to architectural blueprint; persists files to workspace via CodeRunner.", styles['TableCell'])],
        [Paragraph("<b>6. Test Generation</b>", styles['TableCellBold']), Paragraph("Tester Agent", styles['TableCell']), Paragraph("Synthesizes comprehensive unit test harness (Python unittest, C assertions, or JS tests).", styles['TableCell'])],
        [Paragraph("<b>7. Sandbox Run</b>", styles['TableCellBold']), Paragraph("CodeRunner Sandbox", styles['TableCell']), Paragraph("Executes compiler/test harness in isolated subprocess; captures exit code, stdout, and stderr.", styles['TableCell'])],
        [Paragraph("<b>8. Self-Healing</b>", styles['TableCellBold']), Paragraph("Debugger Agent", styles['TableCell']), Paragraph("If tests fail, captures error trace and initiates in-place code repair loop (up to 3 retries).", styles['TableCell'])]
    ]
    p7.append(make_table(["Stage", "Active Engine / Agent", "Operational Process & Deliverable"], stages_data[1:], [80, 110, 314], styles, "#1E3A8A"))
    p7.append(Spacer(1, 8))

    p7.append(Paragraph("5.2 Critical Engineering Clarification: Decision Support vs. Production Deployment", styles['SecH2']))
    crit_clarification = (
        "<b>IMPORTANT:</b> DevForge AI generates, compiles, tests, and verifies code inside an isolated workspace sandbox. "
        "However, in high-assurance environments, the platform acts as an <b>accelerator co-pilot</b>. "
        "Production deployment to live corporate servers or customer-facing endpoints remains subject to final human code review "
        "and corporate CI/CD gate checks."
    )
    p7.append(make_callout(crit_clarification, styles, "#F0FDF4", "#16A34A"))
    pages.append(p7)

    # PAGE 8: SECTION 6 - COMPLETE DESKTOP APPLICATION SCREENS (PYSIDE6)
    p8 = []
    p8.append(Paragraph("Section 6: Complete Desktop Application Screens (PySide6)", styles['SecH1']))
    p8.append(Paragraph("6.1 Native PySide6 / Qt Desktop Architecture", styles['SecH2']))
    p8.append(Paragraph(
        "To deliver a responsive, zero-latency desktop experience that feels identical to Google Antigravity or VS Code, "
        "DevForge AI is built using <b>PySide6 (Qt for Python)</b>. The interface is laid out across six primary panels connected "
        "via native draggable splitters (<code>QSplitter</code>):",
        styles['Body']
    ))

    panels_list = [
        [Paragraph("Panel Number & Name", styles['TableHead']), Paragraph("Underlying Qt Component", styles['TableHead']), Paragraph("Functional Responsibility & User Interaction", styles['TableHead'])],
        [Paragraph("<b>Panel 1: Global Workspace Header</b>", styles['TableCellBold']), Paragraph("Header QFrame / QFileDialog", styles['TableCell']), Paragraph("Displays active workspace directory, browse button, and Ollama connection status heartbeat.", styles['TableCell'])],
        [Paragraph("<b>Panel 2: Prompt & Model Console</b>", styles['TableCellBold']), Paragraph("QTextEdit + QComboBox", styles['TableCell']), Paragraph("Allows developer to enter natural language goals, select models per agent, and click 'Run'.", styles['TableCell'])],
        [Paragraph("<b>Panel 3: Real-Time OS File Tree</b>", styles['TableCellBold']), Paragraph("QTreeView + QFileSystemModel", styles['TableCell']), Paragraph("Live OS filesystem explorer; tracks file additions, edits, and deletions with zero lag.", styles['TableCell'])],
        [Paragraph("<b>Panel 4: Monospace Code Inspector</b>", styles['TableCellBold']), Paragraph("QPlainTextEdit (Consolas)", styles['TableCell']), Paragraph("Read-only code viewer displaying any file clicked in the project explorer.", styles['TableCell'])],
        [Paragraph("<b>Panel 5: Sandboxed Output Terminal</b>", styles['TableCellBold']), Paragraph("QPlainTextEdit (CLI Stream)", styles['TableCell']), Paragraph("Live console showing GCC compiler output, unittest pass/fail results, and Node.js logs.", styles['TableCell'])],
        [Paragraph("<b>Panel 6: Agent Pipeline Status Cards</b>", styles['TableCellBold']), Paragraph("Custom Status Cards", styles['TableCell']), Paragraph("Color-coded status cards reflecting real-time state for Planner, Coder, Tester, and Debugger.", styles['TableCell'])]
    ]
    p8.append(make_table(["Panel Number & Name", "Underlying Qt Component", "Functional Responsibility & User Interaction"], panels_list[1:], [130, 120, 254], styles, "#0F172A"))
    p8.append(Spacer(1, 8))

    p8.append(Paragraph("6.2 Native OS Performance vs. Web Wrappers", styles['SecH2']))
    p8.append(Paragraph(
        "By choosing PySide6 over Chromium/Electron wrappers, DevForge AI uses under 150MB of baseline RAM, leaving over 95% of host memory "
        "available for Ollama model inference and local compilers. Panel resizing operates at native 60 FPS without layout recalculation stutter.",
        styles['Body']
    ))
    pages.append(p8)

    # PAGE 9: SECTION 7 - SCREENS 1 TO 3 DETAILED WALKTHROUGH
    p9 = []
    p9.append(Paragraph("Section 7: Screens 1 to 3 Detailed Engineering Walkthrough", styles['SecH1']))
    
    p9.append(Paragraph("Panel 1: Workspace Hub & Global Status Header", styles['SecH2']))
    p9.append(Paragraph(
        "<b>• Purpose:</b> Provides the operational anchor for project file selection and runtime status.<br/>"
        "<b>• Target User:</b> All developers and researchers.<br/>"
        "<b>• Key Widgets:</b> QLineEdit (displaying current path, e.g. <code>E:/Capstone_MITCORER/workspace</code>), QPushButton ('Browse Folder'), and QLabel ('Ollama Connected: http://127.0.0.1:11434' in green).<br/>"
        "<b>• Technical Implementation:</b> Clicking 'Browse' invokes <code>QFileDialog.getExistingDirectory()</code>. The new path is passed to <code>Supervisor.set_workspace()</code> and updates the root index of <code>QFileSystemModel</code>.",
        styles['Body']
    ))
    p9.append(Spacer(1, 4))

    p9.append(Paragraph("Panel 2: Natural Language Prompt & Model Console", styles['SecH2']))
    p9.append(Paragraph(
        "<b>• Purpose:</b> Captures the developer's high-level engineering requirement and configures model assignments.<br/>"
        "<b>• Key Widgets:</b> Multi-line <code>QTextEdit</code> for prompt entry, four <code>QComboBox</code> dropdowns (Planner Model, Coder Model, Tester Model, Debugger Model), and a primary <code>QPushButton</code> ('Run Multi-Agent Pipeline').<br/>"
        "<b>• User Flow:</b> The developer enters a prompt (e.g. 'Build a C palindrome utility with unit tests'). The user can leave model defaults or customize them. Clicking 'Run' disables input widgets and spawns <code>_run_pipeline()</code> on a background thread.",
        styles['Body']
    ))
    p9.append(Spacer(1, 4))

    p9.append(Paragraph("Panel 3: Real-Time OS File System Explorer", styles['SecH2']))
    p9.append(Paragraph(
        "<b>• Purpose:</b> Gives the developer instant, transparent visibility into project files created by the agents.<br/>"
        "<b>• Key Widgets:</b> <code>QTreeView</code> paired with <code>QFileSystemModel</code>, with filters to hide cache files (<code>__pycache__</code>, <code>.git</code>).<br/>"
        "<b>• Technical Implementation:</b> Because it binds directly to the OS filesystem model, newly generated files (e.g. <code>utils.c</code>, <code>test_main.c</code>) appear instantaneously the microsecond <code>CodeRunner.write_file()</code> executes, without requiring manual refresh.",
        styles['Body']
    ))
    pages.append(p9)

    return pages
