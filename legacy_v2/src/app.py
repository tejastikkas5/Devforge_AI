import os
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import config
from src.llm.ollama_client import OllamaClient
from src.core.event_bus import bus
from src.agents.supervisor import Supervisor
from src.ui.components.file_tree import FileTreeWidget

# Theme configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class DevForgeApp(ctk.CTk):
    """
    Antigravity / Codex Desktop Replica.
    Allows user to select any local folder, inspect its files, and run multi-agent
    prompts that generate, modify, and test files inside that folder in real-time.
    """
    def __init__(self):
        super().__init__()

        self.title("DevForge AI — Antigravity / Codex Local Engine")
        self.geometry("1400x880")
        self.minsize(1100, 700)

        # Active project directory
        self.active_project_dir = os.path.abspath(config.workspace_dir)

        # Core engine
        self.client = OllamaClient(config.ollama_url)
        self.supervisor = Supervisor(self.client, workspace_dir=self.active_project_dir)

        # Right panel visibility state
        self.right_panel_visible = True

        # Build 3-column UI Layout
        self._build_sidebar()
        self._build_right_inspector()
        self._build_center_chat()

        # Start periodic event consumer
        self.after(50, self._process_events)

        # Initialize model list and file tree
        self._refresh_models()
        self.file_tree.set_directory(self.active_project_dir)

    def _build_sidebar(self):
        """Left panel: Project Workspace selector, File Tree, Model selector, and Agent Status."""
        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color="#0B0F19")
        self.sidebar_frame.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar_frame.pack_propagate(False)

        # Header branding
        self.brand_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.brand_frame.pack(fill="x", padx=16, pady=(18, 10))

        self.logo_label = ctk.CTkLabel(
            self.brand_frame,
            text="⚡ DEVFORGE",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#F8FAFC"
        )
        self.logo_label.pack(side="left")

        self.badge_label = ctk.CTkLabel(
            self.brand_frame,
            text="LOCAL",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#2563EB",
            corner_radius=4,
            text_color="#FFFFFF"
        )
        self.badge_label.pack(side="left", padx=8)

        # New Session Button
        self.new_session_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="+ New Conversation",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            border_width=1,
            border_color="#475569",
            height=36,
            command=self._new_session
        )
        self.new_session_btn.pack(fill="x", padx=14, pady=(5, 12))

        # Project Workspace Selector Card
        self.proj_card = ctk.CTkFrame(self.sidebar_frame, fg_color="#161F30", corner_radius=8, border_width=1, border_color="#1E293B")
        self.proj_card.pack(fill="x", padx=14, pady=5)

        proj_top = ctk.CTkFrame(self.proj_card, fg_color="transparent")
        proj_top.pack(fill="x", padx=10, pady=(8, 4))

        self.proj_label = ctk.CTkLabel(
            proj_top,
            text="ACTIVE PROJECT",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#94A3B8"
        )
        self.proj_label.pack(side="left")

        self.choose_folder_btn = ctk.CTkButton(
            proj_top,
            text="📂 Open",
            width=65,
            height=22,
            font=ctk.CTkFont(size=11),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self._choose_folder
        )
        self.choose_folder_btn.pack(side="right")

        self.folder_name_label = ctk.CTkLabel(
            self.proj_card,
            text=os.path.basename(self.active_project_dir) or self.active_project_dir,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#38BDF8",
            anchor="w"
        )
        self.folder_name_label.pack(fill="x", padx=10, pady=(0, 2))

        self.folder_path_label = ctk.CTkLabel(
            self.proj_card,
            text=self.active_project_dir,
            font=ctk.CTkFont(size=10),
            text_color="#64748B",
            anchor="w"
        )
        self.folder_path_label.pack(fill="x", padx=10, pady=(0, 8))

        # File Tree Widget (Antigravity-style file browser)
        self.file_tree = FileTreeWidget(
            self.sidebar_frame,
            on_file_click=self._on_file_selected,
            fg_color="transparent"
        )
        self.file_tree.pack(fill="both", expand=True, padx=8, pady=5)

        # Model Selector & Ollama Status at bottom
        self.bottom_sidebar = ctk.CTkFrame(self.sidebar_frame, fg_color="#111827", corner_radius=0)
        self.bottom_sidebar.pack(fill="x", side="bottom", padx=0, pady=0)

        # Status row
        stat_row = ctk.CTkFrame(self.bottom_sidebar, fg_color="transparent")
        stat_row.pack(fill="x", padx=14, pady=(10, 4))

        self.status_dot = ctk.CTkLabel(stat_row, text="●", text_color="#10B981", font=ctk.CTkFont(size=14))
        self.status_dot.pack(side="left", padx=(0, 6))

        self.status_text = ctk.CTkLabel(stat_row, text="Ollama: Ready", font=ctk.CTkFont(size=12, weight="bold"))
        self.status_text.pack(side="left")

        self.reconnect_btn = ctk.CTkButton(
            stat_row,
            text="🔄",
            width=26,
            height=22,
            font=ctk.CTkFont(size=10),
            fg_color="#334155",
            hover_color="#475569",
            command=self._refresh_models
        )
        self.reconnect_btn.pack(side="right")

        # Model option
        self.model_option = ctk.CTkOptionMenu(
            self.bottom_sidebar,
            values=["Scanning models..."],
            command=self._on_model_changed,
            fg_color="#1E293B",
            button_color="#334155"
        )
        self.model_option.pack(fill="x", padx=14, pady=(4, 10))

    def _build_right_inspector(self):
        """Right panel: Code Viewer, Test Terminal, and Agent Graph."""
        self.right_frame = ctk.CTkFrame(self, width=420, corner_radius=0, fg_color="#0F172A")
        self.right_frame.pack(side="right", fill="y", padx=0, pady=0)
        self.right_frame.pack_propagate(False)

        # Right TabView
        self.right_tabs = ctk.CTkTabview(
            self.right_frame,
            fg_color="#161F30",
            segmented_button_selected_color="#2563EB",
            segmented_button_selected_hover_color="#1D4ED8"
        )
        self.right_tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_viewer = self.right_tabs.add("💻 Code Viewer")
        self.tab_terminal = self.right_tabs.add("📟 Output Terminal")
        self.tab_agents = self.right_tabs.add("🤖 Agents")

        # Tab 1: Code Viewer
        self.code_header = ctk.CTkLabel(
            self.tab_viewer,
            text="No file selected (Click a file in the project tree)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#94A3B8",
            anchor="w"
        )
        self.code_header.pack(fill="x", padx=8, pady=(4, 6))

        self.code_text = ctk.CTkTextbox(
            self.tab_viewer,
            wrap="none",
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#090D16",
            text_color="#38BDF8"
        )
        self.code_text.pack(fill="both", expand=True, padx=4, pady=4)

        # Tab 2: Terminal Output
        self.terminal_text = ctk.CTkTextbox(
            self.tab_terminal,
            wrap="word",
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#090D16",
            text_color="#A7F3D0"
        )
        self.terminal_text.pack(fill="both", expand=True, padx=4, pady=4)

        # Tab 3: Agent Pipeline Status Cards
        self.agent_cards = {}
        agents_info = [
            ("Planner", "Blueprint, Architecture & File Breakdown"),
            ("Coder", "Complete Code Implementation"),
            ("Tester", "Automated Python Unittest Suite"),
            ("Debugger", "Error Diagnostics & Self-Correction")
        ]

        for name, desc in agents_info:
            card = ctk.CTkFrame(self.tab_agents, fg_color="#1E293B", corner_radius=8)
            card.pack(fill="x", padx=8, pady=6)
            
            top_line = ctk.CTkFrame(card, fg_color="transparent")
            top_line.pack(fill="x", padx=10, pady=(8, 2))
            
            lbl_title = ctk.CTkLabel(top_line, text=name, font=ctk.CTkFont(size=13, weight="bold"), text_color="#F8FAFC")
            lbl_title.pack(side="left")
            
            lbl_pill = ctk.CTkLabel(top_line, text="Idle", font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748B")
            lbl_pill.pack(side="right")
            
            lbl_desc = ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=11), text_color="#94A3B8", anchor="w")
            lbl_desc.pack(fill="x", padx=10, pady=(0, 8))
            
            self.agent_cards[name] = {"card": card, "status": lbl_pill}

    def _build_center_chat(self):
        """Center panel: Breadcrumbs, Conversation cards, and Floating prompt input bar."""
        self.center_frame = ctk.CTkFrame(self, fg_color="#0B0F19", corner_radius=0)
        self.center_frame.pack(side="left", fill="both", expand=True)

        # Top breadcrumb bar
        self.top_bar = ctk.CTkFrame(self.center_frame, fg_color="#111827", height=46, corner_radius=0)
        self.top_bar.pack(fill="x", side="top")
        self.top_bar.pack_propagate(False)

        self.breadcrumb_label = ctk.CTkLabel(
            self.top_bar,
            text=f"{os.path.basename(self.active_project_dir)} / New Task",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#E2E8F0"
        )
        self.breadcrumb_label.pack(side="left", padx=20)

        self.toggle_inspector_btn = ctk.CTkButton(
            self.top_bar,
            text="◫ Toggle Inspector",
            width=120,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#1E293B",
            hover_color="#334155",
            command=self._toggle_inspector
        )
        self.toggle_inspector_btn.pack(side="right", padx=15)

        # Center Chat Area (Scrollable text cards)
        self.chat_display = ctk.CTkTextbox(
            self.center_frame,
            wrap="word",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="#090D16",
            text_color="#F1F5F9"
        )
        self.chat_display.pack(fill="both", expand=True, padx=20, pady=(15, 10))

        # Bottom Floating Prompt Bar
        self.input_card = ctk.CTkFrame(self.center_frame, fg_color="#161F30", height=85, corner_radius=12, border_width=1, border_color="#334155")
        self.input_card.pack(fill="x", padx=20, pady=(0, 20))

        self.prompt_input = ctk.CTkEntry(
            self.input_card,
            placeholder_text="Describe files or features to build in this project (e.g. 'Build a contact manager CLI with JSON save & tests')...",
            font=ctk.CTkFont(size=14),
            height=46,
            fg_color="#0B0F19",
            border_color="#1E293B"
        )
        self.prompt_input.pack(side="left", fill="x", expand=True, padx=(14, 10), pady=14)
        self.prompt_input.bind("<Return>", lambda e: self._on_submit())

        # Submit Button
        self.submit_btn = ctk.CTkButton(
            self.input_card,
            text="🚀 Run Pipeline",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            height=46,
            width=140,
            command=self._on_submit
        )
        self.submit_btn.pack(side="right", padx=(0, 14), pady=14)

    def _choose_folder(self):
        """Allows user to pick any directory on their PC as the active project workspace."""
        chosen = filedialog.askdirectory(initialdir=self.active_project_dir, title="Select Project Directory")
        if chosen:
            self.active_project_dir = os.path.abspath(chosen)
            self.supervisor.set_workspace(self.active_project_dir)
            
            # Update UI labels
            proj_name = os.path.basename(self.active_project_dir) or self.active_project_dir
            self.folder_name_label.configure(text=proj_name)
            self.folder_path_label.configure(text=self.active_project_dir)
            self.breadcrumb_label.configure(text=f"{proj_name} / Active Workspace")
            
            # Refresh File Tree
            self.file_tree.set_directory(self.active_project_dir)
            self._append_chat(f"\n📂 Switched project workspace to: {self.active_project_dir}\n")

    def _on_file_selected(self, filepath: str):
        """Called when user clicks any file in the File Tree."""
        if not os.path.isfile(filepath):
            return

        rel_path = os.path.relpath(filepath, self.active_project_dir)
        self.code_header.configure(text=f"📄 {rel_path} ({os.path.getsize(filepath)} bytes)")
        
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.code_text.delete("1.0", "end")
            self.code_text.insert("end", content)
            self.right_tabs.set("💻 Code Viewer")
        except Exception as e:
            self.code_text.delete("1.0", "end")
            self.code_text.insert("end", f"Error opening file: {e}")

    def _toggle_inspector(self):
        if self.right_panel_visible:
            self.right_frame.pack_forget()
            self.right_panel_visible = False
            self.toggle_inspector_btn.configure(text="◫ Show Inspector")
        else:
            self.right_frame.pack(side="right", fill="y", padx=0, pady=0)
            self.right_panel_visible = True
            self.toggle_inspector_btn.configure(text="◫ Hide Inspector")

    def _refresh_models(self):
        # Auto-launch Ollama background server if it was closed or offline
        if not self.client.is_alive():
            self.status_dot.configure(text_color="#F59E0B")
            self.status_text.configure(text="Ollama: Connecting...")
            self.update_idletasks()
            self.client.ensure_server_running()

        if not self.client.is_alive():
            self.status_dot.configure(text_color="#EF4444")
            self.status_text.configure(text="Ollama: Offline (Click 🔄)")
            self.model_option.configure(values=["No server running"])
            return

        self.status_dot.configure(text_color="#10B981")
        self.status_text.configure(text="Ollama: Ready")
        
        models = self.client.list_models()
        if models:
            self.model_option.configure(values=models)
            default = models[0]
            for m in models:
                if "qwen2.5-coder" in m:
                    default = m
                    break
            self.model_option.set(default)
            self._on_model_changed(default)
        else:
            self.model_option.configure(values=["No models found"])

    def _on_model_changed(self, selected_model: str):
        config.default_planner_model = selected_model
        config.default_coder_model = selected_model
        config.default_tester_model = selected_model
        config.default_debugger_model = selected_model
        if hasattr(self, 'supervisor'):
            self.supervisor.planner.model = selected_model
            self.supervisor.coder.model = selected_model
            self.supervisor.tester.model = selected_model
            self.supervisor.debugger.model = selected_model

    def _set_agent_status(self, agent_name: str, status: str):
        if agent_name in self.agent_cards:
            lbl = self.agent_cards[agent_name]["status"]
            card = self.agent_cards[agent_name]["card"]
            if status == "Active":
                lbl.configure(text="Processing...", text_color="#38BDF8")
                card.configure(fg_color="#1E3A8A")
            elif status == "Completed":
                lbl.configure(text="Done ✔", text_color="#10B981")
                card.configure(fg_color="#064E3B")
            elif status == "Failed":
                lbl.configure(text="Failed ✖", text_color="#EF4444")
                card.configure(fg_color="#7F1D1D")
            else:
                lbl.configure(text="Idle", text_color="#64748B")
                card.configure(fg_color="#1E293B")

    def _append_chat(self, text: str):
        self.chat_display.insert("end", text)
        self.chat_display.see("end")

    def _new_session(self):
        self.chat_display.delete("1.0", "end")
        self.code_text.delete("1.0", "end")
        self.terminal_text.delete("1.0", "end")
        for name in self.agent_cards:
            self._set_agent_status(name, "Idle")
        self.breadcrumb_label.configure(text=f"{os.path.basename(self.active_project_dir)} / New Task")
        self._append_chat(f"🚀 New Conversation started. Target workspace: {self.active_project_dir}\n")

    def _on_submit(self):
        prompt = self.prompt_input.get().strip()
        if not prompt or self.supervisor.is_running:
            return

        self.prompt_input.delete(0, "end")
        self.submit_btn.configure(state="disabled", text="Running...")
        self.breadcrumb_label.configure(text=f"{os.path.basename(self.active_project_dir)} / {prompt[:25]}...")

        for name in self.agent_cards:
            self._set_agent_status(name, "Idle")

        self._append_chat(f"\n👤 USER: {prompt}\n")
        self._append_chat("=" * 65 + "\n")

        self.supervisor.start_pipeline_async(prompt)

    def _process_events(self):
        """Consumes events from background agent threads."""
        events = bus.poll(max_items=30)
        for event_type, data in events:
            if event_type == "agent_activated":
                agent = data["agent"]
                if agent in self.agent_cards:
                    self._set_agent_status(agent, "Active")
                    self._append_chat(f"\n▶ [{agent.upper()} AGENT ACTIVATED]\n")
                else:
                    self._append_chat(f"\n🤖 {agent}:\n")

            elif event_type == "token_stream":
                self._append_chat(data["token"])

            elif event_type == "step_completed":
                agent = data["agent"]
                self._set_agent_status(agent, "Completed")
                self._append_chat(f"\n✔ [{agent.upper()} COMPLETED]\n\n")

            elif event_type == "file_written":
                fname = data["filename"]
                fpath = data.get("filepath", "")
                content = data["content"]
                self._append_chat(f"📝 [FILE CREATED/UPDATED]: {fname}\n")
                
                # Show in code viewer
                self.code_header.configure(text=f"📄 {fname}")
                self.code_text.delete("1.0", "end")
                self.code_text.insert("end", content)
                
                # Refresh file tree so the user sees it immediately
                self.file_tree.refresh()

            elif event_type == "sandbox_execution":
                msg = data["message"]
                self.terminal_text.insert("end", f"{msg}\n")
                self.terminal_text.see("end")

            elif event_type == "test_run_result":
                res = data
                status = "PASSED ✅" if res["success"] else "FAILED ❌"
                self.terminal_text.insert("end", f"\n--- Test Execution: {status} (Code: {res['exit_code']}) ---\n")
                if res["stdout"]:
                    self.terminal_text.insert("end", f"[STDOUT]:\n{res['stdout']}\n")
                if res["stderr"]:
                    self.terminal_text.insert("end", f"[STDERR]:\n{res['stderr']}\n")
                self.terminal_text.see("end")
                self.right_tabs.set("📟 Output Terminal")

            elif event_type == "pipeline_finished":
                self.submit_btn.configure(state="normal", text="🚀 Run Pipeline")
                self._append_chat(f"\n🎉 [COMPLETE] Files saved to: {data.get('workspace')}\n")
                self.file_tree.refresh()

            elif event_type == "pipeline_error":
                self.submit_btn.configure(state="normal", text="🚀 Run Pipeline")
                self._append_chat(f"\n❌ [ERROR]: {data['error']}\n")

        self.after(50, self._process_events)

def main():
    app = DevForgeApp()
    app.mainloop()

if __name__ == "__main__":
    main()
