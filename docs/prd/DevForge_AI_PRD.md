# Product Requirements Document (PRD)
# DevForge AI: Autonomous, Enterprise-Grade Multi-Agent Software Development Platform with Heterogeneous Model Routing & Production RAG

---

**Project Name:** DevForge AI  
**Domain:** Autonomous Software Engineering, Multi-Agent Systems & Codebase RAG  
**Document Status:** Comprehensive Pre-Coding & Production Engineering Blueprint (v2.2.0)  
**Authors:** Tejas Tikkas, Rohan Umbarkar, Hrutik Sawant, Vivek Ingole  
**Institutional Affiliation:** Capstone Project — MITCORER (Department of Computer Science)  
**Target Release Cycle:** Production Release v2.2.0 (Air-Gapped Workstation Edition)  
**Primary Runtime Dependencies:** Local Ollama Engine, PySide6 / Qt Native UI, AST Parser, PostGIS / Vector Index  
**Date:** October 2026  

---

## Table of Contents

1. [Section 1: Executive Summary & System Identity](#section-1-executive-summary--system-identity)
2. [Section 2: Problem Statement & Quantified Root Cause Analysis](#section-2-problem-statement--quantified-root-cause-analysis)
3. [Section 3: The Project "Catch": Baseline Prototype vs. True Multi-Model Vision](#section-3-the-project-catch-baseline-prototype-vs-true-multi-model-vision)
4. [Section 4: Comprehensive As-Is vs. To-Be Workflow](#section-4-comprehensive-as-is-vs-to-be-workflow)
5. [Section 5: Market Analysis & Competitor Differentiation Matrix](#section-5-market-analysis--competitor-differentiation-matrix)
6. [Section 6: User Personas & Target Stakeholders](#section-6-user-personas--target-stakeholders)
7. [Section 7: Complete End-to-End System Architecture](#section-7-complete-end-to-end-system-architecture)
8. [Section 8: Supervisor / Orchestrator Core Mechanism](#section-8-supervisor--orchestrator-core-mechanism)
9. [Section 9: Dynamic Heterogeneous Model Routing](#section-9-dynamic-heterogeneous-model-routing)
10. [Section 10: Production Code RAG Layer (AST + Vector Hybrid)](#section-10-production-code-rag-layer-ast--vector-hybrid)
11. [Section 11: Closed-Loop Automated Execution & Healing](#section-11-closed-loop-automated-execution--healing)
12. [Section 12: Complete Application Screen Architecture (PySide6)](#section-12-complete-application-screen-architecture-pyside6)
13. [Section 13: Screens 1 to 3 Detailed Specifications](#section-13-screens-1-to-3-detailed-specifications)
14. [Section 14: Screens 4 to 6 Detailed Specifications](#section-14-screens-4-to-6-detailed-specifications)
15. [Section 15: Functional Requirements Triage (P0 Core MVP)](#section-15-functional-requirements-triage-p0-core-mvp)
16. [Section 16: Functional Requirements (P1 & P2 Roadmap)](#section-16-functional-requirements-p1--p2-roadmap)
17. [Section 17: Non-Functional Requirements (NFRs)](#section-17-non-functional-requirements-nfrs)
18. [Section 18: Data Contracts & IPC Message Schemas](#section-18-data-contracts--ipc-message-schemas)
19. [Section 19: End-to-End User Journey Walkthrough (Pune Capstone Task)](#section-19-end-to-end-user-journey-walkthrough-pune-capstone-task)
20. [Section 20: Seven-Phase Implementation Roadmap](#section-20-seven-phase-implementation-roadmap)
21. [Section 21: Comprehensive Verification & Test Suite](#section-21-comprehensive-verification--test-suite)
22. [Section 22: Quantitative Benchmarks & KPIs](#section-22-quantitative-benchmarks--kpis)
23. [Section 23: Hardware Profile & Resource Sizing](#section-23-hardware-profile--resource-sizing)
24. [Section 24: Risks, Assumptions & Mitigation Strategies](#section-24-risks-assumptions--mitigation-strategies)
25. [Section 25: Enterprise Monetization & Budget Model](#section-25-enterprise-monetization--budget-model)
26. [Section 26: Comprehensive Engineering Glossary](#section-26-comprehensive-engineering-glossary)
27. [Section 27: Academic Citations & References](#section-27-academic-citations--references)
28. [Section 28: Final Executive Project Synthesis](#section-28-final-executive-project-synthesis)

---

## Section 1: Executive Summary & System Identity

### 1.1 Product Vision & High-Level Purpose
Software engineering is undergoing a generational inflection point driven by Large Language Models (LLMs). However, current industry leaders—such as GitHub Copilot, Cursor AI, Devin by Cognition, and OpenHands—are built almost exclusively as cloud-dependent SaaS solutions. They mandate shipping proprietary source code, internal schemas, and intellectual property to third-party remote API endpoints (e.g., OpenAI, Anthropic, or proprietary cloud servers).

For enterprises operating in high-security, highly-regulated verticals (banking, fintech, defense aerospace, healthcare, and critical infrastructure), this architectural paradigm is an absolute non-starter. Stringent regulatory mandates (SOC2 Type II, GDPR, HIPAA, ITAR, and enterprise NDA agreements) strictly forbid code leakage beyond enterprise corporate perimeters. Furthermore, token-based cloud pricing escalates uncontrollably when autonomous multi-agent systems iteratively index full repositories and execute multiple rounds of self-debugging.

**DevForge AI** is engineered to eliminate this compromise. It is an **autonomous, 100% private, on-premise software engineering platform** modeled after modern AI IDEs (such as Antigravity and Codex), designed to execute locally on consumer laptop and workstation hardware via **Ollama** without relying on external cloud APIs.

### 1.2 Core Architectural Innovations
1. **Hierarchical Supervisor/Orchestrator:** A centralized orchestrator coordinates specialized agents (Planner, Coder, Tester, Debugger) across a structured state machine with non-blocking async execution.
2. **Dynamic Heterogeneous Model Routing:** Rather than forcing one model to do everything, the orchestrator routes specific tasks to specialized open-weight models (Qwen2.5-Coder for system planning, Codestral for synthesis, CodeGemma for unit tests, Devstral for bug healing).
3. **Production Hybrid Code RAG:** Combines deterministic Abstract Syntax Tree (AST) structural parsing with local dense vector embeddings, feeding compact, relevant context windows and saving 65%–85% of token overhead.
4. **Closed-Loop Execution Sandbox:** Integrates local compilers and test runners (Python unittest, MinGW GCC C/C++, Node.js). If tests fail, the runtime automatically feeds execution traces into a self-healing debugging loop.
5. **Hardware-Accelerated Local UI:** Native PySide6 / Qt desktop interface with draggable splitters, live OS file tree tracking, multi-tab monospace code inspectors, and real-time execution terminals.

---

## Section 2: Problem Statement & Quantified Root Cause Analysis

### 2.1 The Industry Pain: Quantified Root Causes
Modern enterprise software development organizations face severe friction when adopting commercial AI coding tools. The following matrix summarizes the fundamental breakdown in the existing commercial landscape:

| Root Cause Factor | Operational Manifestation | Empirical Business Impact |
| :--- | :--- | :--- |
| **Skyrocketing API Costs** | Full codebase indexing and autonomous agent loops generate millions of tokens. Tools like Devin cost upwards of $2,000 to $5,000 per 1,000 engineering tasks. | Enterprise dev teams burn $20k to $100k+ annually in cloud inference OpEx. |
| **Zero Data Privacy** | Proprietary source code, database credentials, internal system schemas, and algorithmic logic are sent to remote multi-tenant cloud servers. | Violates SOC2, HIPAA, GDPR, and defense air-gap compliance. High IP leakage risk. |
| **One-Size-Fits-All Inefficiency** | Monolithic models are used indiscriminately for every task: an expensive 70B/400B model is overkill for writing a simple regex, while small models hallucinate architecture. | High latency, GPU throttling, and bloated prompt overhead without task specialization. |
| **Context Suffocation** | Dumping raw multi-file code into prompt windows exceeds context bounds, causing catastrophic forgetting and hallucinations across cross-file imports. | Generated code fails to link with existing utility files or duplicates existing classes. |

---

## Section 3: The Project "Catch": Baseline Prototype vs. True Multi-Model Vision

### 3.1 The Dual Engineering Gaps in Current Codebase
During the initial development of DevForge AI, a crucial realization emerged—representing **the central catch of the project**:

1. **Single-Model Bottleneck:** While the architecture separates the pipeline into distinct agent roles (Planner, Coder, Tester, Debugger), the baseline code in `config/settings.py` hardcoded all agents to a single small model: `qwen2.5-coder:1.5b`. This was chosen initially to ensure the platform booted within the 4GB VRAM limit of a laptop GTX 1650. However, running a single lightweight model across all phases eliminates the benefits of specialized capabilities (e.g., Qwen lacks the architectural depth of DeepSeek-Coder-V2, while Codestral excels at code synthesis).
2. **Disconnected RAG Engine:** Although `src/rag/ast_parser.py` was implemented to extract AST symbol hierarchies, the Supervisor previously only passed a basic directory walk listing filenames (`_get_workspace_overview`). Neither the AST syntax analyzer nor the semantic vector database was actively hooked into the agent prompt context.

### 3.2 The Engineering Resolution
The production release of DevForge AI bridges this exact gap by introducing:
* **Dynamic Heterogeneous Model Routing:** Decoupling model assignment so each agent can be configured with its optimal model.
* **Integrated AST + Vector Hybrid RAG:** Connecting `CodeASTAnalyzer` to the Supervisor so agents receive rich, token-efficient syntax outlines of existing workspace code.

---

## Section 4: Comprehensive As-Is vs. To-Be Workflow

### 4.1 The Legacy Paradigm vs. The DevForge AI Autonomous Loop

| Dimension | Legacy Cloud / Manual Process (As-Is) | DevForge AI Local Orchestration (To-Be) |
| :--- | :--- | :--- |
| **Code Privacy** | Code snippets sent over HTTPS to third-party cloud servers (OpenAI / Anthropic / Microsoft). | **100% Air-Gapped & Local:** All tokens processed on localhost via Ollama. Zero network packets leave machine. |
| **Model Architecture** | Single monolithic LLM (e.g. GPT-4o) tasked with planning, coding, and debugging identically. | **Heterogeneous Dynamic Routing:** Dedicated models assigned to Planner, Coder, Tester, and Debugger. |
| **Codebase Context** | Arbitrary character-based chunking or manual copy-pasting of full files, leading to high token burn. | **AST + Vector Hybrid RAG:** Structural class/function outlines + semantic vector retrieval (65%-85% token savings). |
| **Testing & Verification** | Developer manually copies generated code into IDE, runs unit tests, and manually copies error back to AI. | **Integrated Sandboxed Runner:** Automated local execution (Python unittest, GCC, Node) with exit-code capture. |
| **Bug Remediation** | Manual debugging prompt engineering; developer repeats prompt back-and-forth 5-10 times. | **Closed-Loop Self-Healing:** Test stderr trace automatically injected into Debugger agent for multi-pass auto-repair. |
| **Latency & Cost** | High cloud billing ($1.5k-$3.5k/1k tasks); subject to remote API rate limits and peak queue delays. | **$0.00 Token Cost:** Runs locally on existing workstation GPU hardware with sub-50ms token stream latency. |

---

## Section 5: Market Analysis & Competitor Differentiation Matrix

### 5.1 Comprehensive Competitive Matrix

| Capability / Metric | GitHub Copilot | Cursor AI | Devin / OpenHands | DevForge AI (Us) |
| :--- | :--- | :--- | :--- | :--- |
| **Data Privacy & On-Premise** | ❌ Cloud Only (Sends code to MS/OpenAI) | ❌ Cloud Only (Remote vector indexing) | ⚠️ Cloud / Complex Docker cluster | **✅ 100% Local / Air-Gapped** (Ollama) |
| **Agent Architecture** | ❌ Single Assistant Autocomplete | ❌ Autocomplete & Chat Pane | ✅ Multi-Agent (Cloud LLMs) | **✅ Hierarchical Multi-Agent** (Supervisor + 4 Agents) |
| **Dynamic Model Routing** | ❌ Fixed Model (GPT-4o/Claude) | ❌ Fixed Model per query | ❌ Single LLM Backbone | **✅ Heterogeneous LLM Router** (Per-task specialization) |
| **Context Retrieval Engine** | ⚠️ Window buffer / basic embeddings | ✅ Remote codebase embeddings | ⚠️ Shell command exploration | **✅ Hybrid AST + Local Vector RAG** |
| **Execution & Sandboxing** | ❌ None (User must run in IDE) | ⚠️ Terminal command generation | ✅ Remote Cloud VM Sandbox | **✅ Local Sandbox** (Python, GCC, Node.js) |
| **Cost per 1k Dev Tasks** | $1,000 – $3,000+ | $500 – $1,500+ | $2,000 – $5,000+ | **📉 $0.00** (Zero marginal compute) |

---

## Section 6: User Personas & Target Stakeholders

* **Persona 1: Enterprise Systems Architect (Arjun Sharma)**  
  * *Organization:* Tier-1 Investment Bank / FinTech  
  * *Objective:* Build secure internal microservices without violating SOC2/banking regulations.  
  * *Pain Point:* Cloud AI tools are blocked by corporate firewalls.  
  * *Value:* 100% private, air-gapped agentic development on internal GPU servers with zero data exfiltration risk.
* **Persona 2: Embedded & Systems Software Engineer (Priya Nair)**  
  * *Organization:* Industrial Automation & Embedded Systems Consultancy  
  * *Objective:* Develop robust C/C++ drivers and low-level CLI utilities.  
  * *Pain Point:* Cloud AI tools produce generic Python snippets or hallucinate C headers that fail GCC compilation.  
  * *Value:* Integrated MinGW GCC sandbox that immediately compiles C code, catches errors, and triggers the Debugger.
* **Persona 3: Academic & AI/ML Software Researcher (Rohan Deshmukh)**  
  * *Organization:* Department of Computer Science & Autonomous Agent Lab  
  * *Objective:* Benchmark multi-agent collaboration patterns and evaluate single-model vs heterogeneous performance.  
  * *Pain Point:* Existing agent frameworks are tightly coupled to cloud OpenAI keys.  
  * *Value:* Native PySide6 interface with hot-swappable local Ollama models, live EventBus telemetry, and reproducible test suites.

---

## Section 7: Complete End-to-End System Architecture

### 7.1 Architecture Diagram & Component Flow
*(Ref: `E:/Capstone_MITCORER/docs/prd/Flow.png`)*

```
User Prompt (Natural Language Goal)
       │
       ▼
Supervisor / Orchestrator Core (src/agents/supervisor.py)
       │
       ├────────────────────────────────────────┐
       ▼                                        ▼
Specialized Agents                      Production RAG Layer (src/rag/ast_parser.py)
├── Planning Agent (deepseek-coder-v2)  ├── AST Structural Class/Function Outlines
├── Coding Agent (codestral)            └── Local Vector Embedding Retriever
├── Testing Agent (codegemma)
└── Debugging Agent (devstral)
       │
       ▼
Dynamic Model Selection (Ollama Engine on localhost:11434)
       │
       ▼
Sandboxed Execution Runner (src/core/runner.py)
├── Python unittest Runner
├── MinGW GCC C/C++ Compiler
└── Node.js JavaScript Runner
       │
       ▼
Final Verified Software (Persisted to workspace/)
```

---

## Section 8: Supervisor / Orchestrator Core Mechanism

### 8.1 Centralized Pipeline Coordination
The `Supervisor` class (`src/agents/supervisor.py`) enforces a strict finite-state machine (FSM):
1. **Idle / Ready:** Listening for UI events on thread-safe `EventBus`.
2. **Intent Classification (`_is_coding_task`):** Separates conversational chit-chat from technical engineering tasks.
3. **Context Enrichment (RAG):** Parses workspace AST symbols and injects structural outlines.
4. **Planning Phase:** Prompts Planner agent to create step-by-step specifications.
5. **Coding Phase:** Directs Coder agent to synthesize source code and persists files.
6. **Testing Phase:** Instructs Tester agent to synthesize test cases.
7. **Sandbox Execution:** Executes test suite in isolated subprocess.
8. **Conditional Debugging Loop:** Captures `stderr` on failure and routes to Debugger (up to 3 iterations).
9. **Pipeline Finished:** Emits completion events and restores UI interactivity.

---

## Section 9: Dynamic Heterogeneous Model Routing

### 9.1 Capability Routing Matrix

| Specialized Agent | Optimal Production Model | Lightweight Fallback (4GB VRAM) | Technical Rationale & Capability Justification |
| :--- | :--- | :--- | :--- |
| **Supervisor / Router** | `qwen2.5-coder:7b` | `qwen2.5-coder:1.5b` | Sub-second latency, deterministic prompt categorization, lightweight memory footprint. |
| **Planner Agent** | `deepseek-coder-v2:16b` | `qwen2.5-coder:7b` | Superior architectural reasoning, complex multi-file decomposition, design pattern mastery. |
| **Coder Agent** | `codestral:22b` | `qwen2.5-coder:7b` | State-of-the-art Fill-In-The-Middle (FIM), multi-language syntax precision, low hallucination rate. |
| **Tester Agent** | `codegemma:7b` | `qwen2.5-coder:1.5b` | Fast assertion generation, unit test boilerplate synthesis, boundary condition mocking. |
| **Debugger Agent** | `devstral:24b` | `qwen2.5-coder:7b` | Codebase refactoring specialist; analyzes compiler stack traces and applies in-place syntax diffs. |

---

## Section 10: Production Code RAG Layer (AST + Vector Hybrid)

### 10.1 Two-Tier Retrieval Engine
* **Structural AST Extraction (`src/rag/ast_parser.py`):** Utilizes Python's native `ast` library to extract class definitions, method signatures, parameter names, docstrings, and imports. Provides 100% accurate symbol tables using less than 15% of the token overhead of raw files.
* **Semantic Vector Retrieval:** Code is chunked along function/class boundaries and embedded using local models (`nomic-embed-text` via Ollama). Cosine similarity matches queries to relevant code blocks.

---

## Section 11: Closed-Loop Automated Execution & Healing

### 11.1 Sandboxed Execution Architecture (`src/core/runner.py`)
* **Python Tests:** Executes `unittest` via subprocess.
* **C/C++ Compilation:** Runs MinGW GCC (`gcc file.c test_file.c -o test.exe`) and executes binary.
* **Node.js Sandbox:** Runs JS tests via local Node.js.
* **Timeout Enforcement:** Subprocess execution is capped at 15 seconds to prevent infinite loops.

### 11.2 Self-Healing Loop
When exit code != 0, the Supervisor captures `stderr`, activates the Debugger agent, generates patches, writes them to disk, and re-executes tests up to 3 times until passing.

---

## Section 12: Complete Application Screen Architecture (PySide6)

The desktop GUI (`src/pyside_app.py`) is structured into six modular panels:
1. **Workspace Hub & Header:** Folder selector, system health, and Ollama connection status.
2. **Prompt & Model Console:** Natural language input, execution button, dynamic model dropdowns.
3. **OS File Tree Explorer:** Live OS filesystem viewer (`QTreeView` + `QFileSystemModel`).
4. **Monospace Code Inspector:** Multi-tab syntax viewer displaying clicked files.
5. **Multi-Language Terminal:** Real-time console displaying compiler and test execution traces.
6. **Agent Pipeline Status Cards:** Color-coded status telemetry for Planner, Coder, Tester, and Debugger.

---

## Section 13: Screens 1 to 3 Detailed Specifications

* **Panel 1 (Workspace Hub):** Manages active project path, directory browsing, and Ollama heartbeat status.
* **Panel 2 (Prompt Console):** Ingests natural language goals, provides model dropdowns, and triggers async pipeline.
* **Panel 3 (OS File Tree):** Automatically watches OS filesystem write events and refreshes instantly.

---

## Section 14: Screens 4 to 6 Detailed Specifications

* **Panel 4 (Code Inspector):** Monospace read-only code viewer with tab switching and line numbers.
* **Panel 5 (Terminal):** Displays GCC compiler output, unittest results, and Node.js logs.
* **Panel 6 (Agent Cards):** Displays real-time state, token counts, and outputs for all active agents.

---

## Section 15: Functional Requirements Triage (P0 Core MVP)

* **FR-P0-01 (Supervisor Orchestration):** Coordinates Planner, Coder, Tester, Debugger across background worker thread with non-blocking UI.
* **FR-P0-02 (Local Ollama Integration):** Asynchronous HTTP client communicating with Ollama REST API (`127.0.0.1:11434`).
* **FR-P0-03 (AST Parser Integration):** Parses workspace Python files into structured class and method representations.
* **FR-P0-04 (Sandboxed Code Runner):** Executes test suites locally across Python, C, and JavaScript.
* **FR-P0-05 (Closed-Loop Auto Healing):** Captures stderr on test failure and triggers Debugger for in-place code repair.
* **FR-P0-06 (PySide6 Desktop GUI):** Modern dark navy desktop interface with resizable QSplitters and file tree explorer.

---

## Section 16: Functional Requirements (P1 & P2 Roadmap)

* **FR-P1-01 (Dynamic Model Selector GUI):** GUI dropdowns allowing developers to assign distinct Ollama models per sub-agent at runtime.
* **FR-P1-02 (Vector Semantic Retrieval):** Chunks code along function/class boundaries and indexes via local embeddings.
* **FR-P1-03 (Side-by-Side Diff Inspector):** Visual unified diff view highlighting additions and deletions proposed by Coder or Debugger.
* **FR-P1-04 (Multi-File Syntax Validator):** Pre-write AST validation ensuring generated code does not contain syntax errors.
* **FR-P2-01 (Git Worktree Isolation):** Creates temporary Git worktree branches for each agent task to enable instant rollback.
* **FR-P2-02 (Multi-Node GPU Load Balancer):** Distributes inference requests across multiple networked Ollama GPU server nodes.

---

## Section 17: Non-Functional Requirements (NFRs)

* **NFR-PERF-01 (UI Responsiveness):** Desktop UI maintains 60 FPS rendering without stutter during model streaming.
* **NFR-PERF-02 (Disk Preservation):** Model weights stored on secondary drive (`E:/OllamaModels`).
* **NFR-SEC-01 (100% Air-Gapped):** Zero outbound network telemetry; all traffic restricted to `127.0.0.1`.
* **NFR-SAFE-01 (Sandbox Isolation):** Subprocess execution constrained to workspace with 15-second execution timeout.
* **NFR-REL-01 (Fault Recovery):** Handles Ollama disconnections gracefully without application crashes.

---

## Section 18: Data Contracts & IPC Message Schemas

Inter-agent communication is governed by the typed `EventBus`:
* `pipeline_start`: `{"goal": str, "workspace": str}`
* `agent_activated`: `{"agent": str}`
* `token_stream`: `{"agent": str, "token": str}`
* `file_written`: `{"filename": str, "filepath": str, "content": str}`
* `sandbox_execution`: `{"message": str}`
* `test_run_result`: `{"success": bool, "stdout": str, "stderr": str, "exit_code": int}`
* `pipeline_finished`: `{"status": str, "workspace": str}`

---

## Section 19: End-to-End User Journey Walkthrough (Pune Capstone Task)

1. Developer inputs: *"Build a modular C string reversal and palindrome checking utility with header files and automated unit tests."*
2. Supervisor enriches context using `ast_parser.py` and dispatches goal to Planner (`deepseek-coder-v2`).
3. Planner outputs modular plan: `utils.h`, `utils.c`, and `test_main.c`.
4. Coder (`codestral`) synthesizes `utils.h` and `utils.c`.
5. Tester (`codegemma`) generates unit test suite `test_main.c`.
6. CodeRunner compiles and runs C binary via MinGW GCC.
7. Terminal displays live GCC output; tests pass; files appear in OS file tree explorer.

---

## Section 20: Seven-Phase Implementation Roadmap
*(Ref: `E:/Capstone_MITCORER/docs/prd/phases.png`)*

* **Phase 1: Literature Survey & Research (Month 1):** Study multi-agent SE frameworks and define research questions.
* **Phase 2: Ollama Model Benchmarking (Months 2–3):** Profile Qwen, Codestral, DeepSeek, and Devstral on local hardware.
* **Phase 3: Multi-Agent Architecture (Months 4–5):** Formalize Supervisor state machine and PySide6 EventBus.
* **Phase 4: RAG Implementation (Months 6–7):** Implement AST syntax parsing and local vector embeddings.
* **Phase 5: Platform Development (Months 8–10):** Build PySide6 UI, native splitters, OS file explorer, and compiler runners.
* **Phase 6: Experiments & Evaluation (Months 11–12):** Comparative trials: Single-Model vs. Heterogeneous Multi-Model.
* **Phase 7: Analysis & Research Paper (Month 13+):** Document findings, publish paper, and release enterprise packaging.

---

## Section 21: Comprehensive Verification & Test Suite

| Test ID | Category & Input Condition | Expected System Behavior | Automated Assertion Rule | Tier |
| :--- | :--- | :--- | :--- | :--- |
| **TC-INT-01** | Casual Greeting (e.g. 'hello') | Identifies chat intent; streams reply without writing files. | `status == 'chat_completed' && files_written == 0` | P0 |
| **TC-AST-01** | Complex Python File | Extracts class tree, arguments, and docstrings in <100ms. | `syntax_valid == True && len(classes) > 0` | P0 |
| **TC-RUN-01** | C Compilation (MinGW GCC) | Compiles multi-file C project; executes binary. | `success == True && exit_code == 0` | P0 |
| **TC-DBG-01** | Intentional Syntax Bug | Unit test fails; Supervisor routes stderr to Debugger for fix. | `retest_success == True && retry_count <= 2` | P0 |
| **TC-SAFE-01** | Infinite Loop Execution | Runner enforces 15-second timeout; kills child process cleanly. | `timed_out == True && elapsed_time < 16.0s` | P0 |

---

## Section 22: Quantitative Benchmarks & KPIs

* **First-Pass Synthesis Quality:** $\ge 78.0\%$ Pass@1 with heterogeneous routing (vs. $42.0\%$ single-model baseline).
* **Autonomous Bug Healing Rate:** $\ge 82.0\%$ resolution within 3 iterations with Devstral.
* **Context Window Compression:** $65\% - 85\%$ token reduction via AST structural summaries.
* **End-to-End Task Latency:** $< 60$ seconds from prompt to passing test run.
* **Inference Cloud Cost:** $\$0.00$ on local GPU compute (saving $\$1.5\text{k}-\$3.5\text{k}$ per 1k tasks).

---

## Section 23: Hardware Profile & Resource Sizing

* **Tier 1 (Consumer Laptop - 4GB VRAM):** Sequential GGUF model execution (Qwen2.5-Coder 7B / CodeGemma 2B) with AST pruning.
* **Tier 2 (Mid-Range Workstation - 8GB–12GB VRAM):** Partial GPU offload; concurrent resident models; vector similarity enabled.
* **Tier 3 (Enterprise Server - 24GB+ VRAM):** All models resident in VRAM (Codestral 22B, DeepSeek-Coder-V2 16B, Devstral 24B); parallel execution.

---

## Section 24: Risks, Assumptions & Mitigation Strategies

* **Infinite Debugging Loops:** Mitigated by strict 3-iteration retry cap and graceful degradation.
* **Model Hallucinations:** Mitigated by AST symbol outline injection and standard library constraints.
* **Storage Exhaustion:** Mitigated by configuring `OLLAMA_MODELS` to secondary partition (`E:/OllamaModels`).

---

## Section 25: Enterprise Monetization & Budget Model

* **Enterprise On-Prem License:** \$150 / developer / month for self-hosted GPU clusters.
* **Turnkey Managed Appliance:** \$499 / server node / month for pre-configured air-gapped appliances.
* **Custom RAG Engagements:** \$15,000 – \$50,000 per enterprise engagement.
* **Seed Funding Ask:** \$250,000 for 14-month runway (40% Core RAG dev, 25% Hardware cluster, 20% Enterprise pilots, 15% Compliance & Legal).

---

## Section 26: Comprehensive Engineering Glossary

* **PRD:** Product Requirements Document outlining functional and architectural requirements.
* **Supervisor:** Central agent managing pipeline state transitions and inter-agent message passing.
* **AST:** Abstract Syntax Tree used for structural symbol extraction without full-source token burn.
* **RAG:** Retrieval-Augmented Generation augmenting prompts with relevant local code context.
* **Heterogeneous Routing:** Assigning different specialized models to different software engineering tasks.
* **Ollama:** Local runtime executing quantized neural networks via llama.cpp.
* **PySide6:** Official Qt 6 Python bindings providing native desktop UI rendering.

---

## Section 27: Academic Citations & References

1. Hong, S., et al. (2024). *MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework.* arXiv:2308.00352.
2. Qian, C., et al. (2023). *Communicative Agents for Software Development.* arXiv:2307.07924.
3. Jimenez, C. E., et al. (2024). *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* ICLR 2024.
4. Hui, B., et al. (2024). *Qwen2.5-Coder Technical Report: Code Intelligence at Scale.* Alibaba Group.
5. DeepSeek-AI (2024). *DeepSeek-Coder-V2: Breaking the Barrier of Closed-Source Models in Code Intelligence.* arXiv:2406.11931.
6. Mistral AI (2024). *Codestral: State-of-the-Art Open-Weight Model for Code Generation.* Mistral AI Research.
7. Google DeepMind (2024). *CodeGemma: Open Code Models Based on Gemma Architecture.* Google Research.

---

## Section 28: Final Executive Project Synthesis

DevForge AI delivers a transformative, 100% private, on-premise multi-agent software development platform. By resolving the single-model catch through **Dynamic Heterogeneous Model Routing** and **Production Hybrid Code RAG**, DevForge AI proves that enterprise-grade autonomous software engineering can flourish entirely on local hardware with zero cloud API costs and zero intellectual property leakage.
