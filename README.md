# DevForge AI 3.0

A **fully local** coding assistant in the style of Antigravity / Claude Code / Codex - but it runs on
your own Ollama models, so there are no API keys, no usage limits and no code leaves your machine.

## How to use

1. Double-click `run_devforge.bat` (or `.venv\Scripts\python.exe -m devforge`).
2. Click **＋ Open Folder** and pick a project folder. Previously opened folders are listed on the
   left; clicking one restores its saved conversations.
3. Pick a side at the top:
   - **💬 Chat** - talk to the model about anything, project related or not.
   - **</> Code** - strictly about the open folder. Ask it to build or change things
     (*"generate a simple website for a shoe store"*) or ask about the code
     (*"what does main.py do?"*). Off-topic prompts are politely refused and you are pointed to Chat.
     Generated files appear in the folder; use **▶ Run** to open the site or run the script.

Chat and Code keep **separate histories per folder** (stored in `<folder>/.devforge/`).

## Agents and models (all via Ollama)

| Agent | Model | Job |
|---|---|---|
| Router | `qwen2.5-coder:1.5b` | decides build / ask / off-topic in Code mode, names chats, saves memory |
| Researcher | `qwen2.5:7b` | offline design brief from your request + project docs |
| Designer | `qwen2.5:7b` | picks one of six ready-made themes for a new website |
| Planner | `deepseek-coder:6.7b` | file plan |
| Coder | `qwen2.5-coder:7b` | writes each file, answers project questions, powers Chat |
| Reviewer | `qwen2.5-coder:7b` | reviews JS/Python logic; a finding counts only if it quotes real code |
| Tester | `qwen2.5-coder:7b` | unit tests (Python) |
| Debugger | `qwen2.5-coder:7b` | fixes failing checks/tests (2 rounds) |
| RAG embeddings | `nomic-embed-text` | vector half of hybrid search |

Each agent uses the model that suits its task. The Tester and Debugger moved from `codegemma:2b`
and `qwen2.5-coder:1.5b` to `qwen2.5-coder:7b`: the small models often returned no usable test file
or could not repair real errors.

**Written by code, not by a model** (so they always work): `theme.css` (six themes, both light and
dark palettes, mobile menu styles), `theme-toggle.js` (light/dark switch), `site.js` (hamburger menu
and active nav link), the colour converter that turns fixed colours in `styles.css` into theme
colours, and the HTML/CSS/JS mismatch check that sends real mismatches to the Debugger.

Change them in `devforge/config.py` (`ENABLE_RESEARCH` / `ENABLE_REVIEW` switch the two optional
steps off for speed). If a model is missing, the closest installed one is used. Without an
embedding model, RAG falls back to keyword search only.

## Architecture

```
devforge/
  config.py   model-per-role settings
  llm.py      Ollama client (streaming chat, embeddings, model resolution)
  rag.py      Code RAG: AST-aware chunking, BM25 + optional vector search, RRF fusion, repo map
  fsops.py    safe file writes (path-traversal guard), LLM-output parser, static checks, run helpers
  engine.py   Chat engine + Code pipeline
  store.py    per-folder history + recent folders
  ui/         PySide6 window
tests/        headless tests (fake LLM) -> python -m unittest tests.test_core
```

**Code pipeline:** intent router → RAG context (repo map + relevant chunks) → **Researcher** design brief → **Planner** writes a
file plan → **Coder** writes each file in its own call (HTML before CSS/JS so names match) →
**Reviewer** checks the code (Coder fixes findings) → **Tester** writes `unittest` tests for Python logic → verifier (syntax / HTML refs / JSON / JS
`node --check` / unit tests) → **Debugger** self-healing loop (up to 2 rounds, rejects truncated
rewrites) → RAG index refresh so follow-up prompts see the new files.

Safety: every write is confined to the opened folder; `..`, drive-letter and `.devforge` paths are rejected.

## Skills, memory and smart routing

- **✦ Skills** - write standing instructions per project; each is saved as `skills/<name>.md` inside the
  project folder. DevForge applies relevant skills automatically, or force one with `/skill-name` in a prompt.
- **🧠 Memory** - short facts from your chats are saved in `.devforge/memory.json` and, together with excerpts
  from the folder's other chats, given to every new chat (Chat and Code). View, edit, clear or switch it off
  from the Memory button.
- **Supervisor routing** - each build request is classified (`new`, `redesign`, `toggle`, `fix`, `change`).
  Only a new site runs the Researcher; only a new site or an explicit redesign runs the Designer, so bug fixes
  and feature requests never overwrite your theme. A "light/dark toggle" request is done directly (no model):
  `theme.css` gets both palettes and `theme-toggle.js` switches them.
- **Parallel chats** - several chats can run at once; they take turns on the GPU.

## Project layout

```
devforge/           the application (run with run_devforge.bat)
tests/              automated tests:  python -m unittest tests.test_core
docs/               report, presentation, guides, PRD, pitch decks  (see docs/README.md)
legacy_v2/          older prototype (v2.x) described in the report
samples/            example projects generated by DevForge AI
other_coursework/   other subjects, not part of this project
```
