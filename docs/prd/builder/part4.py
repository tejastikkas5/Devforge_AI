from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib import colors
from .common import USABLE_W, make_callout, make_table

def build_part4_pages(styles):
    pages = []
    
    # PAGE 10: SECTION 8 - DYNAMIC HETEROGENEOUS MODEL ROUTING
    p10 = []
    p10.append(Paragraph("Section 8: Dynamic Heterogeneous Model Routing", styles['SecH1']))
    p10.append(Paragraph("8.1 The Architectural Solution to \"The Catch\"", styles['SecH2']))
    p10.append(Paragraph(
        "As established in Section 2, the primary engineering flaw in single-model multi-agent setups is the mismatch between model capabilities "
        "and task requirements. DevForge AI formally decouples the underlying model configuration from the agent logic. "
        "Each specialized agent is assigned an optimal local model tailored to its specific reasoning, syntax, or throughput demands.",
        styles['Body']
    ))
    
    routing_data = [
        [
            Paragraph("Specialized Agent", styles['TableHead']),
            Paragraph("Optimal Production Model", styles['TableHead']),
            Paragraph("Lightweight Fallback (4GB VRAM)", styles['TableHead']),
            Paragraph("Technical Rationale & Capability Justification", styles['TableHead'])
        ],
        [
            Paragraph("<b>Supervisor / Router</b>", styles['TableCellBold']),
            Paragraph("qwen2.5-coder:7b", styles['TableCell']),
            Paragraph("qwen2.5-coder:1.5b", styles['TableCell']),
            Paragraph("Sub-second latency, deterministic prompt categorization, lightweight memory footprint for background routing.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Planner Agent</b>", styles['TableCellBold']),
            Paragraph("deepseek-coder-v2:16b", styles['TableCell']),
            Paragraph("qwen2.5-coder:7b", styles['TableCell']),
            Paragraph("Superior architectural reasoning, complex multi-file decomposition, deep understanding of software design patterns.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Coder Agent</b>", styles['TableCellBold']),
            Paragraph("codestral:22b", styles['TableCell']),
            Paragraph("qwen2.5-coder:7b", styles['TableCell']),
            Paragraph("State-of-the-art Fill-In-The-Middle (FIM), multi-language syntax precision (Python, C, JS), low indentation error rate.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Tester Agent</b>", styles['TableCellBold']),
            Paragraph("codegemma:7b", styles['TableCell']),
            Paragraph("qwen2.5-coder:1.5b", styles['TableCell']),
            Paragraph("Fast assertion generation, unit test boilerplate synthesis, boundary condition and edge-case mocking.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Debugger Agent</b>", styles['TableCellBold']),
            Paragraph("devstral:24b", styles['TableCell']),
            Paragraph("qwen2.5-coder:7b", styles['TableCell']),
            Paragraph("Codebase refactoring specialist; analyzes compiler stack traces (GCC/Python) and applies in-place syntax diffs.", styles['TableCell'])
        ]
    ]
    p10.append(make_table(["Specialized Agent", "Optimal Production Model", "Lightweight Fallback (4GB VRAM)", "Technical Rationale & Capability Justification"], routing_data[1:], [95, 105, 100, 204], styles, "#1E3A8A"))
    p10.append(Spacer(1, 8))

    p10.append(Paragraph("8.2 Dynamic VRAM Sizing & Model Swap Logic", styles['SecH2']))
    p10.append(Paragraph(
        "On workstations with unified or dedicated VRAM exceeding 16GB, multiple models can remain resident simultaneously. "
        "On hardware-constrained laptops (e.g. GTX 1650 with 4GB VRAM), DevForge AI communicates with Ollama's model runner using "
        "sequential lifecycle management: each sub-agent triggers Ollama to unload previous weights and load the required quantized GGUF weights, "
        "configured with a 5-minute keep-alive parameter (<code>keep_alive: 5m</code>) to balance RAM disk caching with GPU VRAM limits.",
        styles['Body']
    ))
    pages.append(p10)

    # PAGE 11: SECTION 9 - PRODUCTION CODE RAG LAYER (AST + VECTOR)
    p11 = []
    p11.append(Paragraph("Section 9: Production Code RAG Layer (AST + Vector)", styles['SecH1']))
    p11.append(Paragraph("9.1 Two-Tier Hybrid Code Retrieval Architecture", styles['SecH2']))
    p11.append(Paragraph(
        "Feeding raw source files directly into local LLMs exhausts context windows (typically 8k to 32k tokens on local hardware) "
        "and severely increases generation latency. DevForge AI implements a **two-tier hybrid retrieval architecture**:",
        styles['Body']
    ))

    rag_steps = [
        "<b>Tier 1: Deterministic Structural AST Extraction (<code>src/rag/ast_parser.py</code>):</b><br/>"
        "Python's native <code>ast</code> module is utilized by <code>CodeASTAnalyzer</code> to parse workspace files into concise structural outlines. "
        "It extracts: (1) Class definitions and inherited bases, (2) Method and function signatures including parameter lists, "
        "(3) Docstrings describing purpose, and (4) Imported modules. This provides the agents with 100% accurate symbol tables "
        "using less than 15% of the token overhead of raw files.",
        "<b>Tier 2: Semantic Vector Code Chunking & Retrieval:</b><br/>"
        "For large multi-file repositories, code is segmented along logical function and class boundaries. Each block is embedded using "
        "a lightweight local embedding model (e.g. <code>nomic-embed-text</code> via Ollama) and indexed in an in-memory vector store. "
        "When the user inputs a prompt, the RAG engine computes cosine similarity against indexed chunks, retrieving only the top-k (k=3) "
        "most relevant functions and injecting them into the Coder and Tester context windows."
    ]
    for st in rag_steps:
        p11.append(Paragraph(st, styles['Body']))
        p11.append(Spacer(1, 4))

    ast_code_box = (
        "<b>Sample AST Structural Context Injected into Agent Context:</b><br/>"
        "<code>File: utils.py<br/>"
        "Imports: math, typing.List, typing.Dict<br/>"
        "Class: StringManipulator | Methods: reverse_string(s: str), is_palindrome(s: str)<br/>"
        "Function: calculate_hash(data: str) -&gt; str [Docs: Computes SHA256 hex digest]</code>"
    )
    p11.append(make_callout(ast_code_box, styles, "#F8FAFC", "#CBD5E1"))
    pages.append(p11)

    # PAGE 12: SECTION 10 - CLOSED-LOOP AUTOMATED EXECUTION & HEALING
    p12 = []
    p12.append(Paragraph("Section 10: Closed-Loop Automated Execution & Healing", styles['SecH1']))
    p12.append(Paragraph("10.1 Sandboxed Execution Architecture (`src/core/runner.py`)", styles['SecH2']))
    p12.append(Paragraph(
        "DevForge AI includes a dedicated local code runner (<code>CodeRunner</code>) capable of executing code across multiple target languages "
        "in an isolated subprocess sandbox. The runner captures process standard output (<code>stdout</code>), standard error (<code>stderr</code>), "
        "and return codes:",
        styles['Body']
    ))

    runner_features = [
        "<b>• Python Test Suite Execution:</b> Executes unit tests using Python's native <code>unittest</code> framework (<code>python -m unittest test_file.py</code>).",
        "<b>• Native C/C++ Compilation & Linkage:</b> Dispatches MinGW GCC compiler commands (<code>gcc utils.c test_utils.c -o test.exe</code>) followed by binary execution.",
        "<b>• JavaScript / Node.js Execution:</b> Executes JS files directly via local Node.js runtime (<code>node test_suite.js</code>).",
        "<b>• Execution Safety & Timeouts:</b> Every process is constrained by a strict timeout (default: 15 seconds) to prevent infinite loops from hanging system resources."
    ]
    for feat in runner_features:
        p12.append(Paragraph(feat, styles['Bullet']))
    p12.append(Spacer(1, 8))

    p12.append(Paragraph("10.2 Autonomous Debugging & Self-Healing Loop", styles['SecH2']))
    p12.append(Paragraph(
        "When a test execution fails (exit code != 0), the Supervisor initiates an automated healing cycle:",
        styles['Body']
    ))
    
    heal_steps = [
        "1. <b>Error Interception:</b> The Supervisor captures the exact <code>stderr</code> stack trace, compiler error, or assertion failure.",
        "2. <b>Debugger Invocation:</b> The Supervisor activates the <code>DebuggerAgent</code> (configured with <code>devstral</code> or <code>qwen2.5-coder</code>), passing the original source code, test script, and error trace.",
        "3. <b>Targeted Patch Generation:</b> The Debugger diagnoses the root cause (e.g. off-by-one error, missing import, type mismatch, syntax error) and outputs corrected code blocks.",
        "4. <b>In-Place Workspace Update:</b> The runner writes the corrected code files back into the workspace directory.",
        "5. <b>Verification Re-Test:</b> The runner re-executes the test suite. If the test passes, the pipeline terminates successfully. If it fails, the loop repeats up to a maximum of 3 attempts."
    ]
    for hs in heal_steps:
        p12.append(Paragraph(hs, styles['Bullet']))
    pages.append(p12)

    return pages
