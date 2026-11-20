"""Simple PySide6 desktop UI: folder sidebar, Chat/Code switch, chat view and a code panel."""
import html
import os
import sys
import threading
import traceback
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional

import markdown
from PySide6.QtCore import QDir, QProcess, QSize, QSortFilterProxyModel, Qt, QThread, QTimer, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QFont, QKeyEvent
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QFileDialog, QFileSystemModel, QHBoxLayout, QInputDialog,
                               QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMenu, QMessageBox, QPlainTextEdit, QPushButton, QSplitter,
                               QTextBrowser, QToolButton, QTreeView, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
                               QWidget)

from devforge import __version__, config, fsops
from devforge.engine import Cancelled, Engine
from devforge.llm import OllamaClient, OllamaError
from devforge.memory import MAX_NOTES, MemoryStore
from devforge.skills import MAX_INJECT_CHARS, SkillError, SkillStore
from devforge.store import ProjectStore, add_recent, load_recent, remove_recent

STYLE = """
* { font-family: 'Segoe UI', sans-serif; font-size: 10pt; color: #e6e9ef; }
QMainWindow, QWidget#root { background: #0f1218; }
QWidget#sidebar { background: #0b0e13; }
QLabel#brand { font-size: 14pt; font-weight: 600; padding: 4px 2px; }
QLabel#muted { color: #8b93a5; }
QTreeWidget { background: transparent; border: none; outline: none; }
QTreeWidget::item { padding: 5px 4px; border-radius: 6px; color: #c6ccd8; }
QTreeWidget::item:selected { background: #1b2433; color: white; }
QTreeWidget::item:hover { background: #151b26; }
QListWidget { background: transparent; border: none; outline: none; }
QListWidget::item { padding: 8px 10px; border-radius: 6px; color: #c6ccd8; }
QListWidget::item:selected { background: #1b2433; color: white; }
QListWidget::item:hover { background: #151b26; }
QPushButton { background: #1a2030; border: 1px solid #262e42; border-radius: 6px; padding: 7px 14px; }
QPushButton:hover { background: #222a3d; }
QPushButton:disabled { color: #5b6477; background: #141925; }
QPushButton#primary { background: #2563eb; border: none; font-weight: 600; }
QPushButton#primary:hover { background: #3b74f0; }
QPushButton#danger { background: #b42318; border: none; font-weight: 600; }
QPushButton#tab { background: transparent; border: none; border-bottom: 2px solid transparent; border-radius: 0;
                  padding: 8px 16px; color: #8b93a5; font-weight: 600; }
QPushButton#tab:checked { color: white; border-bottom: 2px solid #3b82f6; }
QPushButton#tab:hover:!checked { color: #c6ccd8; }
QTextBrowser, QPlainTextEdit { background: #0f1218; border: none; selection-background-color: #264a8f; }
QDialog { background: #0f1218; }
QLineEdit { background: #151a23; border: 1px solid #262e42; border-radius: 8px; padding: 7px 10px; }
QLineEdit:focus { border: 1px solid #3b82f6; }
QPlainTextEdit#skilltext { background: #151a23; border: 1px solid #262e42; border-radius: 8px; padding: 8px; }
QPlainTextEdit#skilltext:focus { border: 1px solid #3b82f6; }
QPlainTextEdit#input { background: #151a23; border: 1px solid #262e42; border-radius: 10px; padding: 8px; }
QPlainTextEdit#input:focus { border: 1px solid #3b82f6; }
QPlainTextEdit#code, QPlainTextEdit#output { background: #0b0e13; font-family: Consolas, 'Cascadia Mono', monospace; }
QTreeView { background: #0b0e13; border: none; outline: none; }
QTreeView::item { padding: 3px; }
QTreeView::item:selected { background: #1b2433; }
QSplitter::handle { background: #1a2030; }
QSplitter::handle:horizontal { width: 2px; }
QSplitter::handle:vertical { height: 2px; }
QScrollBar:vertical { background: transparent; width: 10px; }
QScrollBar::handle:vertical { background: #2a3347; border-radius: 5px; min-height: 30px; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; width: 0; }
QScrollBar:horizontal { background: transparent; height: 10px; }
QScrollBar::handle:horizontal { background: #2a3347; border-radius: 5px; }
"""

DOC_CSS = """
body { color: #e6e9ef; font-family: 'Segoe UI'; font-size: 10pt; }
p { margin: 4px 0; } li { margin: 2px 0; }
pre { background-color: #0b0e13; color: #d6deeb; padding: 8px; font-family: Consolas, monospace; font-size: 9.5pt; }
code { background-color: #0b0e13; color: #9ecbff; font-family: Consolas, monospace; }
a { color: #6ea8ff; } th, td { padding: 4px 8px; border: 1px solid #2a3347; }
h1, h2, h3 { color: #ffffff; }
"""


def md(text: str) -> str:
    return markdown.markdown(text, extensions=["fenced_code", "tables", "sane_lists", "nl2br"])


