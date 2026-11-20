from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib import colors
from .common import USABLE_W, make_callout, make_table

def build_part6_pages(styles):
    pages = []
    
    # PAGE 16: SECTION 14 - FUNCTIONAL REQUIREMENTS (P0 CORE)
    p16 = []
    p16.append(Paragraph("Section 14: Functional Requirements Triage (P0 Core MVP)", styles['SecH1']))
    p16.append(Paragraph("14.1 Mandatory Engineering Requirements", styles['SecH2']))
    p16.append(Paragraph(
        "Requirements are classified using strict engineering triage. **P0 requirements** are non-negotiable capabilities "
        "required for the core demonstrable MVP:",
        styles['Body']
    ))
    
    p0_rows = [
        [
            Paragraph("<b>FR-P0-01</b>", styles['TableCellBold']),
            Paragraph("Supervisor Orchestration Engine", styles['TableCellBold']),
            Paragraph("Supervisor coordinates Planner, Coder, Tester, and Debugger across background worker thread with non-blocking UI.", styles['TableCell']),
            Paragraph("AC-1.1: Background thread execution without GUI freezing.<br/>AC-1.2: Orderly transitions through Planner -&gt; Coder -&gt; Tester -&gt; Debugger.", styles['TableCell'])
        ],
        [
            Paragraph("<b>FR-P0-02</b>", styles['TableCellBold']),
            Paragraph("Local Ollama Client Integration", styles['TableCellBold']),
            Paragraph("Asynchronous HTTP client communicating with Ollama REST API (`http://127.0.0.1:11434`), supporting chat streaming.", styles['TableCell']),
            Paragraph("AC-2.1: Graceful timeout handling on server disconnect.<br/>AC-2.2: Emits tokens via EventBus with &lt;50ms stream latency.", styles['TableCell'])
        ],
        [
            Paragraph("<b>FR-P0-03</b>", styles['TableCellBold']),
            Paragraph("Structural AST Parser Integration", styles['TableCellBold']),
            Paragraph("CodeASTAnalyzer parses all workspace Python files into structured representations (classes, methods, arguments, imports).", styles['TableCell']),
            Paragraph("AC-3.1: Extracts symbols across all valid .py files in &lt;100ms.<br/>AC-3.2: Feeds structural summary directly into prompt context.", styles['TableCell'])
        ],
        [
            Paragraph("<b>FR-P0-04</b>", styles['TableCellBold']),
            Paragraph("Local Sandboxed Execution Runner", styles['TableCellBold']),
            Paragraph("CodeRunner executes test suites locally across Python (unittest), C (MinGW GCC), and JavaScript (Node.js).", styles['TableCell']),
            Paragraph("AC-4.1: Executes test suites within isolated workspace dir.<br/>AC-4.2: Accurately captures return codes, stdout, and stderr.", styles['TableCell'])
        ],
        [
            Paragraph("<b>FR-P0-05</b>", styles['TableCellBold']),
            Paragraph("Closed-Loop Self-Healing Engine", styles['TableCellBold']),
            Paragraph("Captures stderr on test failure and triggers Debugger agent for automatic in-place code repair.", styles['TableCell']),
            Paragraph("AC-5.1: Automatically triggers Debugger on non-zero exit code.<br/>AC-5.2: Re-tests fixed code up to max 3 iterations.", styles['TableCell'])
        ],
        [
            Paragraph("<b>FR-P0-06</b>", styles['TableCellBold']),
            Paragraph("Native PySide6 Desktop GUI", styles['TableCellBold']),
            Paragraph("Modern dark navy desktop interface with resizable QSplitters, live OS file tree explorer, code viewer, and terminal.", styles['TableCell']),
            Paragraph("AC-6.1: Smooth 60 FPS panel resizing via QSplitter.<br/>AC-6.2: Real-time file tree refresh on OS file writes.", styles['TableCell'])
        ]
    ]
    p16.append(make_table(["Req. ID", "Feature Name", "Technical Specification", "Testable Acceptance Criteria"], p0_rows, [55, 110, 165, 174], styles, "#1E3A8A"))
    pages.append(p16)

    # PAGE 17: SECTION 15 - FUNCTIONAL REQUIREMENTS (P1 & P2 ROADMAP)
    p17 = []
    p17.append(Paragraph("Section 15: Functional Requirements (P1 & P2 Roadmap)", styles['SecH1']))
    p17.append(Paragraph("15.1 Targeted Enhancements (P1) & Enterprise Roadmap (P2)", styles['SecH2']))
    p17.append(Paragraph(
        "P1 requirements represent high-value enhancements that elevate platform depth without external commercial dependencies. "
        "P2 requirements define future enterprise capabilities:",
        styles['Body']
    ))
    
    p1_p2_rows = [
        [
            Paragraph("<b>FR-P1-01</b>", styles['TableCellBold']),
            Paragraph("Dynamic Model Selector GUI", styles['TableCellBold']),
            Paragraph("GUI dropdowns allowing developers to assign distinct Ollama models per sub-agent at runtime.", styles['TableCell']),
            Paragraph("AC-7.1: UI queries installed models via Ollama API.<br/>AC-7.2: Selected models persist to settings.py immediately.", styles['TableCell']),
            Paragraph("P1", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>FR-P1-02</b>", styles['TableCellBold']),
            Paragraph("Vector Semantic Code Retrieval", styles['TableCellBold']),
            Paragraph("Chunks code along function/class boundaries and indexes via local embeddings (nomic-embed-text).", styles['TableCell']),
            Paragraph("AC-8.1: Chunks code by logical boundaries.<br/>AC-8.2: Cosine retrieval latency &lt;250ms for 50-file repo.", styles['TableCell']),
            Paragraph("P1", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>FR-P1-03</b>", styles['TableCellBold']),
            Paragraph("Side-by-Side Diff Inspector", styles['TableCellBold']),
            Paragraph("Visual unified diff view highlighting additions and deletions proposed by Coder or Debugger.", styles['TableCell']),
            Paragraph("AC-9.1: Renders colored unified diff.<br/>AC-9.2: Allows developer one-click accept/reject per file.", styles['TableCell']),
            Paragraph("P1", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>FR-P1-04</b>", styles['TableCellBold']),
            Paragraph("Multi-File Syntax Validator", styles['TableCellBold']),
            Paragraph("Pre-write AST validation ensuring generated code does not contain syntax errors before writing to disk.", styles['TableCell']),
            Paragraph("AC-10.1: Blocks malformed code blocks.<br/>AC-10.2: Prevents corrupting working workspace files.", styles['TableCell']),
            Paragraph("P1", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>FR-P2-01</b>", styles['TableCellBold']),
            Paragraph("Git Worktree Branch Isolation", styles['TableCellBold']),
            Paragraph("Creates temporary Git worktree branches for each agent task to enable instant rollback on failures.", styles['TableCell']),
            Paragraph("AC-11.1: Auto-commits on green test run.<br/>AC-11.2: Rollback to clean HEAD if max retries exceeded.", styles['TableCell']),
            Paragraph("P2", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>FR-P2-02</b>", styles['TableCellBold']),
            Paragraph("Multi-Node GPU Load Balancer", styles['TableCellBold']),
            Paragraph("Distributes inference requests across multiple networked Ollama GPU server nodes.", styles['TableCell']),
            Paragraph("AC-12.1: Parallel execution of code generation and unit testing across separate GPU nodes.", styles['TableCell']),
            Paragraph("P2", styles['TableCellBold'])
        ]
    ]
    p17.append(make_table(["Req. ID", "Feature Name", "Technical Specification", "Testable Acceptance Criteria", "Tier"], p1_p2_rows, [55, 100, 160, 159, 30], styles, "#0F172A"))
    pages.append(p17)

    # PAGE 18: SECTION 16 - NON-FUNCTIONAL REQUIREMENTS (NFRS)
    p18 = []
    p18.append(Paragraph("Section 16: Non-Functional Requirements (NFRs)", styles['SecH1']))
    p18.append(Paragraph("16.1 System Quality Attributes & Operating Constraints", styles['SecH2']))
    p18.append(Paragraph(
        "To ensure corporate-grade stability, security, and responsiveness, DevForge AI enforces the following non-functional constraints:",
        styles['Body']
    ))

    nfr_data = [
        [
            Paragraph("Category", styles['TableHead']),
            Paragraph("NFR ID & Name", styles['TableHead']),
            Paragraph("Target Specification & Performance Threshold", styles['TableHead']),
            Paragraph("Verification Methodology", styles['TableHead'])
        ],
        [
            Paragraph("<b>Performance</b>", styles['TableCellBold']),
            Paragraph("NFR-PERF-01: UI Responsiveness", styles['TableCellBold']),
            Paragraph("The desktop UI must maintain 60 FPS rendering without layout stutter or freeze during active model streaming.", styles['TableCell']),
            Paragraph("Qt profiling and frame rate counter during continuous 50-token/s streaming.", styles['TableCellMuted'])
        ],
        [
            Paragraph("<b>Storage Safety</b>", styles['TableCellBold']),
            Paragraph("NFR-PERF-02: Disk Preservation", styles['TableCellBold']),
            Paragraph("Heavy Ollama model weights must be stored strictly on secondary high-capacity drives (e.g. `E:/OllamaModels`).", styles['TableCell']),
            Paragraph("Automated installer check verifying `OLLAMA_MODELS` environment variable pointing to non-system partition.", styles['TableCellMuted'])
        ],
        [
            Paragraph("<b>Security & Privacy</b>", styles['TableCellBold']),
            Paragraph("NFR-SEC-01: 100% Air-Gapped", styles['TableCellBold']),
            Paragraph("Zero outbound network telemetry. Zero source code, prompts, or traces may be sent outside localhost (`127.0.0.1`).", styles['TableCell']),
            Paragraph("Wireshark network packet inspection verifying 0 outbound non-local packets during full pipeline execution.", styles['TableCellMuted'])
        ],
        [
            Paragraph("<b>Process Safety</b>", styles['TableCellBold']),
            Paragraph("NFR-SAFE-01: Sandboxed Execution", styles['TableCellBold']),
            Paragraph("Subprocess code execution is constrained to `workspace_dir` with a strict 15-second execution timeout.", styles['TableCell']),
            Paragraph("Automated test invoking infinite while loop (`while True: pass`); verifies graceful kill at 15.0s.", styles['TableCellMuted'])
        ],
        [
            Paragraph("<b>Reliability</b>", styles['TableCellBold']),
            Paragraph("NFR-REL-01: Fault Recovery", styles['TableCellBold']),
            Paragraph("If the local Ollama daemon crashes or becomes unresponsive, the platform must catch the socket error gracefully.", styles['TableCell']),
            Paragraph("Unit tests with killed Ollama process; verifies descriptive GUI alert without fatal application crash.", styles['TableCellMuted'])
        ]
    ]
    p18.append(make_table(["Category", "NFR ID & Name", "Target Specification & Performance Threshold", "Verification Methodology"], nfr_data[1:], [75, 115, 184, 130], styles, "#1E3A8A"))
    pages.append(p18)

    return pages
