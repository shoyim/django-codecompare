"""Cyclomatic complexity, Halstead metrics, and Maintainability Index."""
from __future__ import annotations
import ast, math, re
from typing import Any
from codecompare.core.types import ComplexityMetrics

_BRANCH_TYPES = (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With, ast.AsyncWith, ast.AsyncFor, ast.comprehension, ast.Assert)
_OPERATORS = re.compile(r"[+\-*/%=<>!&|^~?:]+|and\b|or\b|not\b|in\b|is\b")
_OPERANDS = re.compile(r"\b\d+(?:\.\d+)?\b|\b[a-zA-Z_]\w*\b")


def _python_cyclomatic(tree: ast.AST) -> int:
    count = 1
    for node in ast.walk(tree):
        if isinstance(node, _BRANCH_TYPES): count += 1
        elif isinstance(node, ast.BoolOp): count += len(node.values) - 1
    return count


def _count_lines(code: str) -> tuple[int, int, int, int]:
    total = comment = blank = logical = 0
    for line in code.splitlines():
        total += 1
        stripped = line.strip()
        if not stripped: blank += 1
        elif stripped.startswith(("#", "//", "--", "/*", "*", "<!--")): comment += 1
        else: logical += 1
    return total, logical, comment, blank


def halstead_metrics(code: str) -> dict[str, float]:
    operators = _OPERATORS.findall(code)
    operands = _OPERANDS.findall(code)
    n1, n2, N1, N2 = len(set(operators)), len(set(operands)), len(operators), len(operands)
    vocab = n1 + n2; length = N1 + N2
    volume = length * math.log2(vocab) if vocab > 1 else 0.0
    difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0.0
    return {"vocabulary": vocab, "length": length, "volume": round(volume, 2),
            "difficulty": round(difficulty, 2), "effort": round(difficulty * volume, 2)}


def maintainability_index(halstead_volume: float, cyclomatic: int, lines_of_code: int, comment_ratio: float = 0.0) -> float:
    if lines_of_code <= 0: return 100.0
    mi = 171 - 5.2 * math.log(max(1.0, halstead_volume)) - 0.23 * cyclomatic - 16.2 * math.log(max(1, lines_of_code))
    if comment_ratio > 0: mi += 50 * math.sin(math.sqrt(2.4 * comment_ratio))
    return round(max(0.0, mi * 100 / 171), 2)


def analyse(code: str, language: str) -> ComplexityMetrics:
    total, logical, comment, blank = _count_lines(code)
    halstead = halstead_metrics(code)
    functions = classes = 0; cyclomatic = 1; max_nesting = 0
    if language == "python":
        try:
            tree = ast.parse(code)
            cyclomatic = _python_cyclomatic(tree)
            functions = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
            classes = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
        except SyntaxError: pass
    else:
        cyclomatic = 1 + len(re.findall(r"\b(if|else if|elif|for|while|case|catch|&&|\|\|)\b", code))
        functions = len(re.findall(r"\b(function|def|func|fn)\b", code))
        classes = len(re.findall(r"\b(class|struct|interface|trait)\b", code))
    comment_ratio = comment / total if total > 0 else 0.0
    mi = maintainability_index(halstead["volume"], cyclomatic, logical, comment_ratio)
    return ComplexityMetrics(cyclomatic=cyclomatic, cognitive=cyclomatic, lines_of_code=total,
                             logical_lines=logical, comment_lines=comment, blank_lines=blank,
                             functions=functions, classes=classes, max_nesting=max_nesting,
                             maintainability_index=mi, halstead_volume=halstead["volume"],
                             halstead_difficulty=halstead["difficulty"])


def compare_metrics(old: ComplexityMetrics, new: ComplexityMetrics) -> dict[str, Any]:
    return {"cyclomatic_delta": new.cyclomatic - old.cyclomatic,
            "lines_delta": new.lines_of_code - old.lines_of_code,
            "functions_delta": new.functions - old.functions,
            "maintainability_delta": round(new.maintainability_index - old.maintainability_index, 2)}