# ---------------------------------------------------------------- worker thread
class Worker(QThread):
    event = Signal(str, dict)
    failed = Signal(str)

    def __init__(self, engine: Engine, mode: str, text: str, sid: Optional[str] = None):
        super().__init__()
        self.engine, self.mode, self.text, self.sid = engine, mode, text, sid
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        self.engine.emit = lambda kind, **kw: self.event.emit(kind, kw)
        self.engine._cancel = lambda: self._stop
        try:
            (self.engine.handle_chat if self.mode == "chat" else self.engine.handle_code)(self.text, self.sid)
        except Cancelled:
            self.event.emit("cancelled", {})
        except OllamaError as e:
            self.failed.emit(str(e))
        except Exception:       # noqa: BLE001 - surface any bug in the UI instead of dying silently
            self.failed.emit("Unexpected error:\n" + traceback.format_exc(limit=6))


class Job:
    """One running prompt. Many can exist at once (one per chat); the UI shows the selected chat's job."""
    _seq = 0

    def __init__(self, root: str, mode: str, text: str, sid: Optional[str]):
        Job._seq += 1
        self.id = Job._seq
        self.root, self.mode, self.text, self.sid = root, mode, text, sid
        self.progress: List[str] = []
        self.live: Optional[str] = "" if mode == "chat" else None
        self.line = -1
        self.worker: Optional[Worker] = None
        self.stopped = False
        self.failed = False

    def running(self) -> bool:
        return self.worker is not None and self.worker.isRunning()


def _same(a: Optional[str], b: Optional[str]) -> bool:
    return bool(a) and bool(b) and os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


# ---------------------------------------------------------------- widgets
class PromptEdit(QPlainTextEdit):
    submitted = Signal()

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter) and not (e.modifiers() & Qt.ShiftModifier):
            self.submitted.emit()
            return
        super().keyPressEvent(e)


class HideProxy(QSortFilterProxyModel):
    HIDDEN = {config.STATE_DIRNAME, "__pycache__", "node_modules", ".git", ".venv"}

    def filterAcceptsRow(self, row, parent):
        idx = self.sourceModel().index(row, 0, parent)
        return self.sourceModel().fileName(idx) not in self.HIDDEN


class ChatView(QTextBrowser):
    def __init__(self):
        super().__init__()
        self.setOpenExternalLinks(True)
        self.document().setDefaultStyleSheet(DOC_CSS)
        self.messages: List[Dict] = []
        self.progress: List[str] = []
        self.live: Optional[str] = None
        self.placeholder = ""
        self._dirty = False
        self._timer = QTimer(self)
        self._timer.setInterval(120)
        self._timer.timeout.connect(self._flush)
        self._timer.start()

    def refresh(self):
        self._dirty = True

    def _bubble(self, who: str, body_html: str, user: bool) -> str:
        bg, label = ("#1e3a8a", "You") if user else ("#161c28", who)
        align = "right" if user else "left"
        width = "80%" if user else "96%"
        return (f'<table align="{align}" width="{width}" cellspacing="0" cellpadding="10" style="margin-bottom:10px">'
                f'<tr><td bgcolor="{bg}"><span style="color:#8fb4ff;font-size:8.5pt"><b>{html.escape(label)}</b></span><br>'
                f'{body_html}</td></tr></table><br clear="all">')

    def _flush(self):
        if not self._dirty:
            return
        self._dirty = False
        bar = self.verticalScrollBar()
        at_bottom = bar.value() >= bar.maximum() - 40
        old = bar.value()
        parts = []
        if not self.messages and not self.progress and self.live is None:
            parts.append(f'<div style="color:#8b93a5;margin-top:60px;text-align:center">{self.placeholder}</div>')
        for m in self.messages:
            if m["role"] == "user":
                parts.append(self._bubble("You", html.escape(m["content"]).replace("\n", "<br>"), True))
            else:
                parts.append(self._bubble("DevForge", md(m["content"]), False))
        if self.live is not None:
            parts.append(self._bubble("DevForge", md(self.live) if self.live else "<i>...</i>", False))
        if self.progress:
            rows = "<br>".join(self.progress)
            parts.append(f'<table width="96%" cellpadding="8"><tr><td bgcolor="#121722" style="color:#9aa4b8">{rows}</td></tr></table>')
        self.setHtml("".join(parts))
        bar.setValue(bar.maximum() if at_bottom else old)


