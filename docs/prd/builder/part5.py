from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib import colors
from .common import USABLE_W, make_callout, make_table

def build_part5_pages(styles):
    pages = []
    
    # PAGE 13: SECTION 11 - COMPLETE APPLICATION SCREEN ARCHITECTURE
    p13 = []
    p13.append(Paragraph("Section 11: Complete Application Screen Architecture", styles['SecH1']))
    p13.append(Paragraph("11.1 Native PySide6 / Qt User Interface Hierarchy", styles['SecH2']))
    p13.append(Paragraph(
        "DevForge AI delivers a high-performance native desktop application built with <b>PySide6 (Qt for Python)</b>. "
        "Unlike electron-based web wrappers that consume gigabytes of memory, the Qt native framework provides hardware-accelerated "
        "rendering, instant 60 FPS panel resizing, and deep OS-level filesystem integration.",
        styles['Body']
    ))
    p13.append(Paragraph(
        "The application is structured into a 6-panel modular layout organized through horizontal and vertical draggable splitters (<code>QSplitter</code>):",
        styles['Body']
    ))

    screens_summary = [
        [
            Paragraph("Screen / Panel", styles['TableHead']),
            Paragraph("Component Type", styles['TableHead']),
            Paragraph("Functional Role in Platform", styles['TableHead']),
            Paragraph("Engineering Tier", styles['TableHead'])
        ],
        [
            Paragraph("<b>Panel 1: Workspace Hub & Header</b>", styles['TableCellBold']),
            Paragraph("Header Bar / Modal", styles['TableCell']),
            Paragraph("Workspace folder selector, system health indicators, and Ollama connection status.", styles['TableCell']),
            Paragraph("P0 (Core)", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>Panel 2: Prompt & Model Console</b>", styles['TableCellBold']),
            Paragraph("Sidebar Input Panel", styles['TableCell']),
            Paragraph("Natural language goal input, one-click execution button, and dynamic model dropdowns.", styles['TableCell']),
            Paragraph("P0 (Core)", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>Panel 3: OS File Tree Explorer</b>", styles['TableCellBold']),
            Paragraph("QTreeView + QFileSystemModel", styles['TableCell']),
            Paragraph("Real-time hierarchical OS filesystem tree; tracks file additions, edits, and deletions live.", styles['TableCell']),
            Paragraph("P0 (Core)", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>Panel 4: Monospace Code Inspector</b>", styles['TableCellBold']),
            Paragraph("QPlainTextEdit (Inspector)", styles['TableCell']),
            Paragraph("Read-only code viewer displaying any file clicked in the project explorer.", styles['TableCell']),
            Paragraph("P0 (Core)", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>Panel 5: Multi-Language Terminal</b>", styles['TableCellBold']),
            Paragraph("QPlainTextEdit (Log/CLI)", styles['TableCell']),
            Paragraph("Live execution console displaying GCC compiler output, unittest traces, and Node.js logs.", styles['TableCell']),
            Paragraph("P0 (Core)", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>Panel 6: Agent Pipeline Status Cards</b>", styles['TableCellBold']),
            Paragraph("Status Dashboard Tab", styles['TableCell']),
            Paragraph("Color-coded real-time state cards for Supervisor, Planner, Coder, Tester, and Debugger.", styles['TableCell']),
            Paragraph("P0 (Core)", styles['TableCellBold'])
        ]
    ]
    p13.append(make_table(["Screen / Panel", "Component Type", "Functional Role in Platform", "Engineering Tier"], screens_summary[1:], [120, 110, 204, 70], styles, "#0F172A"))
    p13.append(Spacer(1, 10))

    p13.append(Paragraph("11.2 Theme & Design Philosophy", styles['SecH2']))
    p13.append(Paragraph(
        "The interface uses a modern deep dark navy theme (`#070A10`, `#0A0E17`, `#1E293B`, `#2563EB`) engineered to match modern IDE "
        "standards (such as Google Antigravity and VS Code). Draggable splitter borders allow developers to expand the code inspector, "
        "terminal, or agent telemetry panels fluidly.",
        styles['Body']
    ))
    pages.append(p13)

    # PAGE 14: SECTION 12 - SCREENS 1 TO 3 DETAILED SPECIFICATIONS
    p14 = []
    p14.append(Paragraph("Section 12: Screens 1 to 3 Detailed Specifications", styles['SecH1']))
    
    # Screen 1
    p14.append(Paragraph("Panel 1: Workspace Hub & Global Status Header", styles['SecH2']))
    s1_spec = [
        "<b>• Purpose:</b> Provides persistent workspace management, folder selection, and engine heartbeat status.",
        "<b>• UI Components:</b> App title badge ('DevForge AI'), Active Workspace Path input with 'Browse' button, Ollama Server status pill (Green = Connected, Red = Disconnected), and Memory Usage gauge.",
        "<b>• User Actions:</b> Click 'Browse' to switch active project directory (e.g. <code>E:/Capstone_MITCORER/workspace</code>); click 'Refresh' to re-verify Ollama heartbeat.",
        "<b>• Backend Events:</b> Emits <code>workspace_changed</code>; triggers <code>CodeRunner.set_workspace()</code> and updates file explorer root path."
    ]
    for s in s1_spec:
        p14.append(Paragraph(s, styles['Bullet']))
    p14.append(Spacer(1, 6))

    # Screen 2
    p14.append(Paragraph("Panel 2: Natural Language Prompt & Model Routing Console", styles['SecH2']))
    s2_spec = [
        "<b>• Purpose:</b> Ingests user engineering goals and configures model assignments for each sub-agent.",
        "<b>• UI Components:</b> Multi-line goal input text area (<code>QTextEdit</code>), 'Run Multi-Agent Pipeline' primary button, and four model dropdown selectors (Planner Model, Coder Model, Tester Model, Debugger Model).",
        "<b>• User Actions:</b> Type developer prompt (e.g. 'Build a C palindrome checker with unit tests and utils header'), select target models from dropdowns, and click Run.",
        "<b>• Backend Events:</b> Invokes <code>Supervisor.start_pipeline_async(user_request)</code> in background worker thread; disables input during active run."
    ]
    for s in s2_spec:
        p14.append(Paragraph(s, styles['Bullet']))
    p14.append(Spacer(1, 6))

    # Screen 3
    p14.append(Paragraph("Panel 3: Real-Time OS File System Explorer", styles['SecH2']))
    s3_spec = [
        "<b>• Purpose:</b> Displays real-time hierarchical project files directly from the operating system.",
        "<b>• UI Components:</b> Native <code>QTreeView</code> bound to <code>QFileSystemModel</code>; automatically watches OS file creation, deletion, and edit events.",
        "<b>• User Actions:</b> Expand/collapse directories; single-click on any source file (<code>.py</code>, <code>.c</code>, <code>.h</code>, <code>.js</code>, <code>.md</code>) to load its contents into Panel 4.",
        "<b>• Backend Events:</b> Listens to <code>file_written</code> events emitted by Supervisor and highlights newly written files."
    ]
    for s in s3_spec:
        p14.append(Paragraph(s, styles['Bullet']))
    pages.append(p14)

    # PAGE 15: SECTION 13 - SCREENS 4 TO 6 DETAILED SPECIFICATIONS
    p15 = []
    p15.append(Paragraph("Section 13: Screens 4 to 6 Detailed Specifications", styles['SecH1']))
    
    # Screen 4
    p15.append(Paragraph("Panel 4: Monospace Code Inspector (Multi-Tab Viewer)", styles['SecH2']))
    s4_spec = [
        "<b>• Purpose:</b> Provides high-readability syntax inspection for generated and existing project code.",
        "<b>• UI Components:</b> Read-only monospace editor (<code>QPlainTextEdit</code>) using `Consolas` / `Fira Code` font, file tab bar displaying current open filename, line number counter, and 'Copy to Clipboard' button.",
        "<b>• Information Displayed:</b> Complete source code of selected file; displays newly synthesized code as soon as the Coder or Debugger completes file generation.",
        "<b>• User Actions:</b> Scroll through code, copy snippets, inspect AST extracted signatures."
    ]
    for s in s4_spec:
        p15.append(Paragraph(s, styles['Bullet']))
    p15.append(Spacer(1, 6))

    # Screen 5
    p15.append(Paragraph("Panel 5: Sandboxed Multi-Language Output Terminal", styles['SecH2']))
    s5_spec = [
        "<b>• Purpose:</b> Real-time terminal reflecting automated compiler and test execution runs.",
        "<b>• UI Components:</b> Monospace dark CLI terminal panel; auto-scrolls to bottom on new output; color-coded output (Green = Passing test / Zero exit code, Red = Compiler error or assertion failure, Amber = Execution warning).",
        "<b>• Information Displayed:</b> Full command executed (e.g. <code>gcc main.c test_main.c -o test.exe</code>), execution duration (ms), <code>stdout</code>, and <code>stderr</code> traces.",
        "<b>• Backend Events:</b> Receives <code>sandbox_execution</code> and <code>test_run_result</code> events from <code>EventBus</code>."
    ]
    for s in s5_spec:
        p15.append(Paragraph(s, styles['Bullet']))
    p15.append(Spacer(1, 6))

    # Screen 6
    p15.append(Paragraph("Panel 6: Agent Pipeline Status & Telemetry Cards", styles['SecH2']))
    s6_spec = [
        "<b>• Purpose:</b> Visual dashboard displaying real-time state, token counts, and outputs of all agents in the pipeline.",
        "<b>• UI Components:</b> Four distinct cards: (1) Planner Card, (2) Coder Card, (3) Tester Card, and (4) Debugger Card. Each card features an animated status pill ('Idle', 'Active / Thinking', 'Completed', 'Failed').",
        "<b>• Information Displayed:</b> Active model name, latency timestamp, summary of generated plan, list of files written, test suite outcome, and bug diagnostic notes.",
        "<b>• User Actions:</b> Click on any card to view detailed raw reasoning tokens and system prompt logs."
    ]
    for s in s6_spec:
        p15.append(Paragraph(s, styles['Bullet']))
    pages.append(p15)

    return pages
