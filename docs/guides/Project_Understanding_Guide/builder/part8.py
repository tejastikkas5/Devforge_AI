from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib import colors
from .common import USABLE_W, make_callout, make_table

def build_pug_part8_pages(styles):
    pages = []
    
    # PAGE 22: SECTION 20 - EDGE-CASE TEST SUITE & VERIFICATION MATRIX
    p22 = []
    p22.append(Paragraph("Section 20: Edge-Case Test Suite & Verification Matrix", styles['SecH1']))
    p22.append(Paragraph("20.1 Technical Test Suite Specification", styles['SecH2']))
    p22.append(Paragraph(
        "Before demonstrating DevForge AI to technical panels or deploying in corporate environments, the engineering team "
        "must execute and pass the following rigorous test suite:",
        styles['Body']
    ))

    test_matrix = [
        [Paragraph("Test ID", styles['TableHead']), Paragraph("Test Category & Condition", styles['TableHead']), Paragraph("Expected System Behavior", styles['TableHead']), Paragraph("Automated Assertion Rule", styles['TableHead']), Paragraph("Tier", styles['TableHead'])],
        [Paragraph("<b>TC-EDG-01</b>", styles['TableCellBold']), Paragraph("Casual Conversational Chat<br/>(e.g. 'hello, how are you?')", styles['TableCell']), Paragraph("Supervisor identifies non-coding goal; streams friendly reply without writing files.", styles['TableCell']), Paragraph("<code>pipeline_finished.status == 'chat_completed' && files_written == 0</code>", styles['TableCellMuted']), Paragraph("P0", styles['TableCellBold'])],
        [Paragraph("<b>TC-EDG-02</b>", styles['TableCellBold']), Paragraph("Malformed Python Code<br/>(Missing colon / Indentation error)", styles['TableCell']), Paragraph("<code>CodeASTAnalyzer</code> catches SyntaxError gracefully without crashing.", styles['TableCell']), Paragraph("<code>ast_data['syntax_valid'] == False && ast_data['error'] != None</code>", styles['TableCellMuted']), Paragraph("P0", styles['TableCellBold'])],
        [Paragraph("<b>TC-EDG-03</b>", styles['TableCellBold']), Paragraph("Missing C Header File<br/>(e.g. `#include &lt;nonexistent.h&gt;`)", styles['TableCell']), Paragraph("GCC fails with error; Debugger intercepts stderr and removes bad header.", styles['TableCell']), Paragraph("<code>retest_result['success'] == True && retry_count &lt;= 2</code>", styles['TableCellMuted']), Paragraph("P0", styles['TableCellBold'])],
        [Paragraph("<b>TC-EDG-04</b>", styles['TableCellBold']), Paragraph("Infinite Subprocess Loop<br/>(`while True: pass`)", styles['TableCell']), Paragraph("CodeRunner kills process at 15.0s timeout; UI remains fully responsive.", styles['TableCell']), Paragraph("<code>result['timed_out'] == True && elapsed_time &lt; 16.0s</code>", styles['TableCellMuted']), Paragraph("P0", styles['TableCellBold'])],
        [Paragraph("<b>TC-EDG-05</b>", styles['TableCellBold']), Paragraph("Ollama Server Disconnected<br/>(Daemon process killed)", styles['TableCell']), Paragraph("Client catches ConnectionRefusedError; displays red status pill in UI.", styles['TableCell']), Paragraph("<code>ui_status_pill == 'Disconnected' && app_crashed == False</code>", styles['TableCellMuted']), Paragraph("P0", styles['TableCellBold'])],
        [Paragraph("<b>TC-EDG-06</b>", styles['TableCellBold']), Paragraph("Non-Existent Directory Target<br/>(Invalid workspace path)", styles['TableCell']), Paragraph("Supervisor rejects path; prompts user with safe fallback to `./workspace`.", styles['TableCell']), Paragraph("<code>os.path.exists(active_workspace) == True</code>", styles['TableCellMuted']), Paragraph("P0", styles['TableCellBold'])]
    ]
    p22.append(make_table(["Test ID", "Test Category & Condition", "Expected System Behavior", "Automated Assertion Rule", "Tier"], test_matrix[1:], [55, 110, 150, 159, 30], styles, "#1E3A8A"))
    pages.append(p22)

    # PAGE 23: SECTION 21 - LIVE EVALUATION & DEMONSTRATION CHECKLIST
    p23 = []
    p23.append(Paragraph("Section 21: Live Evaluation & Demonstration Checklist", styles['SecH1']))
    p23.append(Paragraph("21.1 Scripted 5-Minute Competition Demonstration Walkthrough", styles['SecH2']))
    p23.append(Paragraph(
        "Follow this exact choreographed sequence when presenting DevForge AI to evaluators or industry panels:",
        styles['Body']
    ))

    demo_steps = [
        "<b>☐ Step 1: Introduction (30 seconds):</b> State the core problem: enterprise software teams face prohibitive cloud API bills ($20k–$100k/yr) and strict IP exfiltration bans. Introduce DevForge AI as the 100% private, air-gapped local solution.",
        "<b>☐ Step 2: Architecture & 'The Catch' (45 seconds):</b> Explain that traditional prototypes fail by using a single small model for all tasks. Introduce our <b>Dynamic Heterogeneous Model Router</b> and <b>Production AST Code RAG</b>.",
        "<b>☐ Step 3: Prompt Ingestion (30 seconds):</b> On Panel 2, enter the C palindrome requirement. Highlight the dynamic model dropdowns showing <code>codestral</code> selected for coding and <code>codegemma</code> for testing. Click 'Run'.",
        "<b>☐ Step 4: Live Telemetry & Streaming (60 seconds):</b> Show the Planner card activate, followed by real-time token streaming from the Coder agent. Point out the live OS File Tree in Panel 3 updating as files are created.",
        "<b>☐ Step 5: Sandboxed Compilation & Verification (60 seconds):</b> Open Panel 5. Watch MinGW GCC compile the C files and execute the test suite in real time. Point out the green passing test assertions.",
        "<b>☐ Step 6: Automated Self-Healing Demo (45 seconds):</b> Intentionally introduce a syntax typo in <code>utils.c</code> and click re-test. Watch the Debugger card light up, diagnose the error trace from stderr, patch the code, and re-test to green automatically.",
        "<b>☐ Step 7: Conclusion & Q&A (30 seconds):</b> Reiterate zero cloud token cost, 100% data air-gapping, and invite questions from the panel."
    ]
    for ds in demo_steps:
        p23.append(Paragraph(ds, styles['Bullet']))
        p23.append(Spacer(1, 2))
    pages.append(p23)

    # PAGE 24: SECTION 22 - HARDWARE SIZING & STORAGE GUIDE
    p24 = []
    p24.append(Paragraph("Section 22: Hardware Resource Sizing & Storage Guide", styles['SecH1']))
    p24.append(Paragraph("22.1 Quantized GGUF Profiles & VRAM Allocation", styles['SecH2']))
    p24.append(Paragraph(
        "To ensure reliable execution without Out-Of-Memory (OOM) crashes, DevForge AI is tested across three primary hardware tiers:",
        styles['Body']
    ))

    hw_profile_data = [
        [Paragraph("Developer Hardware Tier", styles['TableHead']), Paragraph("GPU & RAM Profile", styles['TableHead']), Paragraph("Recommended Ollama Model Stack", styles['TableHead']), Paragraph("Memory Optimization Strategy", styles['TableHead'])],
        [Paragraph("<b>Entry Developer Laptop</b>", styles['TableCellBold']), Paragraph("4GB VRAM (GTX 1650)<br/>16GB–24GB System RAM", styles['TableCell']), Paragraph("qwen2.5-coder:7b (Q4_K_M)<br/>codegemma:2b (Q4)", styles['TableCell']), Paragraph("Sequential model execution; Ollama keep-alive: 5m; strict AST token pruning.", styles['TableCellMuted'])],
        [Paragraph("<b>Mid-Range Workstation</b>", styles['TableCellBold']), Paragraph("8GB–12GB VRAM (RTX 3060/4060)<br/>32GB System RAM", styles['TableCell']), Paragraph("deepseek-coder-v2:16b (Q4)<br/>codestral:22b (Q4_K_M)", styles['TableCell']), Paragraph("Partial offload; 2 concurrent models in RAM; full vector similarity search enabled.", styles['TableCellMuted'])],
        [Paragraph("<b>Enterprise Server Node</b>", styles['TableCellBold']), Paragraph("24GB+ VRAM (RTX 4090 / A6000)<br/>64GB+ System RAM", styles['TableCell']), Paragraph("Full 16-bit / 8-bit quantized models:<br/>codestral:22b + devstral:24b", styles['TableCell']), Paragraph("All models permanently resident in VRAM; zero load latency; parallel test runs.", styles['TableCellMuted'])]
    ]
    p24.append(make_table(["Developer Hardware Tier", "GPU & RAM Profile", "Recommended Ollama Model Stack", "Memory Optimization Strategy"], hw_profile_data[1:], [100, 110, 140, 154], styles, "#1E3A8A"))
    p24.append(Spacer(1, 8))

    p24.append(Paragraph("22.2 Drive C: Storage Protection", styles['SecH2']))
    storage_box = (
        "<b>Storage Allocation Protocol:</b><br/>"
        "Large Language Model weights require tens of gigabytes. To protect the developer's primary OS drive (Drive C:) from disk exhaustion, "
        "DevForge AI permanently sets <code>OLLAMA_MODELS</code> to <code>E:\\OllamaModels</code> (configured with 200GB+ free space). "
        "The Python virtual environment is isolated strictly at <code>E:\\Capstone_MITCORER\\.venv</code>."
    )
    p24.append(make_callout(storage_box, styles, "#F8FAFC", "#CBD5E1"))
    pages.append(p24)

    return pages