# ---------------------------------------------------------------- skills window
class SkillsDialog(QDialog):
    """Create / edit / delete this project's skills (saved as <project>/skills/<name>.md)."""

    def __init__(self, root: str, parent=None):
        super().__init__(parent)
        self.store = SkillStore(root)
        self.current: Optional[str] = None          # slug of the skill being edited (None = new)
        self.setWindowTitle(f"Skills - {os.path.basename(root) or root}")
        self.resize(860, 540)

        left = QVBoxLayout()
        lbl = QLabel("SKILLS IN THIS PROJECT")
        lbl.setObjectName("muted")
        self.listw = QListWidget()
        self.listw.itemClicked.connect(self._on_pick)
        self.new_btn = QPushButton("＋  New skill")
        self.new_btn.clicked.connect(self.new_skill)
        left.addWidget(lbl)
        left.addWidget(self.listw, 1)
        left.addWidget(self.new_btn)

        right = QVBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Skill name, e.g. Brand style")
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("One line saying when to use it (optional, helps DevForge pick it)")
        self.text_edit = QPlainTextEdit()
        self.text_edit.setObjectName("skilltext")
        self.text_edit.setPlaceholderText("Write the instructions DevForge should follow, e.g.\n"
                                          "- Always use a dark theme with accent colour #4A90E2\n"
                                          "- Buttons are rounded, text is in plain English")
        self.text_edit.textChanged.connect(self._count)
        self.count_lbl = QLabel("")
        self.count_lbl.setObjectName("muted")
        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("muted")
        self.del_btn = QPushButton("Delete")
        self.del_btn.clicked.connect(self.delete_skill)
        self.save_btn = QPushButton("Save skill")
        self.save_btn.setObjectName("primary")
        self.save_btn.clicked.connect(self.save_skill)
        row = QHBoxLayout()
        row.addWidget(self.status_lbl, 1)
        row.addWidget(self.del_btn)
        row.addWidget(self.save_btn)
        hint = QLabel("Saved as a file in the <b>skills</b> folder of this project. DevForge picks relevant skills "
                      "automatically; type <b>/skill-name</b> in a prompt to force one.")
        hint.setObjectName("muted")
        hint.setWordWrap(True)
        right.addWidget(self.name_edit)
        right.addWidget(self.desc_edit)
        right.addWidget(self.text_edit, 1)
        right.addWidget(self.count_lbl)
        right.addLayout(row)
        right.addWidget(hint)

        outer = QHBoxLayout(self)
        outer.addLayout(left, 1)
        outer.addLayout(right, 3)
        self.reload()
        self.new_skill()

    # ---- list handling
    def reload(self, select: Optional[str] = None):
        self.listw.clear()
        for sk in self.store.list():
            it = QListWidgetItem(f"✦  {sk['name']}")
            it.setData(Qt.UserRole, sk["slug"])
            it.setToolTip(f"{sk['file']} - {sk['description']}")
            self.listw.addItem(it)
            if sk["slug"] == select:
                self.listw.setCurrentItem(it)

    def _on_pick(self, item):
        self.load_skill(item.data(Qt.UserRole))

    def load_skill(self, slug: str):
        sk = self.store.get(slug)
        if not sk:
            return
        self.current = sk["slug"]
        self.name_edit.setText(sk["name"])
        self.desc_edit.setText(sk["description"])
        self.text_edit.setPlainText(sk["text"])
        self.del_btn.setEnabled(True)
        self.status_lbl.setText(f"Editing skills/{sk['file']}  ·  use it with /{sk['slug']}")

    def new_skill(self):
        self.current = None
        self.listw.clearSelection()
        self.name_edit.clear()
        self.desc_edit.clear()
        self.text_edit.clear()
        self.del_btn.setEnabled(False)
        self.status_lbl.setText("New skill")
        self.name_edit.setFocus()

    def _count(self):
        n = len(self.text_edit.toPlainText())
        if n > MAX_INJECT_CHARS:
            self.count_lbl.setText(f"{n} characters - only the first {MAX_INJECT_CHARS} are sent to the model. Consider splitting this skill.")
            self.count_lbl.setStyleSheet("color:#f59e0b")
        else:
            self.count_lbl.setText(f"{n} / {MAX_INJECT_CHARS} characters")
            self.count_lbl.setStyleSheet("")

    # ---- actions
    def save_skill(self) -> bool:
        name, text, desc = self.name_edit.text().strip(), self.text_edit.toPlainText(), self.desc_edit.text()
        try:
            from devforge.skills import slugify
            slug = slugify(name)
            if slug != self.current and self.store.get(slug):
                if QMessageBox.question(self, "Skill exists", f"A skill called '{slug}' already exists. Replace it?") != QMessageBox.Yes:
                    return False
            saved = self.store.save(name, text, desc, replace_slug=self.current)
        except SkillError as e:
            QMessageBox.warning(self, "Cannot save skill", str(e))
            return False
        self.reload(select=saved["slug"])
        self.load_skill(saved["slug"])
        self.status_lbl.setText(f"Saved skills/{saved['file']}  ·  use it with /{saved['slug']}")
        return True

    def delete_skill(self):
        if not self.current:
            return
        if QMessageBox.question(self, "Delete skill", f"Delete the skill '{self.current}'?") != QMessageBox.Yes:
            return
        self.store.delete(self.current)
        self.reload()
        self.new_skill()


