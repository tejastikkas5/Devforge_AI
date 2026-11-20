import os
import sys
import threading
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, Signal, Slot, QDir
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QPlainTextEdit, QTabWidget,
    QFileDialog, QTreeView, QFileSystemModel, QListWidget, QListWidgetItem,
    QFrame, QInputDialog, QMessageBox
)

from config.settings import config
from src.llm.ollama_client import OllamaClient
from src.agents.supervisor import Supervisor
from src.core.event_bus import bus
from src.core.project_manager import ProjectManager

# High-Performance Deep Dark Navy Theme
ANTIGRAVITY_STYLESHEET = """
QMainWindow {
    background-color: #070A10;
}
QWidget {
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
    color: #F1F5F9;
}
/* Splitter Handles */
QSplitter::handle {
    background-color: #161F30;
}
QSplitter::handle:hover {
    background-color: #2563EB;
}
/* Sidebar Panel */
#SidebarFrame {
    background-color: #0A0E17;
    border-right: 1px solid #161F30;
}
#BrandLabel {
    font-size: 17px;
    font-weight: 800;
    color: #FFFFFF;
}
#BrandBadge {
    background-color: #2563EB;
    color: #FFFFFF;
    font-size: 9px;
    font-weight: 800;
    padding: 3px 6px;
    border-radius: 4px;
}
#NewProjectBtn {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 700;
    padding: 9px 12px;
}
#NewProjectBtn:hover {
    background-color: #1D4ED8;
}
/* Projects List */
QListWidget {
    background-color: #0B111E;
    border: 1px solid #161F30;
    border-radius: 6px;
    padding: 4px;
    color: #E2E8F0;
    font-size: 12px;
}
QListWidget::item {
    padding: 8px 10px;
    border-radius: 4px;
    margin-bottom: 2px;
}
QListWidget::item:hover {
    background-color: #161F30;
    color: #38BDF8;
}
QListWidget::item:selected {
    background-color: #1E3A8A;
    color: #FFFFFF;
    font-weight: bold;
}
/* Center Frame */
#CenterFrame {
    background-color: #070A10;
}
#TopBar {
    background-color: #0A0E17;
    border-bottom: 1px solid #161F30;
}
#BreadcrumbLabel {
    font-size: 13px;
    font-weight: 700;
    color: #38BDF8;
}
#LaunchProjectBtn {
    background-color: #10B981;
    color: #FFFFFF;
    font-size: 12px;
    font-weight: 800;
    border: none;
    border-radius: 6px;
    padding: 7px 16px;
}
#LaunchProjectBtn:hover {
    background-color: #059669;
}
#InputCard {
    background-color: #0E1524;
    border: 1px solid #1E293B;
    border-radius: 10px;
}
#PromptInput {
    background-color: transparent;
    color: #FFFFFF;
    border: none;
    font-size: 13px;
}
#RunBtn {
    background-color: #2563EB;
    color: #FFFFFF;
    font-size: 13px;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 10px 22px;
}
#RunBtn:hover {
    background-color: #1D4ED8;
}
#RunBtn:disabled {
    background-color: #334155;
    color: #64748B;
}
/* Right TabView & Monospace Inspector */
QTabWidget::pane {
    border: 1px solid #161F30;
    background-color: #070A10;
    border-radius: 6px;
}
QTabBar::tab {
    background-color: #0E1524;
    color: #94A3B8;
    padding: 8px 14px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-size: 11px;
    font-weight: bold;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #2563EB;
    color: #FFFFFF;
}
QPlainTextEdit {
    background-color: #05070B;
    color: #38BDF8;
    border: none;
    font-family: 'Consolas', 'Fira Code', monospace;
    font-size: 12px;
    line-height: 1.4;
    padding: 10px;
}
QScrollBar:vertical {
    background: #0A0E17;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #1E293B;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #334155;
}
"""

