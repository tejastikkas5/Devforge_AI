import os
import threading
from typing import Optional, Dict, Any, List
from src.llm.ollama_client import OllamaClient
from src.core.event_bus import bus
from src.core.runner import CodeRunner
from src.core.model_router import ModelRouter
from src.core.project_manager import ProjectManager
from src.rag.ast_parser import CodeASTAnalyzer
from src.agents.planner import PlannerAgent
from src.agents.coder import CoderAgent
from src.agents.tester import TesterAgent
from src.agents.debugger import DebuggerAgent
from config.settings import config

class Supervisor:
    """
    Central Autonomous Orchestrator.
    - User gives ONLY a prompt.
    - Supervisor coordinates specialized models in the background.
    - Enriches prompt with AST code RAG.
    - Saves all conversation history under the active project folder.
    - Allows direct 1-click execution of the generated project.
    """

    def __init__(self, client: Optional[OllamaClient] = None, workspace_dir: Optional[str] = None):
        self.client = client or OllamaClient(config.ollama_url)
        self.workspace_dir = os.path.abspath(workspace_dir or config.workspace_dir)
        self.runner = CodeRunner(self.workspace_dir)
        self.router = ModelRouter(self.client)
        self.project_manager = ProjectManager(config.workspace_dir)

        # Instantiate specialized sub-agents with models determined by ModelRouter
        self._init_agents()
        self.is_running = False

    def _init_agents(self):
        """Dynamically binds optimal models for each specialized role."""
        planner_model = self.router.get_model_for_role("planner")
        coder_model = self.router.get_model_for_role("coder")
        tester_model = self.router.get_model_for_role("tester")
        debugger_model = self.router.get_model_for_role("debugger")

        self.planner = PlannerAgent(planner_model, self.client)
        self.coder = CoderAgent(coder_model, self.client)
        self.tester = TesterAgent(tester_model, self.client)
        self.debugger = DebuggerAgent(debugger_model, self.client)

    def set_workspace(self, new_workspace: str):
        """Switches the active project directory."""
        self.workspace_dir = os.path.abspath(new_workspace)
        self.runner.set_workspace(self.workspace_dir)

    def get_workspace_ast_context(self) -> str:
        """
        Production AST Code RAG:
        Extracts structural symbols (classes, methods, docstrings, imports)
        from existing Python files in the workspace.
        """
        summaries = []
        try:
            for root, dirs, files in os.walk(self.workspace_dir):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('__pycache__', 'node_modules', 'venv', '.venv')]
                for f in files:
                    if f.endswith('.py'):
                        fpath = os.path.join(root, f)
                        ast_info = CodeASTAnalyzer.analyze_file(fpath)
                        if ast_info.get("syntax_valid"):
                            summaries.append(CodeASTAnalyzer.format_summary(ast_info))
                    elif f in ('index.html', 'styles.css', 'app.js', 'package.json'):
                        summaries.append(f"Existing file: {f}")
        except Exception as e:
            pass

        if summaries:
            return "Existing Codebase AST & Symbol Outline:\n" + "\n---\n".join(summaries[:15])
        return "Workspace currently has no existing source code files."

    def _is_coding_task(self, prompt: str) -> bool:
        """Determines whether a user prompt requires code generation vs conversational chat."""
        clean = prompt.strip().lower()
        greetings = {"hi", "hii", "hiii", "hello", "helloo", "hey", "heyy", "hola", "yo", "sup", "good morning", "good evening", "who are you", "what are you", "help"}
        if clean in greetings or clean.rstrip(".!?,") in greetings:
            return False

        action_keywords = [
            "build", "create", "generate", "write", "make", "implement", "add", "develop",
            "fix", "debug", "refactor", "code", "script", "program", "function", "class",
            "unittest", "setup", "compile", "convert", "modify", "update", "website", "app",
            "frontend", "backend", "ui", "api", "html", "css", "js", "python"
        ]
        if any(kw in clean for kw in action_keywords):
            return True

        words = clean.split()
        if len(words) <= 3 and not any(k in clean for k in ["file", "app", "py", "c", "js", "html"]):
            return False

        return True

    def start_pipeline_async(self, user_request: str):
        """Launches the multi-agent pipeline in a background thread so UI never hangs."""
        if self.is_running:
            return
        thread = threading.Thread(target=self._run_pipeline, args=(user_request,), daemon=True)
        thread.start()

    def _run_pipeline(self, user_request: str):
        self.is_running = True
        self.router.refresh()
        self._init_agents() # Ensure optimal models are assigned

        # Save user message to project history
        self.project_manager.append_message(self.workspace_dir, "USER", user_request)

        bus.post("pipeline_start", {
            "goal": user_request,
            "workspace": self.workspace_dir,
            "models": self.router.get_active_routing_summary()
        })
        
        try:
            # 1. Casual Chat Branch
            if not self._is_coding_task(user_request):
                bus.post("agent_activated", {"agent": "Assistant", "model": self.planner.model})
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are DevForge AI, a friendly, ultra-capable local AI software engineering platform. "
                            "The user is greeting you or chatting casually. Reply warmly, concisely, and remind them that "
                            "they can ask you to generate full websites, APIs, or software applications with 1 click."
                        )
                    },
                    {"role": "user", "content": user_request}
                ]
                reply_tokens = []
                for token in self.client.stream_chat(self.planner.model, messages):
                    reply_tokens.append(token)
                    bus.post("token_stream", {"agent": "Assistant", "token": token})
                
                full_reply = "".join(reply_tokens)
                self.project_manager.append_message(self.workspace_dir, "Assistant", full_reply)
                bus.post("step_completed", {"agent": "Assistant", "result": full_reply})
                bus.post("pipeline_finished", {"status": "chat_completed", "workspace": self.workspace_dir})
                return

            # 2. Autonomous Full-Stack Software Generation Pipeline
            ast_context = self.get_workspace_ast_context()
            augmented_request = (
                f"{user_request}\n\n"
                f"[Project Workspace]: {self.workspace_dir}\n"
                f"{ast_context}\n"
                f"Instruction: Generate production-grade, 100% complete files (Frontend HTML, CSS styling, JS interactivity, or Python Backend)."
            )

            # Step A: Planning Phase
            bus.post("agent_activated", {"agent": "Planner", "model": self.planner.model})
            plan = self.planner.plan(augmented_request)
            self.project_manager.append_message(self.workspace_dir, "Planner", plan, {"model": self.planner.model})
            bus.post("step_completed", {"agent": "Planner", "result": plan})

            # Step B: Coding Phase (Frontend + Backend + UI)
            bus.post("agent_activated", {"agent": "Coder", "model": self.coder.model})
            code_response = self.coder.generate_code(augmented_request, plan)
            extracted_files = self.coder.extract_files(code_response)

            saved_files = []
            for fname, content in extracted_files:
                path = self.runner.write_file(fname, content)
                saved_files.append((fname, path, content))
                bus.post("file_written", {"filename": fname, "filepath": path, "content": content})

            self.project_manager.append_message(
                self.workspace_dir,
                "Coder",
                code_response,
                {"model": self.coder.model, "files": [f[0] for f in saved_files]}
            )
            bus.post("step_completed", {"agent": "Coder", "result": code_response, "files": saved_files})

            # Step C: Testing & Smoke Verification Phase
            bus.post("agent_activated", {"agent": "Tester", "model": self.tester.model})
            combined_code = "\n\n".join([f"# {f[0]}\n{f[2]}" for f in saved_files])
            test_response = self.tester.generate_tests(user_request, combined_code)
            test_files = self.coder.extract_files(test_response)

            test_filename = "test_suite.py"
            test_content = test_response
            if test_files:
                test_filename = test_files[0][0]
                test_content = test_files[0][1]

            test_path = self.runner.write_file(test_filename, test_content)
            bus.post("file_written", {"filename": test_filename, "filepath": test_path, "content": test_content})
            self.project_manager.append_message(self.workspace_dir, "Tester", test_content, {"model": self.tester.model})

            # Step D: Execute Test / Smoke Harness
            bus.post("sandbox_execution", {"message": f"⚡ Running verification test harness: {test_filename}..."})
            test_result = self.runner.execute_any(test_filename)
            bus.post("test_run_result", test_result)

            # Step E: Self-Healing Debugger Phase if failed
            if not test_result["success"]:
                bus.post("agent_activated", {"agent": "Debugger", "model": self.debugger.model})
                fix_response = self.debugger.diagnose_and_fix(
                    code=combined_code,
                    error_trace=test_result.get("stderr") or test_result.get("stdout") or "Test failed"
                )
                fixed_files = self.coder.extract_files(fix_response)
                for fname, content in fixed_files:
                    path = self.runner.write_file(fname, content)
                    bus.post("file_written", {"filename": fname, "filepath": path, "content": content})

                self.project_manager.append_message(self.workspace_dir, "Debugger", fix_response, {"model": self.debugger.model})
                retest_result = self.runner.execute_any(test_filename)
                bus.post("test_run_result", retest_result)
                bus.post("step_completed", {"agent": "Debugger", "result": fix_response})

            bus.post("pipeline_finished", {
                "status": "success",
                "workspace": self.workspace_dir,
                "file_count": len(saved_files)
            })

        except Exception as e:
            bus.post("pipeline_error", {"error": str(e)})
            bus.post("pipeline_finished", {"status": "error", "workspace": self.workspace_dir})
        finally:
            self.is_running = False
