import os
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Callable, Optional

class FileTreeWidget(ctk.CTkFrame):
    """Modern dark-themed file explorer tree for CustomTkinter."""
    def __init__(self, master, on_file_click: Optional[Callable[[str], None]] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_file_click = on_file_click
        self.current_root = ""

        # Header bar
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=8, pady=(8, 4))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="FILES & FOLDERS",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94A3B8"
        )
        self.title_label.pack(side="left")

        self.refresh_btn = ctk.CTkButton(
            self.header_frame,
            text="🔄",
            width=28,
            height=24,
            fg_color="#334155",
            hover_color="#475569",
            command=self.refresh
        )
        self.refresh_btn.pack(side="right")

        # Tree Container with Dark Styling
        self.tree_container = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=6)
        self.tree_container.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dark.Treeview",
            background="#090D16",
            foreground="#E2E8F0",
            fieldbackground="#090D16",
            borderwidth=0,
            font=("Consolas", 10),
            rowheight=22
        )
        style.map(
            "Dark.Treeview",
            background=[("selected", "#2563EB")],
            foreground=[("selected", "#FFFFFF")]
        )

        self.tree = ttk.Treeview(
            self.tree_container,
            style="Dark.Treeview",
            show="tree",
            selectmode="browse"
        )
        
        # Scrollbars
        self.vsb = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vsb.set)
        
        self.vsb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # Bind click events
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)

        # Node id to real full path mapping
        self._path_map = {}

    def set_directory(self, folder_path: str):
        self.current_root = folder_path
        self.refresh()

    def refresh(self):
        if not self.current_root or not os.path.isdir(self.current_root):
            return

        self.tree.delete(*self.tree.get_children())
        self._path_map.clear()

        # Add root node
        root_name = os.path.basename(self.current_root) or self.current_root
        root_node = self.tree.insert("", "end", text=f"📂 {root_name}", open=True)
        self._path_map[root_node] = self.current_root

        self._populate_tree(self.current_root, root_node)

    def _populate_tree(self, parent_path: str, parent_node: str):
        try:
            entries = os.scandir(parent_path)
            # Separate dirs and files
            dirs = []
            files = []
            for entry in entries:
                if entry.name.startswith(".") or entry.name in ("__pycache__", "node_modules", "venv", ".venv"):
                    continue
                if entry.is_dir():
                    dirs.append(entry)
                elif entry.is_file():
                    files.append(entry)

            # Sort alphabetically
            dirs.sort(key=lambda e: e.name.lower())
            files.sort(key=lambda e: e.name.lower())

            for d in dirs:
                node = self.tree.insert(parent_node, "end", text=f"📁 {d.name}", open=False)
                self._path_map[node] = d.path
                self._populate_tree(d.path, node)

            for f in files:
                icon = "🐍" if f.name.endswith(".py") else ("📄" if f.name.endswith((".md", ".txt", ".json", ".yaml")) else "📜")
                node = self.tree.insert(parent_node, "end", text=f"{icon} {f.name}")
                self._path_map[node] = f.path

        except PermissionError:
            pass
        except Exception as e:
            print(f"[FileTree] Error scanning {parent_path}: {e}")

    def _on_select(self, event):
        selected_nodes = self.tree.selection()
        if not selected_nodes:
            return
        node = selected_nodes[0]
        filepath = self._path_map.get(node)
        if filepath and os.path.isfile(filepath) and self.on_file_click:
            self.on_file_click(filepath)

    def _on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            filepath = self._path_map.get(item)
            if filepath and os.path.isfile(filepath) and self.on_file_click:
                self.on_file_click(filepath)
