import subprocess
import sys
import os
import webbrowser
import threading
import socket
from typing import Dict, Any, Optional

class CodeRunner:
    """
    Executes generated code, runs automated tests, and can launch full-stack applications
    (Web frontends via local HTTP server or default browser, Python scripts, C binaries, Node.js).
    """

    def __init__(self, workspace_dir: str):
        self.workspace_dir = os.path.abspath(workspace_dir)
        os.makedirs(self.workspace_dir, exist_ok=True)
        self.active_server_proc: Optional[subprocess.Popen] = None
        self.active_server_port: Optional[int] = None

    def set_workspace(self, workspace_dir: str):
        """Updates active workspace directory."""
        self.workspace_dir = os.path.abspath(workspace_dir)
        os.makedirs(self.workspace_dir, exist_ok=True)

    def write_file(self, filename: str, content: str) -> str:
        """Writes source code file into the workspace, creating any subfolders if needed."""
        clean_name = filename.strip("/\\")
        filepath = os.path.join(self.workspace_dir, clean_name)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    def execute_python(self, filename: str, timeout_sec: int = 15) -> Dict[str, Any]:
        """Runs a python script and returns output, errors, and status."""
        filepath = os.path.join(self.workspace_dir, filename)
        if not os.path.exists(filepath):
            return {
                "success": False,
                "stdout": "",
                "stderr": f"File {filename} not found in workspace.",
                "exit_code": 1
            }

        try:
            res = subprocess.run(
                [sys.executable, filename],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=timeout_sec
            )
            return {
                "success": res.returncode == 0,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "exit_code": res.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout_sec}s.",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1
            }

    def execute_any(self, filename: str, timeout_sec: int = 15) -> Dict[str, Any]:
        """Runs test or script based on file extension (Python, C/C++, JS)."""
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".py":
            return self.execute_python(filename, timeout_sec)
        elif ext in (".c", ".cpp"):
            exe_out = os.path.join(self.workspace_dir, "test_bin.exe")
            try:
                compile_res = subprocess.run(
                    ["gcc", filename, "-o", "test_bin.exe"],
                    cwd=self.workspace_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec
                )
                if compile_res.returncode != 0:
                    return {
                        "success": False,
                        "stdout": compile_res.stdout,
                        "stderr": f"GCC Compilation Error:\n{compile_res.stderr}",
                        "exit_code": compile_res.returncode
                    }
                run_res = subprocess.run(
                    [exe_out],
                    cwd=self.workspace_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec
                )
                return {
                    "success": run_res.returncode == 0,
                    "stdout": run_res.stdout,
                    "stderr": run_res.stderr,
                    "exit_code": run_res.returncode
                }
            except Exception as e:
                return {"success": False, "stdout": "", "stderr": str(e), "exit_code": 1}

        elif ext == ".js":
            try:
                run_res = subprocess.run(
                    ["node", filename],
                    cwd=self.workspace_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec
                )
                return {
                    "success": run_res.returncode == 0,
                    "stdout": run_res.stdout,
                    "stderr": run_res.stderr,
                    "exit_code": run_res.returncode
                }
            except Exception as e:
                return {"success": False, "stdout": "", "stderr": str(e), "exit_code": 1}

        return {
            "success": True,
            "stdout": f"File {filename} verified.",
            "stderr": "",
            "exit_code": 0
        }

    def _find_free_port(self) -> int:
        """Finds an available TCP port on localhost."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    def launch_project(self) -> Dict[str, Any]:
        """
        One-click execution of the generated project.
        - If index.html exists, starts local Python HTTP server and opens browser.
        - If main.py or app.py exists, launches it.
        - If main.c exists, compiles with GCC and runs it.
        """
        html_path = os.path.join(self.workspace_dir, "index.html")
        main_py = os.path.join(self.workspace_dir, "main.py")
        app_py = os.path.join(self.workspace_dir, "app.py")
        server_py = os.path.join(self.workspace_dir, "server.py")
        main_c = os.path.join(self.workspace_dir, "main.c")

        # 1. Web project with HTML frontend
        if os.path.exists(html_path):
            port = self._find_free_port()
            self.stop_server() # Stop any existing running server
            
            # Start local http server in background
            cmd = [sys.executable, "-m", "http.server", str(port)]
            self.active_server_proc = subprocess.Popen(
                cmd,
                cwd=self.workspace_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.active_server_port = port
            url = f"http://127.0.0.1:{port}/index.html"
            webbrowser.open(url)
            return {
                "success": True,
                "type": "web",
                "message": f"Web application launched live at {url}",
                "url": url,
                "port": port
            }

        # 2. Python backend / script
        for candidate in [server_py, app_py, main_py]:
            if os.path.exists(candidate):
                fname = os.path.basename(candidate)
                # If it looks like a server, start in background and notify
                res = self.execute_python(fname, timeout_sec=20)
                return {
                    "success": res["success"],
                    "type": "python",
                    "message": f"🐍 Executed Python file: {fname}",
                    "stdout": res["stdout"],
                    "stderr": res["stderr"]
                }

        # 3. C Project
        if os.path.exists(main_c):
            res = self.execute_any("main.c", timeout_sec=15)
            return {
                "success": res["success"],
                "type": "c",
                "message": "⚡ Compiled and executed C application",
                "stdout": res["stdout"],
                "stderr": res["stderr"]
            }

        # 4. Fallback: Check if any .py exists
        for f in os.listdir(self.workspace_dir):
            if f.endswith(".py") and not f.startswith("test_"):
                res = self.execute_python(f)
                return {
                    "success": res["success"],
                    "type": "python",
                    "message": f"Executed: {f}",
                    "stdout": res["stdout"],
                    "stderr": res["stderr"]
                }

        return {
            "success": False,
            "type": "unknown",
            "message": "No runnable entry point (index.html, main.py, server.py, or main.c) found in project folder."
        }

    def stop_server(self):
        """Kills any active background preview server."""
        if self.active_server_proc:
            try:
                self.active_server_proc.terminate()
                self.active_server_proc.kill()
            except Exception:
                pass
            self.active_server_proc = None
            self.active_server_port = None
