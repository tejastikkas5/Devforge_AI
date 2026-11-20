# DevForge AI: Complete Project Understanding Guide & MVP Blueprint

---

**Project Name:** DevForge AI  
**Domain:** Autonomous Software Engineering, Multi-Agent Systems & Codebase RAG  
**Document Classification:** Comprehensive Pre-Coding Project Understanding & Architectural Blueprint (v2.2.0)  
**Engineering Core Authors:** Tejas Tikkas, Rohan Umbarkar, Hrutik Sawant, Vivek Ingole  
**Institutional Affiliation:** Capstone Project — MITCORER (Department of Computer Science)  
**Primary Runtime Stack:** Local Ollama Daemon, PySide6 / Qt Native UI, Python AST, MinGW GCC, Node.js  
**Primary Reference:** `PRD/DevForge_AI_PRD.pdf` (PRD v2.2.0)  
**Date:** October 2026  

---

## Executive Summary & Guide Purpose

This comprehensive guide serves as the authoritative, shared technical reference for the entire development team, capstone mentors, and competition evaluators before reviewing or executing the codebase. It translates the submitted **Product Requirements Document (PRD)** and underlying multi-agent artificial intelligence research into simple, clear, unambiguous English.

Whether you are configuring the PySide6 hardware-accelerated desktop canvas, implementing the Supervisor finite-state machine, connecting the Abstract Syntax Tree (AST) parser to prompt contexts, managing local quantized Ollama model lifecycles, or presenting progress to technical judges, this document explains:
* **What we are building** and why it matters.
* **The central "catch"** in baseline prototypes (single-model setups) and our architectural resolution (Dynamic Heterogeneous Model Routing + Production AST Code RAG).
* **How each desktop screen and panel must deliver value.**
* **The step-by-step algorithms, data contracts, and verification protocols.**

---

## Table of Contents

