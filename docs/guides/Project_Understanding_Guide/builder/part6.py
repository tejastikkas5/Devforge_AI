from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib import colors
from .common import USABLE_W, make_callout, make_table

def build_pug_part6_pages(styles):
    pages = []
    
    # PAGE 16: SECTION 14 - CLOSED-LOOP AUTOMATED SANDBOXES & SELF-HEALING
    p16 = []
    p16.append(Paragraph("Section 14: Closed-Loop Automated Sandboxes & Self-Healing", styles['SecH1']))
    p16.append(Paragraph("14.1 The Local Execution Sandbox Architecture (`src/core/runner.py`)", styles['SecH2']))
    p16.append(Paragraph(
        "A critical failure point of traditional AI coding assistants is that they output code without ever running it. "
        "The developer is forced to copy code, run it in their terminal, encounter errors, and copy errors back. "
        "DevForge AI completely automates this loop through <code>CodeRunner</code>:",
        styles['Body']
    ))

    runner_capabilities = [
        "<b>• Python Test Suite Runner:</b> Invokes Python's native <code>unittest</code> engine as an isolated subprocess (<code>python -m unittest test_suite.py</code>). Captures test passes, assertion failures, and stack traces.",
        "<b>• Native MinGW GCC C/C++ Compiler:</b> Compiles multi-file C projects directly into native binaries (<code>gcc -Wall utils.c test_main.c -o test.exe</code>) and immediately executes the binary in the workspace sandbox.",
        "<b>• JavaScript / Node.js Engine:</b> Executes JS files directly using the local Node.js runtime (<code>node test_suite.js</code>).",
        "<b>• Subprocess Sandboxing & 15s Timeout:</b> Every execution is sandboxed within the active <code>workspace_dir</code>. A hard 15-second timeout kills any infinite loops cleanly without locking the UI thread."
    ]
    for rc in runner_capabilities:
        p16.append(Paragraph(rc, styles['Bullet']))
        p16.append(Spacer(1, 3))
    p16.append(Spacer(1, 6))

    p16.append(Paragraph("14.2 Multi-Language Sandbox Execution Matrix", styles['SecH2']))
    sandbox_table = [
        [Paragraph("Target Language", styles['TableHead']), Paragraph("Toolchain / Binary", styles['TableHead']), Paragraph("Execution Command Pattern", styles['TableHead']), Paragraph("Error Capture Target", styles['TableHead'])],
        [Paragraph("<b>Python 3.10+</b>", styles['TableCellBold']), Paragraph("python.exe (.venv)", styles['TableCell']), Paragraph("`python -m unittest &lt;test_file&gt;`", styles['TableCell']), Paragraph("AssertionError, NameError, SyntaxError", styles['TableCellMuted'])],
        [Paragraph("<b>C / C++</b>", styles['TableCellBold']), Paragraph("MinGW GCC", styles['TableCell']), Paragraph("`gcc -Wall &lt;src&gt; &lt;test&gt; -o out.exe && out.exe`", styles['TableCell']), Paragraph("Compiler warnings, linker errors, SIGSEGV", styles['TableCellMuted'])],
        [Paragraph("<b>JavaScript</b>", styles['TableCellBold']), Paragraph("Node.js", styles['TableCell']), Paragraph("`node &lt;test_file&gt;`", styles['TableCell']), Paragraph("TypeError, ReferenceError, Uncaught Exception", styles['TableCellMuted'])]
    ]
    p16.append(make_table(["Target Language", "Toolchain / Binary", "Execution Command Pattern", "Error Capture Target"], sandbox_table[1:], [85, 95, 174, 150], styles, "#1E3A8A"))
    pages.append(p16)

    # PAGE 17: SECTION 15 - THE SELF-HEALING ALGORITHM & RECOVERY LIMITS
    p17 = []
    p17.append(Paragraph("Section 15: The Self-Healing Algorithm & Recovery Limits", styles['SecH1']))
    p17.append(Paragraph("15.1 The Closed-Loop Auto-Repair Algorithm", styles['SecH2']))
    p17.append(Paragraph(
        "When `CodeRunner.execute_any()` returns a non-zero exit code or an execution error, the Supervisor does not give up. "
        "It triggers an automated self-healing loop:",
        styles['Body']
    ))

    healing_steps = [
        "<b>1. Interception:</b> Supervisor intercepts <code>test_result['stderr']</code> or compiler output from <code>stdout</code>.",
        "<b>2. Diagnosis:</b> The Supervisor formats a targeted prompt for <code>DebuggerAgent</code> containing: (a) Original source code, (b) Test suite code, (c) The raw error stack trace.",
        "<b>3. Patch Generation:</b> The Debugger (powered by <code>devstral</code> or <code>qwen2.5-coder</code>) identifies the root cause and generates corrected files.",
        "<b>4. Disk Write:</b> The Supervisor writes the patched files directly to the workspace.",
        "<b>5. Verification Re-Test:</b> The runner re-executes the test suite. If successful, the pipeline terminates green. If unsuccessful, the loop repeats up to a maximum of 3 iterations."
    ]
    for hs in healing_steps:
        p17.append(Paragraph(hs, styles['Bullet']))
        p17.append(Spacer(1, 3))
    p17.append(Spacer(1, 6))

    p17.append(Paragraph("15.2 Guardrails Against Infinite Loops", styles['SecH2']))
    guard_box = (
        "<b>The 3-Iteration Circuit Breaker:</b><br/>"
        "To prevent unbounded local token generation and runaway CPU usage, the self-healing loop is capped at exactly <b>3 retry attempts</b>. "
        "If the test fails on the 3rd attempt, the Supervisor posts a <code>pipeline_finished(status='debug_failed')</code> event, "
        "highlights the Debugger card in red, and presents the developer with a detailed failure report in Panel 5."
    )
    p17.append(make_callout(guard_box, styles, "#FEF2F2", "#F87171"))
    pages.append(p17)

    # PAGE 18: SECTION 16 - DATA MODELS, PYDANTIC SCHEMAS & IPC CONTRACTS
    p18 = []
    p18.append(Paragraph("Section 16: Data Models, Pydantic Schemas & IPC Contracts", styles['SecH1']))
    p18.append(Paragraph("16.1 Typed EventBus Topics & Payload Contracts", styles['SecH2']))
    p18.append(Paragraph(
        "All communications between the UI and backend workers are typed and validated. Table 16.1 documents all EventBus topics:",
        styles['Body']
    ))

    ipc_data = [
        [Paragraph("EventBus Topic", styles['TableHead']), Paragraph("Dispatched By", styles['TableHead']), Paragraph("Payload Structure (Python dict / JSON)", styles['TableHead']), Paragraph("UI Action / Consumer", styles['TableHead'])],
        [Paragraph("<code>pipeline_start</code>", styles['TableCellBold']), Paragraph("UI Controller", styles['TableCell']), Paragraph("`{\"goal\": str, \"workspace\": str}`", styles['TableCell']), Paragraph("Disables Run button; resets terminal.", styles['TableCellMuted'])],
        [Paragraph("<code>agent_activated</code>", styles['TableCellBold']), Paragraph("Supervisor", styles['TableCell']), Paragraph("`{\"agent\": str}` (e.g. 'Planner')", styles['TableCell']), Paragraph("Highlights active agent status card.", styles['TableCellMuted'])],
        [Paragraph("<code>token_stream</code>", styles['TableCellBold']), Paragraph("OllamaClient", styles['TableCell']), Paragraph("`{\"agent\": str, \"token\": str}`", styles['TableCell']), Paragraph("Appends streamed token to viewer.", styles['TableCellMuted'])],
        [Paragraph("<code>step_completed</code>", styles['TableCellBold']), Paragraph("Supervisor", styles['TableCell']), Paragraph("`{\"agent\": str, \"result\": str, ...}`", styles['TableCell']), Paragraph("Sets agent status card to Completed.", styles['TableCellMuted'])],
        [Paragraph("<code>file_written</code>", styles['TableCellBold']), Paragraph("CodeRunner", styles['TableCell']), Paragraph("`{\"filename\": str, \"filepath\": str}`", styles['TableCell']), Paragraph("Refreshes OS File Tree Explorer.", styles['TableCellMuted'])],
        [Paragraph("<code>sandbox_execution</code>", styles['TableCellBold']), Paragraph("CodeRunner", styles['TableCell']), Paragraph("`{\"message\": str}`", styles['TableCell']), Paragraph("Prints command banner in terminal.", styles['TableCellMuted'])],
        [Paragraph("<code>test_run_result</code>", styles['TableCellBold']), Paragraph("CodeRunner", styles['TableCell']), Paragraph("`{\"success\": bool, \"stdout\": str, ...}`", styles['TableCell']), Paragraph("Displays green/red test output.", styles['TableCellMuted'])],
        [Paragraph("<code>pipeline_finished</code>", styles['TableCellBold']), Paragraph("Supervisor", styles['TableCell']), Paragraph("`{\"status\": str, \"workspace\": str}`", styles['TableCell']), Paragraph("Re-enables UI controls and buttons.", styles['TableCellMuted'])]
    ]
    p18.append(make_table(["EventBus Topic", "Dispatched By", "Payload Structure (Python dict / JSON)", "UI Action / Consumer"], ipc_data[1:], [85, 75, 174, 170], styles, "#0F172A"))
    pages.append(p18)

    return pages
