"""
Code Analyzer Module
Analyzes source code to extract structure information.
Uses Python AST for Python code; basic regex/heuristics for other languages.
"""

import ast
import re


def analyze_code(code: str, language: str) -> dict:
    """
    Analyze source code and return structured information.

    Args:
        code: The source code string.
        language: Programming language (python, java, cpp, javascript).

    Returns:
        Dictionary with analysis results.
    """
    language = language.lower().strip()

    if language == "auto detect":
        language = detect_language(code)

    analyzers = {
        "python": analyze_python,
        "java": analyze_java,
        "c++": analyze_cpp,
        "javascript": analyze_javascript,
    }

    analyzer = analyzers.get(language, analyze_generic)
    result = analyzer(code)
    result["language"] = language.capitalize()
    result["code"] = code
    return result


def detect_language(code: str) -> str:
    """Simple heuristic-based language detection."""
    if "def " in code and ":" in code:
        return "python"
    if "public static void main" in code or "System.out" in code:
        return "java"
    if "#include" in code or "cout" in code or "::" in code:
        return "c++"
    if "function " in code or "const " in code or "=>" in code or "console.log" in code:
        return "javascript"
    return "python"  # Default fallback


# ──────────────────────────────────────────────
# Python Analyzer (uses AST)
# ──────────────────────────────────────────────

def analyze_python(code: str) -> dict:
    """Analyze Python code using the AST module."""
    result = {
        "functions": [],
        "classes": [],
        "imports": [],
        "doc_coverage": 0,
    }

    try:
        tree = ast.parse(code)
    except SyntaxError:
        # If AST fails, fall back to generic
        return analyze_generic(code)

    total_documentable = 0
    documented = 0

    for node in ast.walk(tree):
        # --- Functions ---
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            params = [arg.arg for arg in node.args.args]
            has_docstring = (
                isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, (ast.Str, ast.Constant))
            ) if node.body else False

            # Detect return
            has_return = any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(node))

            result["functions"].append({
                "name": node.name,
                "params": params,
                "has_docstring": has_docstring,
                "docstring": ast.get_docstring(node) or "",
                "has_return": has_return,
                "line": node.lineno,
            })
            total_documentable += 1
            if has_docstring:
                documented += 1

        # --- Classes ---
        elif isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(item.name)

            has_docstring = (
                isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, (ast.Str, ast.Constant))
            ) if node.body else False

            result["classes"].append({
                "name": node.name,
                "methods": methods,
                "has_docstring": has_docstring,
                "docstring": ast.get_docstring(node) or "",
                "line": node.lineno,
            })
            total_documentable += 1
            if has_docstring:
                documented += 1

        # --- Imports ---
        elif isinstance(node, ast.Import):
            for alias in node.names:
                result["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                result["imports"].append(f"{module}.{alias.name}")

    # Calculate documentation coverage
    if total_documentable > 0:
        result["doc_coverage"] = round((documented / total_documentable) * 100)
    else:
        result["doc_coverage"] = 0

    return result


# ──────────────────────────────────────────────
# Java Analyzer (regex-based)
# ──────────────────────────────────────────────

def analyze_java(code: str) -> dict:
    """Basic Java code analysis using regex."""
    functions = re.findall(
        r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)',
        code
    )
    classes = re.findall(r'(?:public|private|protected)?\s*class\s+(\w+)', code)
    imports = re.findall(r'import\s+([\w.]+);', code)

    func_list = []
    for name, params in functions:
        if name not in ('if', 'for', 'while', 'switch', 'catch'):
            param_list = [p.strip().split()[-1] for p in params.split(',') if p.strip()]
            func_list.append({
                "name": name,
                "params": param_list,
                "has_docstring": False,
                "docstring": "",
                "has_return": True,
                "line": 0,
            })

    return {
        "functions": func_list,
        "classes": [{"name": c, "methods": [], "has_docstring": False, "docstring": "", "line": 0} for c in classes],
        "imports": imports,
        "doc_coverage": 0,
    }


