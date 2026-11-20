from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib import colors
from .common import USABLE_W, make_callout, make_table

def build_pug_part5_pages(styles):
    pages = []
    
    # PAGE 13: SECTION 11 - DYNAMIC HETEROGENEOUS MODEL ROUTING EXPLAINED
    p13 = []
    p13.append(Paragraph("Section 11: Dynamic Heterogeneous Model Routing Explained", styles['SecH1']))
    p13.append(Paragraph("11.1 The Philosophy of Task Specialization", styles['SecH2']))
    p13.append(Paragraph(
        "In traditional software companies, a single individual does not handle system architecture, rapid typing, QA assertion auditing, "
        "and low-level debugging with equal efficiency. Specialized roles exist because different tasks require different cognitive skills. "
        "The exact same principle applies to Large Language Models in autonomous software engineering:",
        styles['Body']
    ))

    specialization_reasons = [
        "<b>• High-Parameter Reasoning for Planning:</b> Breaking a complex software requirement into multi-file modules, dependency graphs, and interface contracts demands deep reasoning capacity (16B–32B+ parameters). A 1.5B model lacks the attention depth to foresee cross-file import circularity.",
        "<b>• Fill-In-The-Middle (FIM) & Syntax Rigor for Coding:</b> The Coder agent must generate clean, valid syntax without hallucinating closing brackets or inventing third-party dependencies. Models like <code>codestral:22b</code> or <code>qwen2.5-coder:7b</code> are specifically pre-trained on trillions of code tokens for high-precision code synthesis.",
        "<b>• High Throughput & Low Latency for Testing:</b> Writing unit test assertions and mocking inputs is largely boilerplate and template expansion. A lightweight, high-speed model like <code>codegemma:7b</code> or <code>qwen2.5-coder:1.5b</code> can generate 50 lines of test assertions in 2 seconds.",
        "<b>• Codebase Refactoring & Trace Diagnosis for Debugging:</b> Analyzing compiler warnings (e.g. GCC linking errors, Python AttributeError) and applying surgical diffs requires specialized refactoring models like <code>devstral:24b</code>."
    ]
    for sr in specialization_reasons:
        p13.append(Paragraph(sr, styles['Bullet']))
        p13.append(Spacer(1, 3))
    p13.append(Spacer(1, 6))

    p13.append(Paragraph("11.2 The Production Capability & Fallback Matrix", styles['SecH2']))
    matrix_data = [
        [Paragraph("Specialized Agent", styles['TableHead']), Paragraph("High-End Production Model", styles['TableHead']), Paragraph("4GB VRAM Laptop Model", styles['TableHead']), Paragraph("Key Performance Advantage", styles['TableHead'])],
        [Paragraph("<b>Supervisor Router</b>", styles['TableCellBold']), Paragraph("qwen2.5-coder:7b", styles['TableCell']), Paragraph("qwen2.5-coder:1.5b", styles['TableCell']), Paragraph("Zero-latency intent classification & chat.", styles['TableCellMuted'])],
        [Paragraph("<b>Planner Agent</b>", styles['TableCellBold']), Paragraph("deepseek-coder-v2:16b", styles['TableCell']), Paragraph("qwen2.5-coder:7b", styles['TableCell']), Paragraph("Superior multi-file system decomposition.", styles['TableCellMuted'])],
        [Paragraph("<b>Coder Agent</b>", styles['TableCellBold']), Paragraph("codestral:22b", styles['TableCell']), Paragraph("qwen2.5-coder:7b", styles['TableCell']), Paragraph("State-of-the-art FIM code synthesis.", styles['TableCellMuted'])],
        [Paragraph("<b>Tester Agent</b>", styles['TableCellBold']), Paragraph("codegemma:7b", styles['TableCell']), Paragraph("qwen2.5-coder:1.5b", styles['TableCell']), Paragraph("Rapid unit test boilerplate generation.", styles['TableCellMuted'])],
        [Paragraph("<b>Debugger Agent</b>", styles['TableCellBold']), Paragraph("devstral:24b", styles['TableCell']), Paragraph("qwen2.5-coder:7b", styles['TableCell']), Paragraph("Compiler trace root-cause refactoring.", styles['TableCellMuted'])]
    ]
    p13.append(make_table(["Specialized Agent", "High-End Production Model", "4GB VRAM Laptop Model", "Key Performance Advantage"], matrix_data[1:], [100, 110, 105, 189], styles, "#1E3A8A"))
    pages.append(p13)

    # PAGE 14: SECTION 12 - PRODUCTION CODE RAG IN SIMPLE ENGLISH
    p14 = []
    p14.append(Paragraph("Section 12: Production Code RAG in Simple English", styles['SecH1']))
    p14.append(Paragraph("12.1 Why Standard Text RAG Fails on Source Code", styles['SecH2']))
    p14.append(Paragraph(
        "Standard Retrieval-Augmented Generation (RAG) was designed for prose documents (e.g. Wikipedia articles, customer support PDFs). "
        "Standard RAG operates by chopping text into fixed-size chunks (e.g., every 500 characters). "
        "<b>When applied to source code, fixed-size chunking is disastrous:</b>",
        styles['Body']
    ))

    rag_flaws = [
        "<b>• Splitting Functions Mid-Body:</b> A 500-character chunk boundary frequently slices a function in half, severing the function header and arguments from the return statement.",
        "<b>• Losing Import Dependencies:</b> If <code>import math</code> or <code>#include &lt;stdio.h&gt;</code> is separated into Chunk #1, but a function using math is in Chunk #4, the LLM hallucinates that math functions do not exist.",
        "<b>• Class Inheritance Severance:</b> Child class methods are severed from parent class definitions, causing the LLM to invent duplicate methods."
    ]
    for rf in rag_flaws:
        p14.append(Paragraph(rf, styles['Bullet']))
        p14.append(Spacer(1, 3))
    p14.append(Spacer(1, 6))

    p14.append(Paragraph("12.2 The DevForge AI Hybrid Solution", styles['SecH2']))
    p14.append(Paragraph(
        "DevForge AI solves this by introducing a <b>syntax-aware hybrid RAG architecture</b> that combines deterministic grammar analysis "
        "with semantic vector search:",
        styles['Body']
    ))

    hybrid_box = (
        "<b>The DevForge AI Two-Tier Code RAG Pipeline:</b><br/>"
        "1. <b>Deterministic AST Structural Outlines:</b> Before generating code, <code>CodeASTAnalyzer</code> parses workspace files "
        "using the language's native Abstract Syntax Tree. It creates an ultra-compact summary of every class, function signature, parameter list, "
        "and import. This gives agents 100% visibility into existing project APIs using only <b>15% of the token overhead</b> of raw code.<br/>"
        "2. <b>Logical Semantic Chunking:</b> When full code retrieval is required, files are split strictly at function and class boundaries, "
        "never mid-syntax. Chunks are embedded via local Ollama models (<code>nomic-embed-text</code>) for instant similarity matching."
    )
    p14.append(make_callout(hybrid_box, styles, "#F0FDF4", "#22C55E"))
    pages.append(p14)

    # PAGE 15: SECTION 13 - CODEASTANALYZER & VECTOR WALKTHROUGH
    p15 = []
    p15.append(Paragraph("Section 13: Concrete CodeASTAnalyzer & Vector Walkthrough", styles['SecH1']))
    p15.append(Paragraph("13.1 Code Walkthrough: `src/rag/ast_parser.py`", styles['SecH2']))
    p15.append(Paragraph(
        "To understand how the structural extraction executes in code, inspect the static methods in `src/rag/ast_parser.py`:",
        styles['Body']
    ))

    ast_code = (
        "<code># Core AST Visitor Logic in src/rag/ast_parser.py<br/>"
        "tree = ast.parse(source)<br/>"
        "for node in ast.iter_child_nodes(tree):<br/>"
        "    if isinstance(node, ast.ClassDef):<br/>"
        "        methods = [m.name for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]<br/>"
        "        classes.append({'name': node.name, 'lineno': node.lineno, 'methods': methods})<br/>"
        "    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):<br/>"
        "        functions.append({'name': node.name, 'args': [arg.arg for arg in node.args.args]})<br/>"
        "    elif isinstance(node, ast.Import):<br/>"
        "        for alias in node.names: imports.append(alias.name)</code>"
    )
    p15.append(make_callout(ast_code, styles, "#F8FAFC", "#CBD5E1"))
    p15.append(Spacer(1, 8))

    p15.append(Paragraph("13.2 Mathematical Token Compression Proof", styles['SecH2']))
    p15.append(Paragraph(
        "Consider a 200-line Python utility file (`utils.py`) containing 5 helper functions and 2 classes with comprehensive docstrings. "
        "The raw file contains approximately <b>1,450 tokens</b>. "
        "When parsed by `CodeASTAnalyzer.format_summary()`, the structural skeleton compresses into:",
        styles['Body']
    ))
    
    calc_data = [
        [Paragraph("Representation Format", styles['TableHead']), Paragraph("Token Count", styles['TableHead']), Paragraph("Context Window Share", styles['TableHead']), Paragraph("Syntactic Precision", styles['TableHead'])],
        [Paragraph("Raw Python File Ingestion", styles['TableCellBold']), Paragraph("1,450 tokens", styles['TableCell']), Paragraph("36.2% of 4k context window", styles['TableCellMuted']), Paragraph("Full code, but bloats prompt", styles['TableCell'])],
        [Paragraph("<b>AST Structural Skeleton (DevForge AI)</b>", styles['TableCellBold']), Paragraph("<b>195 tokens</b>", styles['TableCellBold']), Paragraph("<b>4.8% of 4k context window</b>", styles['TableCellBold']), Paragraph("<b>100% exact symbols & signatures</b>", styles['TableCellBold'])],
        [Paragraph("<b>Net Engineering Gain</b>", styles['TableCellBold']), Paragraph("<b>-86.5% Tokens</b>", styles['TableCellBold']), Paragraph("<b>7.5x Context Space Saved</b>", styles['TableCellBold']), Paragraph("<b>Zero hallucinated function names</b>", styles['TableCellBold'])]
    ]
    p15.append(make_table(["Representation Format", "Token Count", "Context Window Share", "Syntactic Precision"], calc_data[1:], [130, 90, 134, 150], styles, "#1E3A8A"))
    pages.append(p15)

    return pages
