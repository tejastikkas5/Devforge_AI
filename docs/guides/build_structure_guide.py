"""Builds DevForge_AI_Structure_Guide.pdf. Run from the project root:
    .venv\\Scripts\\python.exe docs\\guides\\build_structure_guide.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted, KeepTogether

OUT = "docs/guides/DevForge_AI_Structure_Guide.pdf"
ACC = colors.HexColor("#2F4EA2")
ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["BodyText"], fontName="Helvetica", fontSize=10, leading=14, spaceAfter=5)
title = ParagraphStyle("t", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=21, textColor=ACC, alignment=0, spaceAfter=2)
sub = ParagraphStyle("s", parent=body, textColor=colors.grey, spaceAfter=10)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=13.5, textColor=ACC, spaceBefore=12, spaceAfter=5)
h3 = ParagraphStyle("h3", parent=ss["Heading3"], fontName="Helvetica-Bold", fontSize=11.5, spaceBefore=10, spaceAfter=3)
cell = ParagraphStyle("c", parent=body, fontSize=9, leading=12, spaceAfter=0)
cellb = ParagraphStyle("cb", parent=cell, fontName="Helvetica-Bold")
tree = ParagraphStyle("tree", fontName="Courier", fontSize=8.5, leading=11, backColor=colors.HexColor("#F3F5FA"),
                      borderPadding=6, spaceAfter=8)


def P(t, st=body): return Paragraph(t, st)


def table(rows, widths=(52*mm, 118*mm)):
    data = [[P(c, cellb if i == 0 else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=list(widths), repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDE5F7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8C2DC")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FD")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t


def folder(name, intro, rows):
    """One folder section: heading, one-line meaning, then a File | What it does table."""
    t = table([["File", "What it does"]] + rows, (62*mm, 108*mm))
    if len(rows) <= 8:
        return [KeepTogether([P(name, h3), P(intro), t]), Spacer(1, 2)]
    return [KeepTogether([P(name, h3), P(intro)]), t, Spacer(1, 2)]


s = [P("DevForge AI - Project Structure Guide", title),
     P("Every project folder and file, one by one, in the same order as the project folder. "
       "Simple words, short answers. Code on GitHub: github.com/tejastikkas5/Devforge_AI", sub)]

# ------------------------------------------------------------------ 1
s += [P("1. The project in 30 seconds", h2),
      P("DevForge AI is a desktop app, like Claude Code or Codex, that runs completely on our own laptop using local AI models "
        "(through Ollama). You type a goal such as \"build a shoe store website\". A team of AI agents plans it, writes the files, "
        "checks them and fixes mistakes, and saves everything in your project folder. No cloud, no API cost, and no code leaves the PC.")]

# ------------------------------------------------------------------ 2
TREE = """Capstone_MITCORER/
|-- .venv/              Python environment (installed packages)
|-- devforge/           THE APP (version 3.0) - main code
|   `-- ui/             the desktop window
|-- docs/               all documents (report, slides, guides, PRD, pitch)
|-- legacy_v2/          the older version 2 of the app
|-- samples/            example projects DevForge made
|-- tests/              automated tests
|-- .gitignore          files GitHub should ignore
|-- README.md           project description and how to use
|-- requirements.txt    packages to install
`-- run_devforge.bat    double-click to start the app"""
s += [KeepTogether([P("2. Folder map", h2), Preformatted(TREE, tree)])]

# ------------------------------------------------------------------ 3
s += [P("3. Folder by folder", h2)]

s += folder("3.1  .venv/", "The project's own Python environment. It holds the installed packages (PySide6, requests, Markdown) "
            "so the app runs the same on every PC. We never edit it, and it is not uploaded to GitHub.", [
    [".venv/Scripts/python.exe", "The Python that run_devforge.bat uses to start the app."],
])

s += folder("3.2  devforge/  (the main app)", "This is the real project. Everything the app does is in this folder.", [
    ["__init__.py", "Marks the folder as a Python package and stores the version number (3.0.0)."],
    ["__main__.py", "The start point. Running <b>python -m devforge</b> opens the window."],
    ["config.py", "Settings: which AI model does which job (ROLE_MODELS), and on/off switches like the number of fix rounds."],
    ["engine.py", "<b>The brain (Supervisor).</b> Understands the request (question / build / off-topic), runs the agents in order, "
                  "checks the result and runs the fix loop."],
    ["rag.py", "<b>RAG.</b> Reads the project, cuts code into functions and classes, and finds the code most related to the "
               "question (keyword + meaning search) to give to the AI."],
    ["llm.py", "Talks to Ollama (the local AI server). Sends prompts, streams answers, makes embeddings, and picks an installed model."],
    ["prompts.py", "The written instructions for each agent (Planner, Coder, Tester, Debugger, Reviewer...)."],
    ["fsops.py", "File tools. Writes files safely (only inside the project folder), checks HTML/CSS/JS/Python, "
                 "checks that the JavaScript only uses ids/classes that exist in the HTML/CSS, "
                 "repairs broken links, and runs code with a time limit."],
    ["themes.py", "The <b>site kit</b>, written by code so it always works: six ready-made designs for the <i>websites DevForge builds</i> (both light and dark palettes, mobile menu styles), the light/dark switch, site.js (hamburger menu, active nav link) and the colour converter that turns fixed colours into theme colours. The Designer agent just picks a design."],
    ["skills.py", "Skills: your own instructions saved per project (skills/*.md), used automatically or by typing /name."],
    ["memory.py", "Project memory. Saves short facts and searches old chats so a new chat remembers earlier ones."],
    ["store.py", "Saves every chat of a project (each message with its time), remembers recently opened folders, and saves app settings such as your light/dark choice (in ~/.devforge/)."],
])

s += folder("3.3  devforge/ui/", "The user interface (what you see on screen), built with PySide6 (Qt).", [
    ["__init__.py", "Small time helpers: works out how long each reply took (from the saved message times) and formats it, e.g. 1m 15s."],
    ["main_window.py", "The whole window: project and chat list, Chat and Code tabs, file tree, code viewer, Run button, "
                       "the light/dark theme switch with its two colour sets (Midnight Violet and Soft Lavender), "
                       "Skills and Memory windows. Runs AI jobs in the background so the window never freezes."],
    ["chat_web.py", "The modern chat area, drawn with HTML/CSS: gradient bubbles, avatars, code cards with a Copy button, \"Working on it\" timeline with a live clock, and a \"Completed in ...\" time under every reply. If it cannot load, the window falls back to a simple built-in chat view."],
])

s += [P("<b>Hidden folder made by the app:</b> when you open a project, DevForge creates a <b>.devforge/</b> folder inside it with "
        "<b>chats/</b> (saved chats), <b>memory.json</b> (project memory) and <b>embeddings.json</b> (RAG cache).")]

s += folder("3.4  docs/", "All written material about the project. No app code here.", [
    ["README.md", "A one-page index of what is inside docs/."],
    ["report/", "The capstone project report (Word and PDF) and its front pages."],
    ["presentation/", "The final review presentation (.pptx and .pdf)."],
    ["guides/", "Short guides for the viva (see the next table)."],
    ["prd/", "Product Requirements Document: what we planned to build, its diagrams (Flow.png, phases.png), "
             "and the Python scripts in prd/builder/ that generate the PDF."],
    ["pitch/", "Earlier startup pitch decks (.pptx, .pdf) and generate_pitch_deck.py, the script that made them."],
])

s += folder("3.5  docs/guides/", "Easy explanations to prepare for the viva.", [
    ["DevForge_AI_Structure_Guide.pdf", "This guide: every folder and file in simple words."],
    ["DevForge_AI_How_It_Works.pdf", "How the whole system works, step by step."],
    ["DevForge_AI_Models_Guide.pdf", "Which AI models we use, why, and what hardware they need."],
    ["DevForge_AI_RAG_Explained.pdf", "RAG explained simply, with likely viva questions."],
    ["Project_Understanding_Guide/", "A long, detailed guide (.md and .pdf) plus the builder/ scripts that create it."],
    ["build_structure_guide.py, build_rag_explainer.py", "Scripts that generate this guide and the RAG guide."],
])

s += folder("3.6  legacy_v2/  (old version)", "Version 2 of DevForge, which the project report describes. "
            "Kept to show how the project grew. Not used by the new app.", [
    ["config/settings.py", "Old settings: app name, Ollama address, workspace folder."],
    ["src/app.py", "Old window made with CustomTkinter."],
    ["src/pyside_app.py", "A later PySide6 version of the old window."],
    ["src/agents/", "The 4 old agents: planner.py, coder.py, tester.py, debugger.py, plus base_agent.py (shared code) "
                    "and supervisor.py (runs them in order)."],
    ["src/core/", "event_bus.py (sends updates to the window), model_router.py (picks a model per agent), "
                  "project_manager.py (handles project folders), runner.py (runs generated code)."],
    ["src/llm/ollama_client.py", "Old connection to Ollama."],
    ["src/rag/ast_parser.py", "Old AST reader that lists classes, functions and imports in Python files."],
    ["src/ui/components/file_tree.py", "Old file tree panel."],
])

s += folder("3.7  samples/", "Real output from our test runs. Good to show in the demo.", [
    ["shoe_store_test/", "A shoe store website made from one prompt (index.html, styles.css, script.js)."],
    ["design_test/", "A website made to test the Designer agent and themes (includes theme.css)."],
    ["old_prototype_output/", "Python and C programs with tests made by the old version 2 (e.g. reverse_string, palindrome)."],
])

s += folder("3.8  tests/", "Automated checks that prove the app works.", [
    ["test_core.py", "63 tests: reading files from AI replies, RAG search, routing, memory, skills, safe file writing, the reply timer, the site kit "
                     "(colour converter, mismatch check, repairing an existing site), dead-link repair, backend route check, "
                     "the no-change retry, the cut-off and wrong-content guards, the proof-based Reviewer, and the full "
                     "agent pipeline with a fake AI. Run: <b>python -m unittest tests.test_core</b> (all pass)."],
])

s += folder("3.9  Files in the main folder", "The small files at the top level.", [
    [".gitignore", "Tells Git not to upload .venv, __pycache__ and .env."],
    ["README.md", "Project description, how to use it, which agent uses which model, and the architecture."],
    ["requirements.txt", "The Python packages to install: PySide6, requests, Markdown."],
    ["run_devforge.bat", "Double-click to start the app. Uses .venv's Python and points Ollama to the models on drive E:."],
])

# ------------------------------------------------------------------ 4
s += [P("4. What happens when you press Send", h2), table([
    ["#", "Step", "Where in the code"],
    ["1", "You type a prompt in the window", "ui/main_window.py"],
    ["2", "A background worker passes it to the Engine (Supervisor)", "engine.py"],
    ["3", "Engine decides: question, build or off-topic, and the type of build", "engine.py: classify_intent, _classify_build"],
    ["4", "RAG finds the related code and makes a file map", "rag.py"],
    ["5", "Agents run in order: Researcher, Designer, Planner, Coder, Reviewer, Tester", "engine.py, prompts.py, config.py"],
    ["6", "Files are written safely and checked", "fsops.py"],
    ["7", "If a check fails, the Debugger fixes it (up to 2 rounds)", "engine.py: _verify, _debug"],
    ["8", "Chat is saved; short facts go to memory", "store.py, memory.py"],
], (8*mm, 100*mm, 62*mm))]

# ------------------------------------------------------------------ 5
s += [P("5. If the judge asks: \"Where did you implement ...?\"", h2), table([
    ["Question", "Answer: file and name"],
    ["RAG (retrieval)", "devforge/rag.py, class CodeIndex; used in engine.py (index().context())."],
    ["Agents / Supervisor", "engine.py (_build) and prompts.py."],
    ["Different model per agent", "config.py (ROLE_MODELS) and llm.py (resolve_model picks the installed model)."],
    ["Mobile menu, colours that follow the theme", "themes.py (SITE_JS, theme_colours), applied by engine.py (_repair_site)."],
    ["HTML/CSS/JS mismatch check", "fsops.py: consistency_check, used in engine.py (_verify)."],
    ["Nav links that go to # / nowhere", "fsops.py: fix_nav_anchors (auto-fix) and dead_nav_links (reported to the Debugger)."],
    ["Frontend fetch() must match backend routes", "fsops.py: consistency_check (reads the Python server routes)."],
    ["Strict senior-engineer prompts per agent", "prompts.py: role, hard rules, self-check list, exact output format."],
    ["Reviewer that cannot invent bugs", "engine.py: _review keeps a finding only if it quotes real code (_proven)."],
    ["Self-healing fix loop", "engine.py: _verify and _debug, up to 2 rounds."],
    ["Running / checking code", "fsops.py: static_check, run_python, run_command."],
    ["Safety (stay inside the folder)", "fsops.py: safe_join blocks ../ and drive letters."],
    ["Intent routing", "engine.py: classify_intent and _classify_build."],
    ["Website themes (for built sites)", "themes.py and engine.py (_design, _toggle_theme)."],
    ["App light/dark switch", "ui/main_window.py: PALETTES, ToggleSwitch, set_theme; choice saved by store.py (save_setting)."],
    ["Modern chat bubbles, code cards", "ui/chat_web.py: WebChatView (HTML/CSS through Qt WebEngine)."],
    ["Reply timer (Completed in ...)", "ui/__init__.py (reply_durations, fmt_duration), shown by ui/chat_web.py."],
    ["Memory across chats", "memory.py; used by engine.py (_apply_memory, _remember)."],
    ["Skills", "skills.py; applied in engine.py (_apply_skills)."],
    ["Chat history", "store.py (files in .devforge/chats/)."],
    ["Several chats at once", "engine.py (_GPU_LOCK) and ui/main_window.py (Job, Worker)."],
    ["The window", "devforge/ui/main_window.py (PySide6)."],
    ["Old version from the report", "legacy_v2/src/."],
], (58*mm, 112*mm))]

# ------------------------------------------------------------------ 6
s += [P("6. Report vs. the code (so you are not surprised)", h2), table([
    ["The report says (version 2.2)", "The current code (version 3.0)"],
    ["4 agents: Planner, Coder, Tester, Debugger", "7 agents: Researcher, Designer, Planner, Coder, Reviewer, Tester, Debugger, plus a Router"],
    ["Debugger repairs up to 3 times", "Up to 2 repair rounds (MAX_DEBUG_ROUNDS in config.py)"],
    ["EventBus connects back end and UI", "Engine sends progress through a callback; the Worker turns it into Qt signals"],
    ["Six-panel window", "Simpler, modern window: sidebar, Chat and Code tabs, file tree, code viewer, output; light/dark themes and a reply timer"],
    ["Large models (16B-24B)", "Our laptop uses 1.5B-7B models; bigger ones can be set in config.py"],
    ["Tree-sitter planned for C and JavaScript", "Full AST for Python only; other files use line windows"],
], (85*mm, 85*mm)), Spacer(1, 6),
    P("Models in use (one per task): qwen2.5-coder 1.5B (Router, chat titles, memory), qwen2.5 7B (Researcher, Designer), "
      "deepseek-coder 6.7B (Planner), qwen2.5-coder 7B (Coder, Reviewer, Tester, Debugger), nomic-embed-text (RAG vectors). "
      "Tester and Debugger moved up from codegemma 2B / qwen2.5-coder 1.5B, which often could not write tests or repair real errors.")]


def footer(c, d):
    c.saveState(); c.setFont("Helvetica", 8); c.setFillColor(colors.grey)
    c.drawString(20*mm, 10*mm, "DevForge AI - structure guide for the viva")
    c.drawRightString(A4[0] - 20*mm, 10*mm, f"Page {d.page}")
    c.restoreState()


SimpleDocTemplate(OUT, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=16*mm, bottomMargin=18*mm,
                  title="DevForge AI - Project Structure Guide").build(s, onFirstPage=footer, onLaterPages=footer)
print("ok", OUT)