# ---------------------------------------------------------------- project memory window
class MemoryDialog(QDialog):
    """Read / edit / clear what DevForge remembers about this project across all its chats."""

    def __init__(self, root: str, parent=None):
        super().__init__(parent)
        self.store = MemoryStore(root)
        self.setWindowTitle(f"Project memory - {os.path.basename(root) or root}")
        self.resize(640, 500)
        info = QLabel("DevForge saves short facts from your chats (preferences, decisions, what was built) and "
                      "gives them to <b>every chat in this folder</b>, so a new chat already knows what an older one "
                      "discussed. One note per line - edit or delete freely.")
        info.setWordWrap(True)
        info.setObjectName("muted")
        self.enabled_box = QCheckBox("Use project memory in every chat")
        self.enabled_box.setChecked(self.store.enabled())
        self.edit = QPlainTextEdit()
        self.edit.setObjectName("skilltext")
        self.edit.setPlaceholderText("Nothing remembered yet. Notes appear here after your first chats.")
        self.edit.setPlainText("\n".join(n["text"] for n in self.store.notes()))
        self.edit.textChanged.connect(self._count)
        self.count_lbl = QLabel("")
        self.count_lbl.setObjectName("muted")
        self.clear_btn = QPushButton("Clear all")
        self.clear_btn.clicked.connect(self.clear_all)
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("primary")
        self.save_btn.clicked.connect(self.save)
        row = QHBoxLayout()
        row.addWidget(self.count_lbl, 1)
        row.addWidget(self.clear_btn)
        row.addWidget(self.save_btn)
        lay = QVBoxLayout(self)
        lay.addWidget(info)
        lay.addWidget(self.enabled_box)
        lay.addWidget(self.edit, 1)
        lay.addLayout(row)
        self._count()

    def _lines(self) -> List[str]:
        return [ln for ln in self.edit.toPlainText().splitlines() if ln.strip()]

    def _count(self):
        n = len(self._lines())
        self.count_lbl.setText(f"{n} note(s)  ·  DevForge keeps the newest {MAX_NOTES}")

    def save(self) -> bool:
        self.store.replace_all(self._lines())
        self.store.set_enabled(self.enabled_box.isChecked())
        self.edit.setPlainText("\n".join(n["text"] for n in self.store.notes()))
        self.count_lbl.setText(f"Saved - {len(self.store.notes())} note(s)")
        return True

    def clear_all(self):
        if QMessageBox.question(self, "Clear memory", "Forget everything saved for this project?\n"
                                "(Your chats and files are not touched.)") != QMessageBox.Yes:
            return
        self.store.clear()
        self.edit.clear()