# ──────────────────────────────────────────────
# C++ Analyzer (regex-based)
# ──────────────────────────────────────────────

def analyze_cpp(code: str) -> dict:
    """Basic C++ code analysis using regex."""
    functions = re.findall(
        r'(?:[\w:]+\s+)+(\w+)\s*\(([^)]*)\)\s*\{',
        code
    )
    classes = re.findall(r'class\s+(\w+)', code)
    includes = re.findall(r'#include\s*[<"]([^>"]+)[>"]', code)

    func_list = []
    for name, params in functions:
        if name not in ('if', 'for', 'while', 'switch', 'catch', 'class'):
            param_list = [p.strip().split()[-1] for p in params.split(',') if p.strip()]
            func_list.append({
                "name": name,
                "params": param_list,
                "has_docstring": False,
                "docstring": "",
                "has_return": True,
                "line": 0,
            })

    return {
        "functions": func_list,
        "classes": [{"name": c, "methods": [], "has_docstring": False, "docstring": "", "line": 0} for c in classes],
        "imports": includes,
        "doc_coverage": 0,
    }


# ──────────────────────────────────────────────
# JavaScript Analyzer (regex-based)
# ──────────────────────────────────────────────

def analyze_javascript(code: str) -> dict:
    """Basic JavaScript code analysis using regex."""
    # Match: function name(...), const name = (...) =>, etc.
    functions_standard = re.findall(r'function\s+(\w+)\s*\(([^)]*)\)', code)
    functions_arrow = re.findall(r'(?:const|let|var)\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>', code)
    classes = re.findall(r'class\s+(\w+)', code)
    imports = re.findall(r"(?:import|require)\s*\(?['\"]([^'\"]+)['\"]", code)

    func_list = []
    for name, params in functions_standard + functions_arrow:
        param_list = [p.strip() for p in params.split(',') if p.strip()]
        func_list.append({
            "name": name,
            "params": param_list,
            "has_docstring": False,
            "docstring": "",
            "has_return": True,
            "line": 0,
        })

    return {
        "functions": func_list,
        "classes": [{"name": c, "methods": [], "has_docstring": False, "docstring": "", "line": 0} for c in classes],
        "imports": imports,
        "doc_coverage": 0,
    }


# ──────────────────────────────────────────────
# Generic Analyzer (fallback)
# ──────────────────────────────────────────────

def analyze_generic(code: str) -> dict:
    """Minimal fallback analyzer — counts lines and basic patterns."""
    lines = code.strip().split('\n')
    return {
        "functions": [],
        "classes": [],
        "imports": [],
        "doc_coverage": 0,
        "note": f"Generic analysis: {len(lines)} lines of code detected.",
    }


def format_analysis_summary(analysis: dict) -> str:
    """Format the analysis result as a readable Markdown summary."""
    lang = analysis.get("language", "Unknown")
    funcs = analysis.get("functions", [])
    classes = analysis.get("classes", [])
    imports = analysis.get("imports", [])
    coverage = analysis.get("doc_coverage", 0)

    summary = f"""### 📊 Code Analysis Results

| Metric | Value |
|--------|-------|
| **Language** | {lang} |
| **Functions Found** | {len(funcs)} |
| **Classes Found** | {len(classes)} |
| **Imports** | {len(imports)} |
| **Documentation Coverage** | {coverage}% |
"""

    if funcs:
        summary += "\n**Functions:**\n"
        for f in funcs:
            params = ", ".join(f["params"]) if f["params"] else "none"
            doc_icon = "✅" if f.get("has_docstring") else "❌"
            summary += f"- `{f['name']}({params})` — Docstring: {doc_icon}\n"

    if classes:
        summary += "\n**Classes:**\n"
        for c in classes:
            doc_icon = "✅" if c.get("has_docstring") else "❌"
            summary += f"- `{c['name']}` — Docstring: {doc_icon}\n"

    if analysis.get("note"):
        summary += f"\n> ℹ️ {analysis['note']}\n"

    return summary
