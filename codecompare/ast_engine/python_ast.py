"""Python AST extraction, normalisation, and comparison."""
from __future__ import annotations
import ast, hashlib
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FunctionInfo:
    name: str; args: list[str]; decorators: list[str]
    start_line: int; end_line: int; cyclomatic_complexity: int
    body_hash: str; is_async: bool = False; docstring: str = ""


@dataclass
class ClassInfo:
    name: str; bases: list[str]; methods: list[str]
    start_line: int; end_line: int; decorator_list: list[str] = field(default_factory=list)


@dataclass
class ImportInfo:
    module: str; names: list[str]; alias: str = ""; is_from: bool = False


@dataclass
class PythonASTSummary:
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    imports: list[ImportInfo] = field(default_factory=list)
    global_vars: list[str] = field(default_factory=list)
    parse_error: str = ""
    tree_hash: str = ""


_BRANCH_NODES = (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With, ast.Assert, ast.comprehension, ast.BoolOp)


def _cyclomatic_complexity(node: ast.AST) -> int:
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, _BRANCH_NODES): complexity += 1
        if isinstance(child, ast.BoolOp): complexity += len(child.values) - 1
    return complexity


class _Extractor(ast.NodeVisitor):
    def __init__(self, source_lines: list[str]) -> None:
        self.source_lines = source_lines
        self.functions: list[FunctionInfo] = []
        self.classes: list[ClassInfo] = []
        self.imports: list[ImportInfo] = []
        self.global_vars: list[str] = []
        self._class_stack: list[str] = []

    def visit_FunctionDef(self, node): self._process_func(node, False); self.generic_visit(node)
    def visit_AsyncFunctionDef(self, node): self._process_func(node, True); self.generic_visit(node)

    def _process_func(self, node, is_async: bool) -> None:
        body_src = "\n".join(self.source_lines[node.lineno-1:node.end_lineno])
        body_hash = hashlib.sha256(body_src.encode()).hexdigest()[:16]
        self.functions.append(FunctionInfo(
            name=node.name, args=[a.arg for a in node.args.args],
            decorators=[ast.unparse(d) for d in node.decorator_list],
            start_line=node.lineno, end_line=node.end_lineno,
            cyclomatic_complexity=_cyclomatic_complexity(node),
            body_hash=body_hash, is_async=is_async,
            docstring=ast.get_docstring(node) or ""))

    def visit_ClassDef(self, node):
        bases = [ast.unparse(b) for b in node.bases]
        methods = [n.name for n in ast.walk(node) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        self.classes.append(ClassInfo(name=node.name, bases=bases, methods=methods,
                                      start_line=node.lineno, end_line=node.end_lineno))
        self._class_stack.append(node.name); self.generic_visit(node); self._class_stack.pop()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(ImportInfo(module=alias.name, names=[alias.name], alias=alias.asname or "", is_from=False))

    def visit_ImportFrom(self, node):
        self.imports.append(ImportInfo(module=node.module or "", names=[a.name for a in node.names], is_from=True))

    def visit_Assign(self, node):
        if not self._class_stack:
            for t in node.targets:
                if isinstance(t, ast.Name): self.global_vars.append(t.id)


def extract(code: str) -> PythonASTSummary:
    summary = PythonASTSummary()
    try: tree = ast.parse(code)
    except SyntaxError as exc: summary.parse_error = str(exc); return summary
    visitor = _Extractor(code.splitlines())
    visitor.visit(tree)
    summary.functions = visitor.functions
    summary.classes = visitor.classes
    summary.imports = visitor.imports
    summary.global_vars = visitor.global_vars
    summary.tree_hash = hashlib.sha256(ast.dump(tree).encode()).hexdigest()[:24]
    return summary


def compare_summaries(old: PythonASTSummary, new: PythonASTSummary) -> dict[str, Any]:
    old_funcs = {f.name: f for f in old.functions}
    new_funcs = {f.name: f for f in new.functions}
    old_cls = {c.name: c for c in old.classes}
    new_cls = {c.name: c for c in new.classes}
    old_imports = {i.module for i in old.imports}
    new_imports = {i.module for i in new.imports}
    return {
        "functions": {
            "added": [n for n in new_funcs if n not in old_funcs],
            "removed": [n for n in old_funcs if n not in new_funcs],
            "changed": [n for n in old_funcs if n in new_funcs and old_funcs[n].body_hash != new_funcs[n].body_hash],
            "complexity_delta": {n: new_funcs[n].cyclomatic_complexity - old_funcs[n].cyclomatic_complexity for n in old_funcs if n in new_funcs},
        },
        "classes": {
            "added": [n for n in new_cls if n not in old_cls],
            "removed": [n for n in old_cls if n not in new_cls],
            "changed": [n for n in old_cls if n in new_cls and set(old_cls[n].methods) != set(new_cls[n].methods)],
        },
        "imports": {"added": sorted(new_imports - old_imports), "removed": sorted(old_imports - new_imports)},
    }


def ast_similarity(old: PythonASTSummary, new: PythonASTSummary) -> float:
    if old.parse_error or new.parse_error: return 0.0
    def set_sim(a: set, b: set) -> float:
        if not a and not b: return 1.0
        return len(a & b) / len(a | b) if (a | b) else 1.0
    old_funcs = {f.name for f in old.functions}
    new_funcs = {f.name for f in new.functions}
    old_cls = {c.name for c in old.classes}
    new_cls = {c.name for c in new.classes}
    func_score = set_sim(old_funcs, new_funcs)
    cls_score = set_sim(old_cls, new_cls)
    matching = old_funcs & new_funcs
    if matching:
        om, nm = {f.name: f for f in old.functions}, {f.name: f for f in new.functions}
        body_score = sum(1 for n in matching if om[n].body_hash == nm[n].body_hash) / len(matching)
    else:
        body_score = 1.0 if not old_funcs and not new_funcs else 0.0
    return func_score * 0.4 + cls_score * 0.2 + body_score * 0.4