# ---------------------------------------------------------------- main window
class MainWindow(QMainWindow):
    ollama_status = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"DevForge AI {__version__}")
        self.resize(1360, 820)
        self.setStyleSheet(STYLE)
        self.root: Optional[str] = None
        self.mode = "code"
        self.engine: Optional[Engine] = None
        self.jobs: List[Job] = []                 # every running prompt, across all folders/chats
        self._draft_job: Optional[Job] = None     # job started from a not-yet-saved new chat
        self.proc: Optional[QProcess] = None
        self.client = OllamaClient()
        self.sid: Optional[str] = None      # active chat id (None = unsaved new chat)
        self._build_ui()
        self.refresh_sidebar()
        self.ollama_status.connect(self.status_lbl.setText)
        threading.Thread(target=self._probe_ollama, daemon=True).start()
        self._apply_mode()

    # ------------------------------------------------------------ layout
    def _build_ui(self):
        root_w = QWidget()
        root_w.setObjectName("root")
        self.setCentralWidget(root_w)
        outer = QHBoxLayout(root_w)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # sidebar
        side = QWidget()
        side.setObjectName("sidebar")
        side.setFixedWidth(270)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(14, 14, 14, 14)
        brand = QLabel("⚒ DevForge AI")
        brand.setObjectName("brand")
        sub = QLabel("Local coding assistant · offline")
        sub.setObjectName("muted")
        self.open_btn = QPushButton("＋  Open Folder")
        self.open_btn.setObjectName("primary")
        self.open_btn.clicked.connect(self.choose_folder)
        recent_lbl = QLabel("PROJECTS")
        recent_lbl.setObjectName("muted")
        self.recent = QTreeWidget()
        self.recent.setHeaderHidden(True)
        self.recent.setIndentation(12)
        self.recent.setExpandsOnDoubleClick(False)
        self.recent.setUniformRowHeights(False)
        self.recent.itemClicked.connect(self._sidebar_clicked)
        self.recent.setContextMenuPolicy(Qt.CustomContextMenu)
        self.recent.customContextMenuRequested.connect(self._sidebar_menu)
        self.status_lbl = QLabel("Checking Ollama...")
        self.status_lbl.setObjectName("muted")
        self.status_lbl.setWordWrap(True)
        for w in (brand, sub):
            sl.addWidget(w)
        sl.addSpacing(10)
        sl.addWidget(self.open_btn)
        sl.addSpacing(12)
        sl.addWidget(recent_lbl)
        sl.addWidget(self.recent, 1)
        sl.addWidget(self.status_lbl)
        outer.addWidget(side)

        # main column
        col = QWidget()
        cl = QVBoxLayout(col)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        header = QWidget()
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 6, 16, 0)
        self.folder_lbl = QLabel("No folder selected")
        self.folder_lbl.setStyleSheet("font-weight:600;font-size:11pt")
        self.chat_tab = QPushButton("💬  Chat")
        self.code_tab = QPushButton("</>  Code")
        for b in (self.chat_tab, self.code_tab):
            b.setObjectName("tab")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
        self.chat_tab.clicked.connect(lambda: self.set_mode("chat"))
        self.code_tab.clicked.connect(lambda: self.set_mode("code"))
        self.new_btn = QPushButton("＋  New chat")
        self.new_btn.clicked.connect(lambda: self.new_chat())
        self.memory_btn = QPushButton("🧠  Memory")
        self.memory_btn.setToolTip("What DevForge remembers about this project across all its chats")
        self.memory_btn.clicked.connect(self.open_memory)
        self.skills_btn = QPushButton("✦  Skills")
        self.skills_btn.setToolTip("Write standing instructions for this project (saved in its skills folder)")
        self.skills_btn.clicked.connect(self.open_skills)
        hl.addWidget(self.folder_lbl)
        hl.addSpacing(24)
        hl.addWidget(self.chat_tab)
        hl.addWidget(self.code_tab)
        hl.addStretch(1)
        hl.addWidget(self.memory_btn)
        hl.addWidget(self.skills_btn)
        hl.addWidget(self.new_btn)
        cl.addWidget(header)

        self.split = QSplitter(Qt.Horizontal)
        self.split.setChildrenCollapsible(False)

        # chat panel
        chat_w = QWidget()
        chl = QVBoxLayout(chat_w)
        chl.setContentsMargins(16, 8, 12, 12)
        self.view = ChatView()
        self.input = PromptEdit()
        self.input.setObjectName("input")
        self.input.setFixedHeight(76)
        self.input.submitted.connect(self.send)
        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("primary")
        self.send_btn.clicked.connect(self.send_or_stop)
        self.send_btn.setFixedWidth(84)
        row = QHBoxLayout()
        row.addWidget(self.input, 1)
        row.addWidget(self.send_btn, 0, Qt.AlignBottom)
        chl.addWidget(self.view, 1)
        chl.addLayout(row)
        self.split.addWidget(chat_w)

        # code panel
        self.code_w = QWidget()
        kl = QVBoxLayout(self.code_w)
        kl.setContentsMargins(0, 8, 12, 12)
        bar = QHBoxLayout()
        self.run_btn = QPushButton("▶  Run")
        self.run_btn.clicked.connect(self.run_project)
        open_ex = QPushButton("Open in Explorer")
        open_ex.clicked.connect(lambda: self.root and os.startfile(self.root))
        bar.addWidget(self.run_btn)
        bar.addWidget(open_ex)
        bar.addStretch(1)
        kl.addLayout(bar)
        inner = QSplitter(Qt.Vertical)
        top = QSplitter(Qt.Horizontal)
        self.fs = QFileSystemModel()
        self.fs.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
        self.proxy = HideProxy()
        self.proxy.setSourceModel(self.fs)
        self.tree = QTreeView()
        self.tree.setModel(self.proxy)
        for c in (1, 2, 3):
            self.tree.hideColumn(c)
        self.tree.setHeaderHidden(True)
        self.tree.clicked.connect(self._tree_clicked)
        self.code = QPlainTextEdit()
        self.code.setObjectName("code")
        self.code.setReadOnly(True)
        self.code.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.code.setPlainText("Select a file to view it.")
        top.addWidget(self.tree)
        top.addWidget(self.code)
        top.setSizes([200, 480])
        self.output = QPlainTextEdit()
        self.output.setObjectName("output")
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Run output appears here.")
        inner.addWidget(top)
        inner.addWidget(self.output)
        inner.setSizes([520, 150])
        kl.addWidget(inner, 1)
        self.split.addWidget(self.code_w)
        self.split.setSizes([620, 680])
        cl.addWidget(self.split, 1)
        outer.addWidget(col, 1)

    # ------------------------------------------------------------ recent folders
    # ------------------------------------------------------------ sidebar: projects > chats
    def _folder_row(self, path: str, active: bool) -> QWidget:
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(4, 0, 2, 0)
        lbl = QLabel("📁  " + (os.path.basename(path) or path))
        lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        if active:
            lbl.setStyleSheet("font-weight:600;color:white")
        btn = QToolButton()
        btn.setText("＋")
        btn.setToolTip("New chat in this folder")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("QToolButton{border:none;color:#8b93a5;font-size:13pt;padding:0 6px}"
                          "QToolButton:hover{color:white}")
        btn.clicked.connect(lambda _=False, p=path: self.new_chat(p))
        h.addWidget(lbl, 1)
        h.addWidget(btn)
        return w

    def refresh_sidebar(self):
        tree = self.recent
        expanded = {tree.topLevelItem(i).data(0, Qt.UserRole) for i in range(tree.topLevelItemCount())
                    if tree.topLevelItem(i).isExpanded()}
        tree.blockSignals(True)
        tree.clear()
        select = None
        for p in load_recent():
            active = bool(self.root) and os.path.normcase(p) == os.path.normcase(self.root)
            top = QTreeWidgetItem(tree)
            top.setData(0, Qt.UserRole, p)
            top.setData(0, Qt.UserRole + 1, "folder")
            top.setToolTip(0, p)
            top.setSizeHint(0, QSize(0, 34))
            tree.setItemWidget(top, 0, self._folder_row(p, active))
            for sess in ProjectStore(p).list_sessions():
                ch = QTreeWidgetItem(top)
                is_running = any(j.sid == sess["id"] and _same(j.root, p) for j in self.jobs)
                glyph = "⏳" if is_running else ("💬" if sess["mode"] == "chat" else "</>")
                ch.setText(0, f"{glyph}  {sess['title']}")
                ch.setToolTip(0, sess["title"])
                ch.setData(0, Qt.UserRole, p)
                ch.setData(0, Qt.UserRole + 1, "chat")
                ch.setData(0, Qt.UserRole + 2, sess["id"])
                if active and sess["id"] == self.sid:
                    select = ch
            top.setExpanded(active or p in expanded)
        if select:
            tree.setCurrentItem(select)
        tree.blockSignals(False)

    def _sidebar_clicked(self, item, _col=0):
        path, kind = item.data(0, Qt.UserRole), item.data(0, Qt.UserRole + 1)
        if kind == "folder":
            item.setExpanded(not item.isExpanded() if self._is_active(path) else True)
            if not self._is_active(path):
                sessions = ProjectStore(path).list_sessions()
                if sessions:
                    self.open_session(path, sessions[0]["id"])
                else:
                    self.open_folder(path)
        else:
            self.open_session(path, item.data(0, Qt.UserRole + 2))

    def _is_active(self, path: str) -> bool:
        return bool(self.root) and os.path.normcase(path) == os.path.normcase(self.root)

    def _sidebar_menu(self, pos):
        it = self.recent.itemAt(pos)
        if not it:
            return
        path, kind = it.data(0, Qt.UserRole), it.data(0, Qt.UserRole + 1)
        menu = QMenu(self)
        if kind == "chat":
            sid = it.data(0, Qt.UserRole + 2)
            a_ren, a_del = menu.addAction("Rename"), menu.addAction("Delete")
            chosen = menu.exec(self.recent.mapToGlobal(pos))
            if chosen == a_ren:
                self.rename_chat(path, sid)
            elif chosen == a_del:
                self.delete_chat(path, sid)
        else:
            a_new, a_exp, a_rem = menu.addAction("New chat"), menu.addAction("Open in Explorer"), menu.addAction("Remove from list")
            chosen = menu.exec(self.recent.mapToGlobal(pos))
            if chosen == a_new:
                self.new_chat(path)
            elif chosen == a_exp and os.path.isdir(path):
                os.startfile(path)
            elif chosen == a_rem:
                remove_recent(path)
                if self._is_active(path):
                    self.root, self.engine, self.sid = None, None, None
                    self.folder_lbl.setText("No folder selected")
                    self._load_history()
                    self._apply_mode()
                self.refresh_sidebar()

    def rename_chat(self, path: str, sid: str):
        store = ProjectStore(path)
        meta = store.meta(sid)
        if not meta:
            return
        text, ok = QInputDialog.getText(self, "Rename chat", "Chat name:", text=meta["title"])
        if ok and text.strip():
            store.rename(sid, text.strip(), auto=False)
            self.refresh_sidebar()

    def delete_chat(self, path: str, sid: str):
        store = ProjectStore(path)
        meta = store.meta(sid)
        if not meta:
            return
        if any(j.sid == sid and _same(j.root, path) for j in self.jobs):
            QMessageBox.information(self, "Chat is running", "This chat is still working. Press Stop first, then delete it.")
            return
        if QMessageBox.question(self, "Delete chat", f"Delete \"{meta['title']}\"?\n"
                                "(Your project files are not touched.)") != QMessageBox.Yes:
            return
        store.delete(sid)
        if self._is_active(path) and self.sid == sid:
            self.start_draft()
        self.refresh_sidebar()

    # ------------------------------------------------------------ opening folders / chats
    def choose_folder(self):
        start = self.root or str(Path.home())
        path = QFileDialog.getExistingDirectory(self, "Choose a project folder", start)
        if path:
            self.open_folder(path)

    def _activate_folder(self, path: str):
        path = os.path.abspath(path)
        if not self._is_active(path):
            self.root = path
            self.folder_lbl.setText(f"📁 {os.path.basename(path) or path}")
            self.folder_lbl.setToolTip(path)
            self.fs.setRootPath(path)
            self.tree.setRootIndex(self.proxy.mapFromSource(self.fs.index(path)))
            self.code.setPlainText("Select a file to view it.")
            self.output.clear()
        add_recent(path)

    def open_folder(self, path: str):
        """Open a folder and start a fresh (unsaved) chat in it."""
        if not os.path.isdir(path):
            return
        self._activate_folder(path)
        self.start_draft()

    def open_session(self, path: str, sid: str):
        if not os.path.isdir(path):
            return
        meta = ProjectStore(path).meta(sid)
        if not meta:
            self.refresh_sidebar()
            return
        self._activate_folder(path)
        self._draft_job = None
        self.sid, self.mode = sid, meta["mode"]
        self._load_history()
        self._apply_mode()
        self.refresh_sidebar()

    def start_draft(self):
        """New chat: nothing is saved until the first prompt is sent."""
        self._draft_job = None
        self.sid = None
        self._load_history()
        self._apply_mode()
        self.refresh_sidebar()
        self.input.setFocus()

    def new_chat(self, path: Optional[str] = None):
        path = path or self.root
        if not path:
            self.choose_folder()
            return
        self._activate_folder(path)
        self.start_draft()

    # ------------------------------------------------------------ mode + history
    def set_mode(self, mode: str):
        if mode == self.mode:
            self.chat_tab.setChecked(self.mode == "chat")
            self.code_tab.setChecked(self.mode == "code")
            return
        self.mode = mode
        info = ProjectStore(self.root).meta(self.sid) if (self.root and self.sid) else None
        if info and info["count"] > 0:
            self.start_draft()          # a saved chat keeps its mode, so open a new one in the other mode
        else:
            self._apply_mode()

    def _apply_mode(self):
        self.chat_tab.setChecked(self.mode == "chat")
        self.code_tab.setChecked(self.mode == "code")
        self.code_w.setVisible(self.mode == "code")
        has = self.root is not None
        if not has:
            ph = "<h2>Open a folder to get started</h2>Click <b>＋ Open Folder</b> on the left. You can keep many chats per folder."
        elif self.mode == "chat":
            ph = ("<h2>💬 New chat</h2>Ask me anything - project related or not. "
                  "Switch to <b>Code</b> when you want me to build or change files in this folder.")
        else:
            ph = ("<h2>&lt;/&gt; New chat</h2>Describe what to build or change in this folder, e.g.<br>"
                  "<i>“generate a simple website for a shoe store”</i><br>"
                  "I only handle project-related requests here.")
        self.view.placeholder = ph
        self.input.setPlaceholderText(
            "Ask anything... (Enter to send, Shift+Enter for a new line, /skill-name to force a skill)" if self.mode == "chat"
            else "Describe what to build or change in this folder... (type /skill-name to force a skill)")
        self.view.refresh()
        self._sync_controls()

    def _load_history(self):
        msgs = ProjectStore(self.root).load(self.sid) if (self.root and self.sid) else []
        self.view.messages = [m for m in msgs if m["role"] in ("user", "assistant")]
        job = self.job_for_view()
        self.view.progress = job.progress if job else []      # a running chat shows its live progress again
        self.view.live = job.live if job else None
        self.view.refresh()

    def open_memory(self):
        if self.root:
            MemoryDialog(self.root, self).exec()

    def open_skills(self):
        if self.root:
            SkillsDialog(self.root, self).exec()

    # ------------------------------------------------------------ jobs (background prompts)
    def job_for_view(self) -> Optional[Job]:
        """The running job of the chat currently on screen, if any."""
        if not self.root:
            return None
        for j in self.jobs:
            if self.sid is None and j is self._draft_job:
                return j
            if self.sid is not None and j.sid == self.sid and _same(j.root, self.root):
                return j
        return None

    def busy(self) -> bool:
        return self.job_for_view() is not None

    def _style_send(self, stop: bool):
        self.send_btn.setObjectName("danger" if stop else "primary")
        self.send_btn.setStyleSheet("")
        self.style().unpolish(self.send_btn)
        self.style().polish(self.send_btn)

    def _sync_controls(self):
        """Buttons follow the chat on screen: its own job decides Send vs Stop. Nothing else is locked."""
        has = self.root is not None
        job = self.job_for_view()
        self.input.setEnabled(has and job is None)
        self.new_btn.setEnabled(has)
        self.skills_btn.setEnabled(has)
        self.memory_btn.setEnabled(has)
        self.open_btn.setEnabled(True)
        self.recent.setEnabled(True)
        self.send_btn.setEnabled(has)
        if job is not None:
            self.send_btn.setText("Stopping..." if job.stopped else "■ Stop")
            self.send_btn.setEnabled(not job.stopped)
            self._style_send(True)
        else:
            self.send_btn.setText("Send")
            self._style_send(False)

    def send_or_stop(self):
        job = self.job_for_view()
        if job is not None:
            job.stopped = True
            job.worker.stop()
            self._sync_controls()
        else:
            self.send()

    def send(self):
        text = self.input.toPlainText().strip()
        if not text or not self.root or self.job_for_view() is not None:
            return
        self.input.clear()
        job = Job(self.root, self.mode, text, self.sid)
        job.worker = Worker(Engine(self.root, self.client), job.mode, text, job.sid)   # own engine per job
        job.worker.event.connect(lambda k, d, j=job: self._on_event(j, k, d))
        job.worker.failed.connect(lambda msg, j=job: self._on_failed(j, msg))
        job.worker.finished.connect(lambda j=job: self._on_finished(j))
        self.jobs.append(job)
        if self.sid is None:
            self._draft_job = job
        self.view.messages.append({"role": "user", "content": text})
        self.view.progress = job.progress
        self.view.live = job.live
        self.view.refresh()
        self._sync_controls()
        job.worker.start()

    def _on_event(self, job: Job, kind: str, d: dict):
        shown = self.job_for_view() is job
        if kind == "session":               # the new chat now exists on disk: show it at the top
            job.sid = d["id"]
            if self._draft_job is job:
                self._draft_job = None
                if shown and self.sid is None:
                    self.sid = job.sid
            self.refresh_sidebar()
        elif kind == "title":               # proper AI-generated name replaces the provisional one
            self.refresh_sidebar()
        elif kind == "stage":
            self._finish_line(job)
            model = f" <span style='color:#6b7385'>({d['model']})</span>" if d.get("model") else ""
            job.progress.append(f"⏳ <b>{html.escape(d['agent'])}</b>{model} - {html.escape(d['text'])}")
            job.line = len(job.progress) - 1
        elif kind == "stream":
            job.live = (job.live or "") + d["text"]
        elif kind == "file":
            if _same(job.root, self.root):
                self._open_file(os.path.join(job.root, d["path"]))
        elif kind == "done":
            self._finish_line(job)
        if self.job_for_view() is job:
            self.view.progress = job.progress
            self.view.live = job.live
            self.view.refresh()

    @staticmethod
    def _finish_line(job: Job):
        if 0 <= job.line < len(job.progress):
            job.progress[job.line] = job.progress[job.line].replace("⏳", "✓", 1)
        job.line = -1

    def _on_failed(self, job: Job, msg: str):
        job.failed = True
        if job.sid:      # keep the error in that chat's history, visible whenever it is opened
            ProjectStore(job.root).append(job.sid, "assistant", f"⚠️ **Something went wrong**\n\n{msg}")

    def _on_finished(self, job: Job):
        shown = self.job_for_view() is job
        if job.stopped and not job.failed and job.sid:
            ProjectStore(job.root).append(job.sid, "assistant", "⏹ Stopped.")
        job.worker.wait(2000)
        if job in self.jobs:
            self.jobs.remove(job)
        if self._draft_job is job:
            self._draft_job = None
        if shown:
            self._load_history()
            self._sync_controls()
            self.input.setFocus()
        self.refresh_sidebar()

    # ------------------------------------------------------------ code panel
    def _tree_clicked(self, idx):
        path = self.fs.filePath(self.proxy.mapToSource(idx))
        if os.path.isfile(path):
            self._open_file(path)

    def _open_file(self, path: str):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                self.code.setPlainText(f.read(300_000))
        except OSError as e:
            self.code.setPlainText(f"Cannot open file: {e}")

    def run_project(self):
        if self.proc and self.proc.state() != QProcess.NotRunning:
            self.proc.kill()
            return
        if not self.root:
            return
        target = fsops.find_run_target(self.root)
        if not target:
            self.output.setPlainText("Nothing to run yet - ask me to build something first.")
            return
        kind, rel = target
        if kind == "browser":
            webbrowser.open(QUrl.fromLocalFile(os.path.join(self.root, rel)).toString())
            self.output.setPlainText(f"Opened {rel} in your browser.")
            return
        self.output.setPlainText(f"> {kind} {rel}\n")
        self.proc = QProcess(self)
        self.proc.setWorkingDirectory(self.root)
        self.proc.setProcessChannelMode(QProcess.MergedChannels)
        self.proc.readyReadStandardOutput.connect(
            lambda: self.output.appendPlainText(bytes(self.proc.readAllStandardOutput()).decode("utf-8", "replace").rstrip()))
        self.proc.finished.connect(self._run_finished)
        exe = sys.executable if kind == "python" else "node"
        self.proc.start(exe, [rel])
        self.run_btn.setText("■  Stop")

    def _run_finished(self, code, _status):
        self.output.appendPlainText(f"\n[process exited with code {code}]")
        self.run_btn.setText("▶  Run")

    # ------------------------------------------------------------ misc
    def _probe_ollama(self):
        if not self.client.ensure_server():
            self.ollama_status.emit("● Ollama not running")
            return
        models = self.client.list_models()
        self.ollama_status.emit(f"● Ollama connected · {len(models)} model(s)")

    def closeEvent(self, e):
        for j in list(self.jobs):
            j.worker.stop()
        for j in list(self.jobs):
            j.worker.wait(5000)
        if self.proc and self.proc.state() != QProcess.NotRunning:
            self.proc.kill()
        super().closeEvent(e)


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
