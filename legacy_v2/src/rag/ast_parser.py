import ast
import os
from typing import Dict, List, Any

class CodeASTAnalyzer:
    """Extracts structural syntax elements (classes, functions, imports) from Python source files."""
    
    @staticmethod
    def analyze_file(filepath: str) -> Dict[str, Any]:
        if not os.path.exists(filepath):
            return {"error": f"File {filepath} not found."}
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            return CodeASTAnalyzer.analyze_source(source, filename=os.path.basename(filepath))
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def analyze_source(source: str, filename: str = "snippet.py") -> Dict[str, Any]:
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            return {
                "filename": filename,
                "syntax_valid": False,
                "error": f"SyntaxError at line {e.lineno}: {e.msg}",
                "classes": [],
                "functions": [],
                "imports": []
            }

        classes = []
        functions = []
        imports = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                methods = [m.name for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
                classes.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "methods": methods,
                    "docstring": ast.get_docstring(node) or ""
                })
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node) or ""
                })
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")

        return {
            "filename": filename,
            "syntax_valid": True,
            "error": None,
            "classes": classes,
            "functions": functions,
            "imports": imports
        }

    @staticmethod
    def format_summary(ast_data: Dict[str, Any]) -> str:
        """Creates a concise structural representation for context windows."""
        if not ast_data.get("syntax_valid", False):
            return f"File: {ast_data.get('filename')}\nError: {ast_data.get('error')}"
            
        summary = [f"File: {ast_data.get('filename')}"]
        if ast_data.get("imports"):
            summary.append(f"Imports: {', '.join(ast_data['imports'][:8])}")
        for cls in ast_data.get("classes", []):
            methods_str = ", ".join(cls["methods"]) if cls["methods"] else "none"
            summary.append(f"Class {cls['name']}(methods: {methods_str})")
        for fn in ast_data.get("functions", []):
            args_str = ", ".join(fn["args"])
            summary.append(f"Function {fn['name']}({args_str})")
            
        return "\n".join(summary)