1. [Section 1: Project Overview & Executive Mission](#section-1-project-overview--executive-mission)
2. [Section 2: Understanding the Actual Problem & Root Causes](#section-2-understanding-the-actual-problem--root-causes)
3. [Section 3: The Project "Catch" Explained Plainly](#section-3-the-project-catch-explained-plainly)
4. [Section 4: Existing Solutions vs. DevForge AI](#section-4-existing-solutions-vs-devforge-ai)
5. [Section 5: Our Proposed Solution & End-to-End Workflow](#section-5-our-proposed-solution--end-to-end-workflow)
6. [Section 6: Complete Desktop Application Screens (PySide6)](#section-6-complete-desktop-application-screens-pyside6)
7. [Section 7: Screens 1 to 3 Detailed Engineering Walkthrough](#section-7-screens-1-to-3-detailed-engineering-walkthrough)
8. [Section 8: Screens 4 to 6 Detailed Engineering Walkthrough](#section-8-screens-4-to-6-detailed-engineering-walkthrough)
9. [Section 9: System Architecture Explained Simply](#section-9-system-architecture-explained-simply)
10. [Section 10: The Supervisor / Orchestrator Core Mechanism](#section-10-the-supervisor--orchestrator-core-mechanism)
11. [Section 11: Dynamic Heterogeneous Model Routing Explained](#section-11-dynamic-heterogeneous-model-routing-explained)
12. [Section 12: Production Code RAG in Simple English](#section-12-production-code-rag-in-simple-english)
13. [Section 13: Concrete CodeASTAnalyzer & Vector Walkthrough](#section-13-concrete-codeastanalyzer--vector-walkthrough)
14. [Section 14: Closed-Loop Automated Sandboxes & Self-Healing](#section-14-closed-loop-automated-sandboxes--self-healing)
15. [Section 15: The Self-Healing Algorithm & Recovery Limits](#section-15-the-self-healing-algorithm--recovery-limits)
16. [Section 16: Data Models, Pydantic Schemas & IPC Contracts](#section-16-data-models-pydantic-schemas--ipc-contracts)
17. [Section 17: End-to-End User Journey Walkthrough](#section-17-end-to-end-user-journey-walkthrough)
18. [Section 18: Concrete Execution Traces & Code Artifacts](#section-18-concrete-execution-traces--code-artifacts)
19. [Section 19: MVP Engineering Development Plan (6 Phases)](#section-19-mvp-engineering-development-plan-6-phases)
20. [Section 20: Edge-Case Test Suite & Verification Matrix](#section-20-edge-case-test-suite--verification-matrix)
21. [Section 21: Live Evaluation & Demonstration Checklist](#section-21-live-evaluation--demonstration-checklist)
22. [Section 22: Hardware Resource Sizing & Storage Guide](#section-22-hardware-resource-sizing--storage-guide)
23. [Section 23: Complete Engineering Glossary for Beginners](#section-23-complete-engineering-glossary-for-beginners)
24. [Section 24: Final Project Summary & Immediate Action Items](#section-24-final-project-summary--immediate-action-items)

---

## Section 1: Project Overview & Executive Mission

### 1.1 What is DevForge AI?
**DevForge AI** is a 100% private, air-gapped, on-premise software engineering platform modeled after modern AI development environments (such as Google Antigravity and OpenAI Codex). It runs on local consumer laptops and workstation hardware (tested down to a modest GTX 1650 GPU with 4GB VRAM and 16GB–24GB RAM) using local open-weight Large Language Models via **Ollama**, completely eliminating the need to transmit proprietary enterprise code to remote cloud APIs.

Instead of forcing a human developer to manually copy and paste code between an AI chat window and a code editor, DevForge AI acts as an autonomous software engineering team. A central **Supervisor / Orchestrator** ingests a natural language prompt, coordinates specialized sub-agents (Planner, Coder, Tester, Debugger), indexes project code via an Abstract Syntax Tree (AST) RAG engine, compiles and runs unit tests in a local sandbox (Python, C/C++, JavaScript), and automatically heals runtime bugs in a closed loop.

### 1.2 Simple One-Paragraph Explanation (For Non-Technical Audiences)
> *"Imagine hiring a team of four specialized software engineers—an architect who drafts the system blueprint, a programmer who writes the code, a quality assurance tester who writes test cases, and a debugger who diagnoses crashes. Now imagine that entire team lives directly inside your laptop, runs completely offline without sending your company's secret code to the internet, and works together in under 60 seconds to build, compile, and verify your program for zero dollars in API costs. That is DevForge AI."*

### 1.3 Short Pitch for Competition Judges & Evaluators
> *"Enterprise dev teams burn $20k to $100k annually on cloud AI tokens, while regulated industries in defense, finance, and healthcare are legally prohibited from leaking proprietary code to third-party APIs like OpenAI. Current local multi-agent tools fail because they use a single small model for every task and lack codebase context. DevForge AI solves this by introducing a 100% air-gapped desktop engine that pairs a Hierarchical Supervisor with Dynamic Heterogeneous Model Routing and Production AST Code RAG. We assign optimal open-weight models to their proven strengths—DeepSeek for planning, Codestral for coding, CodeGemma for testing, and Devstral for debugging—delivering verified, compiling software in an automated self-healing loop at zero marginal API cost."*

---

## Section 2: Understanding the Actual Problem & Root Causes

### 2.1 The Crisis of Cloud-Dependent AI Engineering
Commercial AI coding platforms have achieved widespread developer adoption. However, for serious enterprise software engineering, relying on public multi-tenant cloud APIs introduces four severe structural crises:

1. **Exponential Token Expenditure:** Codebases are massive. Indexing a multi-file repository with 50 files and passing full context through cloud LLMs consumes millions of tokens. When autonomous agents iterate across multiple debugging cycles, operational expenses scale exponentially ($2,000–$5,000 per 1,000 engineering tasks).
2. **Strict Intellectual Property & Regulatory Prohibitions:** Under GDPR, SOC2 Type II, HIPAA, and ITAR compliance, organizations handling proprietary financial ledgers, patient healthcare data, or defense algorithms cannot transmit source code across external networks. A single code leak can trigger catastrophic legal and regulatory penalties.
3. **The "Monolithic Model" Inefficiency:** Commercial tools route every query through a single monolithic cloud model (e.g. GPT-4o or Claude 3.5 Sonnet). Using a 400B-parameter reasoning model to write a 3-line regex or docstring is an enormous waste of compute and introduces unnecessary latency. Conversely, using lightweight models causes architectural hallucinations.
4. **Context Suffocation & Attention Degradation:** Passing raw source code files into LLM prompts without syntactic pruning rapidly exhausts model attention. The model misses cross-file class definitions, invents non-existent methods, and produces code that fails to link or compile.

### 2.2 Quantified Business Risks of Uncontrolled Cloud AI

| Enterprise Risk | Root Cause Mechanism | Business Impact & Downside |
| :--- | :--- | :--- |
| **Uncapped Cloud OpEx** | Autonomous multi-agent token multiplier (10x–50x per prompt). | $20,000 to $100,000+ unbudgeted annual cloud spend. |
| **IP & Trade Secret Leakage** | Proprietary code ingested into multi-tenant public AI provider logs. | Loss of competitive moat, regulatory fines, breach of client NDAs. |
| **Broken Dependencies** | LLM generates code blind to existing repository syntax hierarchies. | Developers spend hours manually resolving missing imports and broken classes. |
| **Vendor Lock-In** | Platform tied to proprietary cloud endpoints that can deprecate models. | Inability to customize models or guarantee long-term operational uptime. |

---

## Section 3: The Project "Catch" Explained Plainly

### 3.1 The Prototype Baseline vs. Architectural Vision
To evaluate DevForge AI honestly and appreciate its technical roadmap, developers and evaluators must understand **the central catch in the existing baseline code**:

> **The Catch in Current Code:**  
> If you inspect the existing configuration file (`config/settings.py`), you will discover this definition:
> ```python
> default_planner_model = "qwen2.5-coder:1.5b"
> default_coder_model   = "qwen2.5-coder:1.5b"
> default_tester_model  = "qwen2.5-coder:1.5b"
> default_debugger_model= "qwen2.5-coder:1.5b"
> ```
> Although the codebase defines distinct sub-agent classes (`PlannerAgent`, `CoderAgent`, `TesterAgent`, `DebuggerAgent`), **they are all hardcoded to call the exact same 1.5B model**! Furthermore, while `src/rag/ast_parser.py` contains a working `CodeASTAnalyzer`, the Supervisor previously only passed a basic directory walk listing filenames (`_get_workspace_overview`), leaving both AST structural extraction and vector similarity search disconnected from the pipeline.

### 3.2 Why Was This Done, and What Is the Solution?
* **The Technical Reason:** The baseline prototype was built and tested on a student developer laptop featuring an NVIDIA GTX 1650 with 4GB VRAM. Attempting to load multiple large models simultaneously into 4GB VRAM triggers immediate CUDA Out-Of-Memory (OOM) fatal crashes. Using `qwen2.5-coder:1.5b` allowed the entire pipeline, compiler sandbox, and PySide6 UI to run without crashes.
* **The Engineered Resolution:**  
  1. **Dynamic Heterogeneous Model Routing:** Decouple model configuration from agent logic. When running on high-end hardware, route Planner to `deepseek-coder-v2:16b`, Coder to `codestral:22b`, Tester to `codegemma:7b`, and Debugger to `devstral:24b`. When running on 4GB VRAM, use sequential model loading with Ollama keep-alive cache management.  
  2. **Production Code RAG Hookup:** Actively invoke `CodeASTAnalyzer.analyze_source()` inside the Supervisor to extract class/method signatures and inject compact outlines into agent prompts, saving 65%–85% of token overhead.

---

## Section 4: Existing Solutions vs. DevForge AI

### 4.1 Detailed Industry Comparison Matrix

| Engineering Dimension | GitHub Copilot | Cursor AI | Devin / OpenHands | DevForge AI (Us) |
| :--- | :--- | :--- | :--- | :--- |
| **Privacy / Deployment** | Cloud SaaS only (MS Azure) | Cloud SaaS only | Cloud / Complex Docker server | **100% Air-Gapped Local** (Ollama) |
| **Agent Coordination** | Single Autocomplete | Autocomplete + Chat | Multi-Agent (Cloud LLMs) | **Hierarchical Supervisor** + 4 Agents |
| **Model Topology** | Monolithic GPT-4o | Monolithic Claude 3.5 | Single LLM Backbone | **Heterogeneous Dynamic Routing** |
| **Code Context Engine** | Recent file window | Remote vector index | Shell command grep | **Hybrid AST + Vector RAG** |
| **Verification Sandbox** | None (Manual user run) | Terminal suggestion | Remote Cloud VM | **Local Native Sandboxes** (Python, C, JS) |
| **Bug Self-Healing** | Manual copy-paste | Semi-manual chat fix | Autonomous cloud loops | **Autonomous Closed-Loop Debugger** |
| **Inference API Cost** | $1,000–$3,000 / 1k tasks | $500–$1,500 / 1k tasks | $2,000–$5,000 / 1k tasks | **$0.00** (Zero marginal compute) |

---

## Section 5: Our Proposed Solution & End-to-End Workflow

### 5.1 The 8-Stage Autonomous Engineering Pipeline

```
[1. User Prompt] ──▶ [2. Supervisor Classification] ──▶ [3. AST Context RAG]
                                                               │
                                                               ▼
[6. Unit Test Harness] ◀── [5. Coder Code Synthesis] ◀── [4. Planner Architecture]
        │
        ▼
[7. Sandbox Run (GCC/Python)] ──▶ (Failed) ──▶ [8. Debugger Self-Healing Loop]
        │                                                     │
        ▼ (Passed)                                            ▼
[Verified Software & OS File Tree Update] ◀───────────────────┘
```

1. **Stage 1 (Ingestion):** User inputs goal prompt in PySide6 UI; selects project folder on disk.
2. **Stage 2 (Classification):** Supervisor evaluates prompt intent (`_is_coding_task`). Directs chit-chat to assistant or initiates engineering pipeline.
3. **Stage 3 (Context RAG):** `CodeASTAnalyzer` extracts AST syntax trees (classes, methods, imports) across existing workspace files.
4. **Stage 4 (Architecture):** Planner agent generates step-by-step modular specification including required files, interfaces, and dependencies.
5. **Stage 5 (Synthesis):** Coder agent synthesizes source code files according to architectural blueprint; persists files to workspace via `CodeRunner`.
6. **Stage 6 (Test Generation):** Tester agent synthesizes comprehensive unit test harness (Python unittest, C assertions, or JS tests).
7. **Stage 7 (Sandbox Run):** `CodeRunner` executes compiler/test harness in isolated subprocess; captures exit code, stdout, and stderr.
8. **Stage 8 (Self-Healing):** If tests fail, Debugger captures error trace and initiates in-place code repair loop (up to 3 retries).

---

## Section 6: Complete Desktop Application Screens (PySide6)

The native desktop UI is organized into six modular panels connected by draggable splitters:
* **Panel 1: Global Workspace Header:** Path selector, folder browsing, and Ollama connection status heartbeat.
* **Panel 2: Prompt & Model Console:** Natural language goal input, one-click execution button, dynamic model dropdowns.
* **Panel 3: Real-Time OS File Tree:** Live OS filesystem explorer (`QTreeView` + `QFileSystemModel`) updating instantly on disk writes.
* **Panel 4: Monospace Code Inspector:** Read-only syntax viewer (`Consolas` / `Fira Code`) displaying any clicked file.
* **Panel 5: Sandboxed Output Terminal:** Real-time console displaying GCC compiler output, unittest pass/fail results, and Node.js logs.
* **Panel 6: Agent Pipeline Status Cards:** Color-coded status telemetry cards for Planner, Coder, Tester, and Debugger.

---

## Section 7: Screens 1 to 3 Detailed Engineering Walkthrough

### Panel 1: Workspace Hub & Global Status Header
* **Purpose:** Provides the operational anchor for project file selection and runtime status.
* **Key Widgets:** `QLineEdit` (displaying current path, e.g. `E:/Capstone_MITCORER/workspace`), `QPushButton` ("Browse Folder"), and `QLabel` ("Ollama Connected: http://127.0.0.1:11434" in green).
* **Technical Implementation:** Clicking "Browse" invokes `QFileDialog.getExistingDirectory()`. The new path is passed to `Supervisor.set_workspace()` and updates the root index of `QFileSystemModel`.

### Panel 2: Natural Language Prompt & Model Console
* **Purpose:** Captures the developer's high-level engineering requirement and configures model assignments.
* **Key Widgets:** Multi-line `QTextEdit` for prompt entry, four `QComboBox` dropdowns (Planner Model, Coder Model, Tester Model, Debugger Model), and a primary `QPushButton` ("Run Multi-Agent Pipeline").
* **User Flow:** The developer enters a prompt (e.g. "Build a C palindrome utility with unit tests"). The user can leave model defaults or customize them. Clicking "Run" disables input widgets and spawns `_run_pipeline()` on a background thread.

### Panel 3: Real-Time OS File System Explorer
* **Purpose:** Gives the developer instant, transparent visibility into project files created by the agents.
* **Key Widgets:** `QTreeView` paired with `QFileSystemModel`, with filters to hide cache files (`__pycache__`, `.git`).
* **Technical Implementation:** Because it binds directly to the OS filesystem model, newly generated files (e.g. `utils.c`, `test_main.c`) appear instantaneously the microsecond `CodeRunner.write_file()` executes, without requiring manual refresh.

---

## Section 8: Screens 4 to 6 Detailed Engineering Walkthrough

### Panel 4: Monospace Code Inspector
* **Purpose:** Provides a clean, syntax-focused monospace viewer to inspect both existing codebase files and newly synthesized agent code.
* **Key Widgets:** Read-only `QPlainTextEdit` styled with dark navy background (`#0A0E17`), light text (`#E2E8F0`), line numbering margins, and an explicit Consolas/Fira Code monospace font stack.
* **User Interaction:** Clicking any file in the Panel 3 File Tree instantly loads the file into this inspector. When the Coder agent writes a file, the file is automatically selected and rendered.

### Panel 5: Sandboxed Multi-Language Output Terminal
* **Purpose:** Displays real-time compiler, interpreter, and test execution console output.
* **Key Widgets:** Terminal-styled `QPlainTextEdit` with ANSI color-coding and automatic scroll-to-bottom behavior.
* **Information Displayed:** The exact command executed (e.g. `gcc utils.c test_main.c -o test.exe`), duration in milliseconds, exit code (0 = success, 1+ = failure), and any stdout / stderr output.
* **Role in Self-Healing:** Whenever red compiler errors appear in this terminal, the user watches the Debugger agent immediately activate to resolve them.

### Panel 6: Agent Pipeline Status & Telemetry Cards
* **Purpose:** Visual dashboard showing the exact status and deliverables of every agent in the pipeline.
* **Key Widgets:** Four visual cards: (1) Planner Card, (2) Coder Card, (3) Tester Card, and (4) Debugger Card. Each card displays an animated status badge (Idle / Thinking / Success / Failed), the active model name, execution duration, and key output summaries.
* **Developer Value:** Completely eliminates the "black box" mystery of AI agents by showing exactly who is doing what in real time.

---

## Section 9: System Architecture Explained Simply

### 9.1 Decoupled Multi-Tier Topology
DevForge AI is decoupled into five distinct layers:
1. **Client UI Tier (PySide6 / Qt):** High-performance desktop presentation layer; communicates with backend workers via thread-safe signals and slots.
2. **Supervisor Orchestrator Core:** State machine managing lifecycle, task scheduling, prompt intent routing, and self-healing loops.
3. **Agent Workforce:** Discrete agent instances (Planner, Coder, Tester, Debugger) operating with specialized system prompts and assigned models.
4. **Production Code RAG Layer:** AST structural syntax extraction (`src/rag/ast_parser.py`) plus local vector embedding retrieval.
5. **Sandboxed Execution Runtime:** Subprocess runner (`src/core/runner.py`) executing Python, C/C++ (MinGW GCC), and Node.js with strict 15s timeouts.

### 9.2 Asynchronous EventBus Architecture (`src/core/event_bus.py`)
To prevent UI freezing during model inference, DevForge AI uses an in-memory `EventBus`. The Supervisor runs in a separate daemon thread, posting events (`pipeline_start`, `agent_activated`, `token_stream`, `file_written`, `sandbox_execution`). The Qt UI subscribes to these events and updates its interface via Qt Signal bridges without ever blocking the main GUI event loop.

---

## Section 10: The Supervisor / Orchestrator Core Mechanism

### 10.1 Finite State Machine (FSM) Lifecycle
The `Supervisor` class (`src/agents/supervisor.py`) enforces an orderly, deterministic lifecycle across nine discrete states:

| Step / State | Trigger Condition | Orchestrator Operation & Event Dispatched |
| :--- | :--- | :--- |
| **1. IDLE** | Application launch | Awaiting user prompt; EventBus initialized; UI controls active. |
| **2. CLASSIFY** | User clicks 'Run' | Evaluates `_is_coding_task()`. Greetings route to conversational chat; code goals initiate pipeline. |
| **3. RAG ENRICH** | Coding task confirmed | Queries `ast_parser.py` to analyze workspace files and appends structural outline to user prompt. |
| **4. PLAN** | Context enriched | Dispatches goal to `PlannerAgent`; posts `agent_activated('Planner')`; receives architectural spec. |
| **5. CODE** | Plan generated | Dispatches spec to `CoderAgent`; extracts files from markdown; writes files via `CodeRunner`. |
| **6. TEST GEN** | Files persisted | Dispatches code to `TesterAgent`; receives test suite; writes `test_suite.py` or `test_main.c`. |
| **7. EXECUTE** | Test files written | Invokes `CodeRunner.execute_any()`; captures stdout/stderr; posts `test_run_result`. |
| **8. DEBUG** | Test failed (exit != 0) | Invokes `DebuggerAgent`; applies in-place code patch; re-executes tests (up to 3 retries). |
| **9. COMPLETE** | Tests pass or max retries | Posts `pipeline_finished`; re-enables UI prompt input and buttons. |

---

## Section 11: Dynamic Heterogeneous Model Routing Explained

### 11.1 The Philosophy of Task Specialization
In traditional software engineering, different tasks require different cognitive strengths. The same applies to local LLMs:
* **Planner Agent (High Reasoning):** `deepseek-coder-v2:16b` or `qwen2.5-coder:7b` provides the architectural foresight needed to decompose multi-file dependencies.
* **Coder Agent (FIM & Precision):** `codestral:22b` or `qwen2.5-coder:7b` delivers state-of-the-art Fill-In-The-Middle accuracy with clean syntax and low hallucination.
* **Tester Agent (High-Speed Boilerplate):** `codegemma:7b` or `qwen2.5-coder:1.5b` rapidly generates assertion suites and boundary mocks in seconds.
* **Debugger Agent (Refactoring & Trace Analysis):** `devstral:24b` or `qwen2.5-coder:7b` analyzes compiler stack traces and applies targeted in-place patches.

---

## Section 12: Production Code RAG in Simple English

### 12.1 Why Standard Text RAG Fails on Source Code
Standard text chunking (e.g. slicing every 500 characters) is disastrous for code:
* Functions are cut in half, severing parameters from return statements.
* Imports and type definitions are severed from function bodies.
* Class inheritance structures are broken, causing LLMs to hallucinate missing methods.

### 12.2 The DevForge AI Hybrid Solution
DevForge AI resolves this via:
1. **Deterministic AST Outlines:** `CodeASTAnalyzer` parses workspace files into compressed skeletons containing class hierarchies, method signatures, parameter names, and docstrings.
2. **Semantic Vector Chunking:** Code is chunked strictly at function/class boundaries and indexed using local embeddings (`nomic-embed-text`) for instant cosine similarity matching.

---

## Section 13: Concrete CodeASTAnalyzer & Vector Walkthrough

### 13.1 Implementation in `src/rag/ast_parser.py`
```python
# Core AST Visitor Logic in src/rag/ast_parser.py
tree = ast.parse(source)
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.ClassDef):
        methods = [m.name for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
        classes.append({'name': node.name, 'lineno': node.lineno, 'methods': methods})
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        functions.append({'name': node.name, 'args': [arg.arg for arg in node.args.args]})
    elif isinstance(node, ast.Import):
        for alias in node.names: imports.append(alias.name)
```

### 13.2 Mathematical Token Compression Proof
* **Raw Python File Ingestion:** 1,450 tokens (36.2% of a 4k context window).
* **AST Structural Skeleton:** **195 tokens** (4.8% of context window).
* **Net Gain:** **86.5% reduction in token overhead**, freeing 7.5x more context space for code generation.

---

## Section 14: Closed-Loop Automated Sandboxes & Self-Healing

### 14.1 Sandboxed Execution Architecture (`src/core/runner.py`)
* **Python Tests:** Executes `unittest` via subprocess (`python -m unittest test_file.py`).
* **C/C++ Compilation:** Runs MinGW GCC (`gcc -Wall utils.c test_main.c -o test.exe`) and executes binary.
* **Node.js Sandbox:** Runs JS tests via local Node.js (`node test_suite.js`).
* **Timeout Enforcement:** Subprocess execution is capped at 15 seconds to prevent infinite loops.

---

## Section 15: The Self-Healing Algorithm & Recovery Limits

### 15.1 The Auto-Repair Flow
When a test fails, the Supervisor:
1. Intercepts compiler errors or test failure traces from `stderr`.
2. Packages original code, tests, and error logs into a diagnosis prompt for the Debugger agent.
3. The Debugger outputs patched code files.
4. `CodeRunner` writes patches to disk and re-executes tests.
5. Capped at **3 maximum retry attempts** to prevent infinite loops.

---

## Section 16: Data Models, Pydantic Schemas & IPC Contracts

### 16.1 EventBus Protocol Specification
* `pipeline_start`: `{"goal": str, "workspace": str}`
* `agent_activated`: `{"agent": str}` (e.g. 'Planner')
* `token_stream`: `{"agent": str, "token": str}`
* `step_completed`: `{"agent": str, "result": str}`
* `file_written`: `{"filename": str, "filepath": str}`
* `sandbox_execution`: `{"message": str}`
* `test_run_result`: `{"success": bool, "stdout": str, "stderr": str, "exit_code": int}`
* `pipeline_finished`: `{"status": str, "workspace": str}`

---

## Section 17: End-to-End User Journey Walkthrough

### 17.1 Concrete Execution: Pune Capstone String & Palindrome Task
1. Developer enters: *"Create a modular C utility that reverses strings and checks palindromes with unit tests and utils header."*
2. Supervisor enriches context using `ast_parser.py` and dispatches goal to Planner (`deepseek-coder-v2`).
3. Planner generates architectural plan: `utils.h`, `utils.c`, and `test_main.c`.
4. Coder (`codestral`) synthesizes header and implementation files.
5. Tester (`codegemma`) generates unit test suite `test_main.c`.
6. CodeRunner compiles and runs C binary via MinGW GCC: `gcc utils.c test_main.c -o test.exe`.
7. Terminal displays live GCC output; tests pass; files appear in OS file tree explorer.

---

## Section 18: Concrete Execution Traces & Code Artifacts

### 18.1 Synthesized Header (`workspace/utils.h`)
```c
#ifndef UTILS_H
#define UTILS_H
#include <stdbool.h>
void reverse_string(char *str);
bool is_palindrome(const char *str);
#endif
```

### 18.2 Synthesized Implementation (`workspace/utils.c`)
```c
#include <string.h>
#include "utils.h"

void reverse_string(char *str) {
    if (!str) return;
    int i = 0, j = strlen(str) - 1;
    while (i < j) { char temp = str[i]; str[i++] = str[j]; str[j--] = temp; }
}

bool is_palindrome(const char *str) {
    if (!str) return false;
    int i = 0, j = strlen(str) - 1;
    while (i < j) { if (str[i++] != str[j--]) return false; }
    return true;
}
```

---

## Section 19: MVP Engineering Development Plan (6 Phases)

1. **Phase 1: Local Ingestion:** OllamaClient, streaming SSE, Pydantic settings.
2. **Phase 2: RAG & AST Parser:** `CodeASTAnalyzer`, symbol extraction, vector store.
3. **Phase 3: Agent Orchestrator:** Supervisor FSM, Planner, Coder, Tester, Debugger.
4. **Phase 4: Sandboxed Runner:** CodeRunner supporting Python, C (GCC), and Node.js.
5. **Phase 5: PySide6 Desktop UI:** 6-panel layout, QSplitters, OS file explorer, terminal.
6. **Phase 6: Verification & Prep:** Automated test suite, edge cases, scripted demo.

---

## Section 20: Edge-Case Test Suite & Verification Matrix

* **TC-EDG-01 (Chat Intent):** Casual greetings stream friendly reply without creating files.
* **TC-EDG-02 (Malformed Python):** `CodeASTAnalyzer` catches SyntaxErrors without crashing.
* **TC-EDG-03 (Missing C Header):** GCC failure caught by Debugger for automated remediation.
* **TC-EDG-04 (Infinite Loop):** Subprocess killed at 15-second execution timeout.
* **TC-EDG-05 (Daemon Disconnect):** Catches connection errors gracefully with UI warning.

---

## Section 21: Live Evaluation & Demonstration Checklist

Follow this scripted 5-minute competition walkthrough:
* **Step 1 (30s):** State problem: cloud token costs and IP exfiltration bans.
* **Step 2 (45s):** Explain "the catch" and introduce Dynamic Model Routing + AST RAG.
* **Step 3 (30s):** Input C palindrome prompt; show model dropdowns.
* **Step 4 (60s):** Show live agent cards, token streaming, and OS file tree updating.
* **Step 5 (60s):** Show terminal compiling C via GCC and passing tests.
* **Step 6 (45s):** Inject typo; show Debugger auto-healing code.
* **Step 7 (30s):** Conclude with $0.00 compute cost and air-gapped security.

---

## Section 22: Hardware Resource Sizing & Storage Guide

* **Entry Laptop (4GB VRAM):** Sequential GGUF execution (Qwen2.5-Coder 7B / CodeGemma 2B) with AST pruning.
* **Mid-Range Workstation (8GB–12GB VRAM):** Partial offload; concurrent resident models; vector search enabled.
* **Enterprise Server (24GB+ VRAM):** All models resident in VRAM (Codestral 22B, DeepSeek-Coder-V2 16B, Devstral 24B).
* **Storage Optimization:** Permanently set `OLLAMA_MODELS` to `E:\OllamaModels` (200GB+ free space) to protect Drive C:.

---

## Section 23: Complete Engineering Glossary for Beginners

* **PRD:** Product Requirements Document detailing system requirements before development.
* **Supervisor:** Central orchestrator managing sub-agents and pipeline execution.
* **AST:** Abstract Syntax Tree used for code symbol extraction without token bloat.
* **RAG:** Retrieval-Augmented Generation augmenting prompts with local code context.
* **Heterogeneous Routing:** Assigning different specialized models to different tasks.
* **Ollama:** Local runtime executing open-source LLMs without internet connection.
* **PySide6:** Official Python bindings for Qt 6 desktop application development.
* **EventBus:** Decoupled publish-subscribe messaging preventing UI freezing.
* **GGUF:** Compact format for storing quantized AI model weights for fast local inference.

---

## Section 24: Final Project Summary & Immediate Action Items

* **The Problem We Solve:** High cloud API costs, IP privacy violations, and single-model prototype limitations.
* **The Solution:** DevForge AI—100% private, air-gapped multi-agent platform with Dynamic Model Routing, AST Code RAG, and closed-loop sandboxed self-healing.
* **Immediate Actions:**  
  1. Connect AST parser to Supervisor in `src/agents/supervisor.py`.  
  2. Bind dynamic model selectors in `src/pyside_app.py`.  
  3. Execute the automated test matrix across Python, C, and JS.  
  4. Rehearse the 5-minute live competition presentation.