class EventBridge(QtCore.QObject):
    """Thread-safe event bridge delivering backend events to Qt UI thread."""
    event_received = Signal(str, object)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DevForge AI — Autonomous Full-Stack Software Engine")
        self.resize(1480, 920)
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(ANTIGRAVITY_STYLESHEET)

        # Project manager & client
        self.project_manager = ProjectManager(config.workspace_dir)
        self.client = OllamaClient(config.ollama_url)

        # Get or create initial active project
        projects = self.project_manager.list_projects()
        if projects:
            self.active_project = projects[0]
        else:
            self.active_project = self.project_manager.create_project("Initial Web Project")

        self.active_project_dir = self.active_project["path"]

        # Core autonomous supervisor
        self.supervisor = Supervisor(self.client, workspace_dir=self.active_project_dir)

        # Event bridge
        self.bridge = EventBridge()
        self.bridge.event_received.connect(self._handle_event)

        # Build 3-Panel Splitter UI
        self._build_ui()

        # Start background event bus listener thread
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._event_monitor_loop, daemon=True)
        self.monitor_thread.start()

        # Load initial state
        self._refresh_projects_list()
        self._load_active_project()

    def _build_ui(self):
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.main_splitter)

        # 1. Left Sidebar (Projects & Files)
        self.sidebar_widget = self._create_sidebar()
        self.main_splitter.addWidget(self.sidebar_widget)

        # 2. Center Chat & Generation View
        self.center_widget = self._create_center()
        self.main_splitter.addWidget(self.center_widget)

        # 3. Right Inspector (Code, Terminal, Active Agents)
        self.right_widget = self._create_inspector()
        self.main_splitter.addWidget(self.right_widget)

        # Set initial splitter widths: 280px | 760px | 440px
        self.main_splitter.setSizes([280, 760, 440])
        self.main_splitter.setCollapsible(0, False)
        self.main_splitter.setCollapsible(1, False)

    def _create_sidebar(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("SidebarFrame")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 16, 14, 14)
        layout.setSpacing(10)

        # Top Branding
        brand_row = QHBoxLayout()
        logo = QLabel("⚡ DEVFORGE AI")
        logo.setObjectName("BrandLabel")
        badge = QLabel("AUTONOMOUS")
        badge.setObjectName("BrandBadge")
        brand_row.addWidget(logo)
        brand_row.addWidget(badge)
        brand_row.addStretch()
        layout.addLayout(brand_row)

        # + New Project Folder Button
        self.btn_new_project = QPushButton("➕ New Project Folder")
        self.btn_new_project.setObjectName("NewProjectBtn")
        self.btn_new_project.setCursor(Qt.PointingHandCursor)
        self.btn_new_project.clicked.connect(self._create_new_project_dialog)
        layout.addWidget(self.btn_new_project)

        # Projects Section Header
        p_header = QHBoxLayout()
        p_lbl = QLabel("PROJECTS / SESSIONS")
        p_lbl.setStyleSheet("font-size: 10px; font-weight: bold; color: #94A3B8;")
        p_header.addWidget(p_lbl)
        p_header.addStretch()
        btn_refresh_p = QPushButton("🔄")
        btn_refresh_p.setFixedSize(22, 18)
        btn_refresh_p.setStyleSheet("background: transparent; color: #94A3B8; border: none;")
        btn_refresh_p.setCursor(Qt.PointingHandCursor)
        btn_refresh_p.clicked.connect(self._refresh_projects_list)
        p_header.addWidget(btn_refresh_p)
        layout.addLayout(p_header)

        # List of Projects
        self.projects_list = QListWidget()
        self.projects_list.setFixedHeight(150)
        self.projects_list.itemClicked.connect(self._on_project_selected)
        layout.addWidget(self.projects_list)

        # Project Files Tree Header
        f_header = QHBoxLayout()
        f_lbl = QLabel("PROJECT FILES")
        f_lbl.setStyleSheet("font-size: 10px; font-weight: bold; color: #94A3B8;")
        f_header.addWidget(f_lbl)
        f_header.addStretch()
        btn_refresh_tree = QPushButton("🔄")
        btn_refresh_tree.setFixedSize(22, 18)
        btn_refresh_tree.setStyleSheet("background: transparent; color: #94A3B8; border: none;")
        btn_refresh_tree.setCursor(Qt.PointingHandCursor)
        btn_refresh_tree.clicked.connect(self._refresh_file_tree)
        f_header.addWidget(btn_refresh_tree)
        layout.addLayout(f_header)

        # Native OS File Tree
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(self.active_project_dir)
        self.file_model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(self.active_project_dir))
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)
        self.tree_view.header().hide()
        self.tree_view.clicked.connect(self._on_file_clicked)
        layout.addWidget(self.tree_view, 1)

        # Bottom System Status (Informational only — no dropdowns for user)
        bot_frame = QFrame()
        bot_layout = QVBoxLayout(bot_frame)
        bot_layout.setContentsMargins(0, 0, 0, 0)
        bot_layout.setSpacing(4)

        stat_row = QHBoxLayout()
        self.stat_dot = QLabel("●")
        self.stat_dot.setStyleSheet("color: #10B981; font-size: 13px;")
        self.stat_text = QLabel("Autonomous Router: Active")
        self.stat_text.setStyleSheet("font-size: 11px; font-weight: bold; color: #94A3B8;")
        stat_row.addWidget(self.stat_dot)
        stat_row.addWidget(self.stat_text)
        stat_row.addStretch()
        bot_layout.addLayout(stat_row)

        self.lbl_active_models = QLabel("Backend: Specialized Multi-Model Mesh")
        self.lbl_active_models.setStyleSheet("font-size: 10px; color: #64748B;")
        bot_layout.addWidget(self.lbl_active_models)

        layout.addWidget(bot_frame)
        return panel

    def _create_center(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("CenterFrame")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(10)

        # Top Bar with Project Breadcrumb & Run Project Action
        top_bar = QFrame()
        top_bar.setObjectName("TopBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 10, 16, 10)

        self.lbl_breadcrumb = QLabel(f"📁 {self.active_project.get('title', 'Project')}")
        self.lbl_breadcrumb.setObjectName("BreadcrumbLabel")
        top_layout.addWidget(self.lbl_breadcrumb)
        top_layout.addStretch()

        # ONE-CLICK RUN PROJECT BUTTON
        self.btn_launch_app = QPushButton("▶ Run Project")
        self.btn_launch_app.setObjectName("LaunchProjectBtn")
        self.btn_launch_app.setCursor(Qt.PointingHandCursor)
        self.btn_launch_app.clicked.connect(self._launch_current_project)
        top_layout.addWidget(self.btn_launch_app)

        self.btn_toggle_inspector = QPushButton("◫ Inspector")
        self.btn_toggle_inspector.setStyleSheet("""
            background-color: #161F30; color: #94A3B8; border: 1px solid #334155;
            border-radius: 6px; font-size: 11px; font-weight: bold; padding: 7px 12px;
        """)
        self.btn_toggle_inspector.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_inspector.clicked.connect(self._toggle_inspector)
        top_layout.addWidget(self.btn_toggle_inspector)

        layout.addWidget(top_bar)

        # Center Conversation Feed
        self.chat_display = QPlainTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QPlainTextEdit {
                background-color: #070A10;
                color: #F8FAFC;
                border: none;
                font-size: 13px;
                line-height: 1.5;
                padding: 16px;
            }
        """)
        layout.addWidget(self.chat_display, 1)

        # Floating Bottom Input Card
        input_container = QWidget()
        in_wrap = QHBoxLayout(input_container)
        in_wrap.setContentsMargins(16, 0, 16, 0)

        input_card = QFrame()
        input_card.setObjectName("InputCard")
        card_layout = QHBoxLayout(input_card)
        card_layout.setContentsMargins(12, 8, 12, 8)
        card_layout.setSpacing(10)

        self.prompt_input = QTextEdit()
        self.prompt_input.setObjectName("PromptInput")
        self.prompt_input.setPlaceholderText(
            "Give your prompt (e.g. 'Generate a modern portfolio website with dark mode, project cards, and working contact form')..."
        )
        self.prompt_input.setFixedHeight(56)
        card_layout.addWidget(self.prompt_input)

        self.btn_run = QPushButton("⚡ Generate Project")
        self.btn_run.setObjectName("RunBtn")
        self.btn_run.setFixedHeight(56)
        self.btn_run.setCursor(Qt.PointingHandCursor)
        self.btn_run.clicked.connect(self._on_submit)
        card_layout.addWidget(self.btn_run)

        in_wrap.addWidget(input_card)
        layout.addWidget(input_container)

        return panel

    def _create_inspector(self) -> QWidget:
        panel = QFrame()
        panel.setStyleSheet("background-color: #0A0E17; border-left: 1px solid #161F30;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.tabs = QTabWidget()

        # Tab 1: Code Viewer
        tab_code = QWidget()
        c_layout = QVBoxLayout(tab_code)
        c_layout.setContentsMargins(0, 6, 0, 0)
        self.lbl_code_file = QLabel("No file selected")
        self.lbl_code_file.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: bold; padding: 4px;")
        c_layout.addWidget(self.lbl_code_file)

        self.code_viewer = QPlainTextEdit()
        self.code_viewer.setReadOnly(True)
        c_layout.addWidget(self.code_viewer)
        self.tabs.addTab(tab_code, "💻 Code Viewer")

        # Tab 2: Terminal Output
        tab_term = QWidget()
        t_layout = QVBoxLayout(tab_term)
        t_layout.setContentsMargins(0, 6, 0, 0)
        self.terminal_view = QPlainTextEdit()
        self.terminal_view.setReadOnly(True)
        self.terminal_view.setStyleSheet("background-color: #05070B; color: #A7F3D0;")
        t_layout.addWidget(self.terminal_view)
        self.tabs.addTab(tab_term, "📟 Output Terminal")

        # Tab 3: Specialized Agent Cards
        tab_agents = QWidget()
        a_layout = QVBoxLayout(tab_agents)
        a_layout.setContentsMargins(0, 8, 0, 0)
        a_layout.setSpacing(8)

        self.agent_labels = {}
        agents_info = [
            ("Planner", "Architecture & Decomposition"),
            ("Coder", "Frontend + Backend Implementation"),
            ("Tester", "Automated QA & Verification"),
            ("Debugger", "Diagnosis & Autonomous Healing")
        ]

        for name, desc in agents_info:
            card = QFrame()
            card.setStyleSheet("background-color: #111827; border: 1px solid #1E293B; border-radius: 6px; padding: 6px;")
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(8, 6, 8, 6)

            top = QHBoxLayout()
            lbl_n = QLabel(name)
            lbl_n.setStyleSheet("font-weight: bold; font-size: 12px; color: #F1F5F9;")
            lbl_s = QLabel("Idle")
            lbl_s.setStyleSheet("color: #64748B; font-size: 11px; font-weight: bold;")
            top.addWidget(lbl_n)
            top.addStretch()
            top.addWidget(lbl_s)
            c_lay.addLayout(top)

            lbl_d = QLabel(desc)
            lbl_d.setStyleSheet("color: #94A3B8; font-size: 10px;")
            c_lay.addWidget(lbl_d)

            a_layout.addWidget(card)
            self.agent_labels[name] = {"card": card, "status": lbl_s}

        a_layout.addStretch()
        self.tabs.addTab(tab_agents, "🤖 Active Agents")

        layout.addWidget(self.tabs)
        return panel

    def _refresh_projects_list(self):
        """Scans workspace and refreshes project list."""
        self.projects_list.clear()
        projects = self.project_manager.list_projects()
        selected_row = 0
        for i, proj in enumerate(projects):
            item = QListWidgetItem(f"📁 {proj['title']}")
            item.setData(Qt.UserRole, proj)
            self.projects_list.addItem(item)
            if proj["path"] == self.active_project_dir:
                selected_row = i

        if self.projects_list.count() > 0:
            self.projects_list.setCurrentRow(selected_row)

    def _create_new_project_dialog(self):
        """Creates a brand new dedicated project folder."""
        text, ok = QInputDialog.getText(self, "New Project", "Enter project name (e.g. 'Coffee Shop Website'):")
        if ok and text.strip():
            new_proj = self.project_manager.create_project(text.strip())
            self.active_project = new_proj
            self.active_project_dir = new_proj["path"]
            self.supervisor.set_workspace(self.active_project_dir)
            self._refresh_projects_list()
            self._load_active_project()

    def _on_project_selected(self, item: QListWidgetItem):
        proj = item.data(Qt.UserRole)
        if proj and proj["path"] != self.active_project_dir:
            self.active_project = proj
            self.active_project_dir = proj["path"]
            self.supervisor.set_workspace(self.active_project_dir)
            self._load_active_project()

    def _load_active_project(self):
        """Loads conversation history and files for current project folder."""
        title = self.active_project.get("title", os.path.basename(self.active_project_dir))
        self.lbl_breadcrumb.setText(f"📁 {title}")
        self._refresh_file_tree()

        # Load persisted conversation history
        self.chat_display.clear()
        messages = self.project_manager.load_history(self.active_project_dir)
        if messages:
            self._append_chat(f"📂 [PROJECT LOADED]: {title}\n" + "=" * 65 + "\n")
            for msg in messages:
                sender = msg.get("sender", "System")
                text = msg.get("text", "")
                if sender == "USER":
                    self._append_chat(f"\n👤 USER: {text}\n" + "-" * 50 + "\n")
                elif sender == "Planner":
                    self._append_chat(f"\n📋 [PLANNER BLUEPRINT]:\n{text}\n")
                elif sender == "Coder":
                    files = msg.get("metadata", {}).get("files", [])
                    self._append_chat(f"\n💻 [CODER IMPLEMENTED {len(files)} FILES]:\n{', '.join(files)}\n")
                elif sender == "Tester":
                    self._append_chat(f"\n🧪 [TEST SUITE VERIFIED]\n")
                elif sender == "Debugger":
                    self._append_chat(f"\n🔧 [DEBUGGER HEALED ISSUE]\n")
                else:
                    self._append_chat(f"\n🤖 {sender}: {text}\n")
        else:
            self._append_chat(f"🚀 Project '{title}' ready.\nEnter your prompt below to generate full frontend, backend, and UI.\n")

    def _refresh_file_tree(self):
        self.file_model.setRootPath(self.active_project_dir)
        self.tree_view.setRootIndex(self.file_model.index(self.active_project_dir))

    def _on_file_clicked(self, index):
        filepath = self.file_model.filePath(index)
        if os.path.isfile(filepath):
            rel_name = os.path.relpath(filepath, self.active_project_dir)
            self.lbl_code_file.setText(f"📄 {rel_name} ({os.path.getsize(filepath)} bytes)")
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                self.code_viewer.setPlainText(content)
                self.tabs.setCurrentIndex(0)
            except Exception as e:
                self.code_viewer.setPlainText(f"Error reading file: {e}")

    def _launch_current_project(self):
        """Direct 1-click execution of the generated application."""
        self.terminal_view.appendPlainText("\n🚀 [LAUNCHING PROJECT] Inspecting entry points...\n")
        res = self.supervisor.runner.launch_project()
        if res["success"]:
            self.terminal_view.appendPlainText(f"✅ {res['message']}\n")
            if res.get("stdout"):
                self.terminal_view.appendPlainText(f"[STDOUT]:\n{res['stdout']}\n")
            self.tabs.setCurrentIndex(1)
        else:
            self.terminal_view.appendPlainText(f"⚠️ {res['message']}\n")
            if res.get("stderr"):
                self.terminal_view.appendPlainText(f"[STDERR]:\n{res['stderr']}\n")
            QMessageBox.information(self, "Run Project", res["message"])

    def _toggle_inspector(self):
        is_visible = self.right_widget.isVisible()
        self.right_widget.setVisible(not is_visible)
        self.btn_toggle_inspector.setText("◫ Show Inspector" if is_visible else "◫ Hide Inspector")

    def _set_agent_status(self, agent_name: str, status: str):
        if agent_name in self.agent_labels:
            lbl = self.agent_labels[agent_name]["status"]
            card = self.agent_labels[agent_name]["card"]
            if status == "Active":
                lbl.setText("Running...")
                lbl.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: bold;")
                card.setStyleSheet("background-color: #1E3A8A; border: 1px solid #2563EB; border-radius: 6px;")
            elif status == "Completed":
                lbl.setText("Done ✔")
                lbl.setStyleSheet("color: #10B981; font-size: 11px; font-weight: bold;")
                card.setStyleSheet("background-color: #064E3B; border: 1px solid #059669; border-radius: 6px;")
            elif status == "Failed":
                lbl.setText("Failed ✖")
                lbl.setStyleSheet("color: #EF4444; font-size: 11px; font-weight: bold;")
                card.setStyleSheet("background-color: #7F1D1D; border: 1px solid #DC2626; border-radius: 6px;")
            else:
                lbl.setText("Idle")
                lbl.setStyleSheet("color: #64748B; font-size: 11px; font-weight: bold;")
                card.setStyleSheet("background-color: #111827; border: 1px solid #1E293B; border-radius: 6px;")

    def _append_chat(self, text: str):
        self.chat_display.moveCursor(QtGui.QTextCursor.End)
        self.chat_display.insertPlainText(text)
        self.chat_display.moveCursor(QtGui.QTextCursor.End)

    def _on_submit(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt or self.supervisor.is_running:
            return

        self.prompt_input.clear()
        self.btn_run.setEnabled(False)
        self.btn_run.setText("⚡ Generating...")

        for name in self.agent_labels:
            self._set_agent_status(name, "Idle")

        self._append_chat(f"\n👤 USER: {prompt}\n" + "=" * 65 + "\n")
        self.supervisor.start_pipeline_async(prompt)

    def _event_monitor_loop(self):
        """Monitors EventBus in background and fires Qt Signals."""
        while self.is_monitoring:
            events = bus.poll(max_items=25)
            for ev_type, data in events:
                self.bridge.event_received.emit(ev_type, data)
            QtCore.QThread.msleep(40)

    @Slot(str, object)
    def _handle_event(self, event_type: str, data: object):
        if event_type == "pipeline_start":
            models = data.get("models", {})
            model_strs = [f"{role}: {m}" for role, m in models.items()]
            self.lbl_active_models.setText(" • ".join(model_strs[:2]))

        elif event_type == "agent_activated":
            agent = data["agent"]
            model = data.get("model", "")
            if agent in self.agent_labels:
                self._set_agent_status(agent, "Active")
                self._append_chat(f"\n▶ [{agent.upper()} AGENT ACTIVATED | Model: {model}]\n")
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
            content = data["content"]
            self._append_chat(f"📝 [FILE CREATED]: {fname}\n")
            self.lbl_code_file.setText(f"📄 {fname}")
            self.code_viewer.setPlainText(content)
            self._refresh_file_tree()
            self.tabs.setCurrentIndex(0)

        elif event_type == "sandbox_execution":
            self.terminal_view.appendPlainText(f"{data['message']}")

        elif event_type == "test_run_result":
            res = data
            status = "PASSED ✅" if res.get("success") else "FAILED ❌"
            self.terminal_view.appendPlainText(f"\n--- Verification Harness: {status} ---\n")
            if res.get("stdout"):
                self.terminal_view.appendPlainText(f"[STDOUT]:\n{res['stdout']}\n")
            if res.get("stderr"):
                self.terminal_view.appendPlainText(f"[STDERR]:\n{res['stderr']}\n")
            self.tabs.setCurrentIndex(1)

        elif event_type == "pipeline_finished":
            self.btn_run.setEnabled(True)
            self.btn_run.setText("⚡ Generate Project")
            file_count = data.get("file_count", 0)
            self._append_chat(f"\n🎉 [GENERATION COMPLETE] {file_count} files saved in project folder.\n")
            self._append_chat("💡 Click the green '▶ Run Project' button in the top bar to launch your application live!\n")
            self._refresh_projects_list()
            self._refresh_file_tree()

        elif event_type == "pipeline_error":
            self.btn_run.setEnabled(True)
            self.btn_run.setText("⚡ Generate Project")
            self._append_chat(f"\n❌ [ERROR]: {data.get('error')}\n")

def run():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
