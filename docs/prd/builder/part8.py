from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib import colors
from .common import USABLE_W, make_callout, make_table

def build_part8_pages(styles):
    pages = []
    
    # PAGE 22: SECTION 20 - COMPREHENSIVE VERIFICATION & TEST SUITE
    p22 = []
    p22.append(Paragraph("Section 20: Comprehensive Verification & Test Suite", styles['SecH1']))
    p22.append(Paragraph("20.1 Edge-Case & System Robustness Test Suite", styles['SecH2']))
    p22.append(Paragraph(
        "Before deploying DevForge AI or presenting to evaluators, the platform must successfully pass the following automated test matrix:",
        styles['Body']
    ))
    
    test_rows = [
        [
            Paragraph("Test ID", styles['TableHead']),
            Paragraph("Category & Input Condition", styles['TableHead']),
            Paragraph("Expected System Behavior", styles['TableHead']),
            Paragraph("Automated Assertion Rule", styles['TableHead']),
            Paragraph("Tier", styles['TableHead'])
        ],
        [
            Paragraph("<b>TC-INT-01</b>", styles['TableCellBold']),
            Paragraph("Casual Greeting<br/>(e.g. 'hello, how are you?')", styles['TableCell']),
            Paragraph("Supervisor identifies chat intent; streams friendly reply without invoking Coder or writing files.", styles['TableCell']),
            Paragraph("<code>pipeline_finished.status == 'chat_completed' && files_written == 0</code>", styles['TableCellMuted']),
            Paragraph("P0", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>TC-AST-01</b>", styles['TableCellBold']),
            Paragraph("Complex Python File<br/>(Classes, Decorators, Async)", styles['TableCell']),
            Paragraph("<code>CodeASTAnalyzer</code> extracts class tree, function arguments, and docstrings in &lt;100ms.", styles['TableCell']),
            Paragraph("<code>ast_data['syntax_valid'] == True && len(classes) &gt; 0</code>", styles['TableCellMuted']),
            Paragraph("P0", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>TC-RUN-01</b>", styles['TableCellBold']),
            Paragraph("C Compilation<br/>(MinGW GCC with utils header)", styles['TableCell']),
            Paragraph("Compiles multi-file C project; executes binary and captures stdout/stderr.", styles['TableCell']),
            Paragraph("<code>result['success'] == True && result['exit_code'] == 0</code>", styles['TableCellMuted']),
            Paragraph("P0", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>TC-DBG-01</b>", styles['TableCellBold']),
            Paragraph("Intentional Syntax Bug<br/>(Missing colon in Python)", styles['TableCell']),
            Paragraph("Unit test fails; Supervisor intercepts stderr; Debugger agent fixes syntax error automatically.", styles['TableCell']),
            Paragraph("<code>retest_result['success'] == True && retry_count &lt;= 2</code>", styles['TableCellMuted']),
            Paragraph("P0", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>TC-OOM-01</b>", styles['TableCellBold']),
            Paragraph("Constrained VRAM (4GB)<br/>(Sequential model load)", styles['TableCell']),
            Paragraph("Unloads previous model before instantiating next model; zero CUDA out-of-memory errors.", styles['TableCell']),
            Paragraph("<code>cuda_oom_detected == False && pipeline_completed == True</code>", styles['TableCellMuted']),
            Paragraph("P0", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>TC-SAFE-01</b>", styles['TableCellBold']),
            Paragraph("Infinite Loop Execution<br/>(<code>while True: pass</code>)", styles['TableCell']),
            Paragraph("Subprocess runner enforces 15-second timeout; kills child process cleanly without freezing UI.", styles['TableCell']),
            Paragraph("<code>result['timed_out'] == True && elapsed_time &lt; 16.0s</code>", styles['TableCellMuted']),
            Paragraph("P0", styles['TableCellBold'])
        ]
    ]
    p22.append(make_table(["Test ID", "Category & Input Condition", "Expected System Behavior", "Automated Assertion Rule", "Tier"], test_rows[1:], [55, 110, 150, 159, 30], styles, "#1E3A8A"))
    pages.append(p22)

    # PAGE 23: SECTION 21 - QUANTITATIVE BENCHMARKS & KPIS
    p23 = []
    p23.append(Paragraph("Section 21: Quantitative Benchmarks & KPIs", styles['SecH1']))
    p23.append(Paragraph("21.1 Core Platform Metrics & Verification Protocols", styles['SecH2']))
    p23.append(Paragraph(
        "To objectively validate the performance gains of dynamic heterogeneous routing and hybrid RAG over the single-model baseline, "
        "DevForge AI establishes five primary KPIs:",
        styles['Body']
    ))

    kpi_rows = [
        [
            Paragraph("KPI Dimension", styles['TableHead']),
            Paragraph("Baseline Benchmark<br/>(Single 1.5B/7B Model)", styles['TableHead']),
            Paragraph("Target Benchmark<br/>(DevForge AI Heterogeneous)", styles['TableHead']),
            Paragraph("Rigorous Measurement Protocol", styles['TableHead'])
        ],
        [
            Paragraph("<b>First-Pass Synthesis Quality</b>", styles['TableCellBold']),
            Paragraph("42.0% Pass@1<br/>(Frequent syntax/import bugs)", styles['TableCell']),
            Paragraph("<b>≥ 78.0% Pass@1</b><br/>(With Codestral/DeepSeek routing)", styles['TableCellBold']),
            Paragraph("Automated execution of 50 standard algorithmic and system utility tasks in test workspace.", styles['TableCellMuted'])
        ],
        [
            Paragraph("<b>Autonomous Bug Healing Rate</b>", styles['TableCellBold']),
            Paragraph("35.0% within 3 iterations<br/>(Small models repeat errors)", styles['TableCell']),
            Paragraph("<b>≥ 82.0% within 3 iterations</b><br/>(With Devstral specialized debugger)", styles['TableCellBold']),
            Paragraph("Inject 30 intentional syntax, type, and logic bugs into workspace; record autonomous resolution rate.", styles['TableCellMuted'])
        ],
        [
            Paragraph("<b>Context Window Compression</b>", styles['TableCellBold']),
            Paragraph("0% Reduction<br/>(Raw source file dumps)", styles['TableCell']),
            Paragraph("<b>65% – 85% Token Reduction</b><br/>(Via AST structural summaries)", styles['TableCellBold']),
            Paragraph("Token counter comparing raw file characters vs. AST extracted symbol outlines across 20-file project.", styles['TableCellMuted'])
        ],
        [
            Paragraph("<b>End-to-End Task Latency</b>", styles['TableCellBold']),
            Paragraph("180 seconds<br/>(Bloated prompt / slow context)", styles['TableCell']),
            Paragraph("<b>&lt; 60 seconds</b><br/>(Pruned context + specialized routing)", styles['TableCellBold']),
            Paragraph("Total wall-clock duration from user prompt input to verified green test suite execution.", styles['TableCellMuted'])
        ],
        [
            Paragraph("<b>Inference Cloud Expenditure</b>", styles['TableCellBold']),
            Paragraph("$1,500 – $3,500<br/>(Cloud API tokens per 1k tasks)", styles['TableCell']),
            Paragraph("<b>$0.00</b><br/>(100% Local GPU compute)", styles['TableCellBold']),
            Paragraph("Calculated token equivalence against OpenAI GPT-4o / Claude 3.5 API pricing tiers.", styles['TableCellMuted'])
        ]
    ]
    p23.append(make_table(["KPI Dimension", "Baseline Benchmark (Single Model)", "Target Benchmark (DevForge AI Heterogeneous)", "Rigorous Measurement Protocol"], kpi_rows[1:], [110, 110, 134, 150], styles, "#0F172A"))
    pages.append(p23)

    # PAGE 24: SECTION 22 - HARDWARE PROFILE & RESOURCE SIZING
    p24 = []
    p24.append(Paragraph("Section 22: Hardware Profile & Resource Sizing", styles['SecH1']))
    p24.append(Paragraph("22.1 Hardware Tiers & Quantization Strategies", styles['SecH2']))
    p24.append(Paragraph(
        "A foundational design requirement of DevForge AI is accessibility across diverse developer workstations without requiring "
        "datacenter-grade infrastructure. The system automatically adapts model configurations based on detected hardware profile:",
        styles['Body']
    ))

    hw_rows = [
        [
            Paragraph("Hardware Tier", styles['TableHead']),
            Paragraph("GPU & Memory Profile", styles['TableHead']),
            Paragraph("Configured Model Stack", styles['TableHead']),
            Paragraph("Execution Strategy & Concurrency", styles['TableHead'])
        ],
        [
            Paragraph("<b>Tier 1: Entry Developer<br/>(Consumer Laptop)</b>", styles['TableCellBold']),
            Paragraph("4GB VRAM (GTX 1650 / RTX 3050)<br/>16GB – 24GB System RAM", styles['TableCell']),
            Paragraph("• Planner: qwen2.5-coder:7b (Q4_K_M)<br/>• Coder: qwen2.5-coder:7b (Q4_K_M)<br/>• Tester: codegemma:2b<br/>• Debugger: qwen2.5-coder:7b", styles['TableCell']),
            Paragraph("Sequential model execution; models swapped via Ollama with <code>keep_alive: 5m</code>; AST context pruning strictly enforced.", styles['TableCellMuted'])
        ],
        [
            Paragraph("<b>Tier 2: Mid-Range Workstation</b>", styles['TableCellBold']),
            Paragraph("8GB – 12GB VRAM (RTX 3060/4070)<br/>32GB System RAM", styles['TableCell']),
            Paragraph("• Planner: deepseek-coder-v2:16b (Q4)<br/>• Coder: codestral:22b (Q4_K_M)<br/>• Tester: codegemma:7b<br/>• Debugger: devstral:24b (Q4)", styles['TableCell']),
            Paragraph("Partial offload; 2 concurrent models in RAM cache; sub-second prompt evaluation; full vector similarity search enabled.", styles['TableCellMuted'])
        ],
        [
            Paragraph("<b>Tier 3: Enterprise On-Prem Node</b>", styles['TableCellBold']),
            Paragraph("24GB+ VRAM (RTX 4090 / A6000 / Mac Studio 64GB)<br/>64GB+ System RAM", styles['TableCell']),
            Paragraph("• Planner: deepseek-coder-v2:16b (FP16)<br/>• Coder: codestral:22b (Q8/FP16)<br/>• Tester: codegemma:7b (FP16)<br/>• Debugger: devstral:24b (Q8)", styles['TableCell']),
            Paragraph("All models permanently resident in VRAM; zero model loading latency; parallel test execution and code generation.", styles['TableCellMuted'])
        ]
    ]
    p24.append(make_table(["Hardware Tier", "GPU & Memory Profile", "Configured Model Stack", "Execution Strategy & Concurrency"], hw_rows[1:], [95, 115, 150, 144], styles, "#1E3A8A"))
    pages.append(p24)

    return pages
