"""Tests for the Python AST engine."""
from __future__ import annotations
import pytest
from codecompare.ast_engine.python_ast import extract, compare_summaries, ast_similarity, _cyclomatic_complexity

SIMPLE = """\
def add(a, b): return a + b

class Calculator:
    def multiply(self, x, y): return x * y
"""

MODIFIED = """\
def add(a, b): return a + b

def subtract(a, b): return a - b

class Calculator:
    def multiply(self, x, y): return x * y
    def divide(self, x, y):
        if y == 0: raise ValueError
        return x / y
"""

BROKEN = "def oops(: pass"


class TestExtract:
    def test_functions(self): assert "add" in [f.name for f in extract(SIMPLE).functions]
    def test_classes(self): assert "Calculator" in [c.name for c in extract(SIMPLE).classes]
    def test_broken_syntax(self): s = extract(BROKEN); assert s.parse_error != ""
    def test_tree_hash_deterministic(self): assert extract(SIMPLE).tree_hash == extract(SIMPLE).tree_hash
    def test_tree_hash_differs(self): assert extract(SIMPLE).tree_hash != extract(MODIFIED).tree_hash
    def test_complexity_tracked(self):
        for fn in extract(SIMPLE).functions: assert fn.cyclomatic_complexity >= 1
    def test_imports(self):
        s = extract("import os\nfrom sys import argv\n")
        assert "os" in [i.module for i in s.imports]


class TestCompareSummaries:
    def test_added_function(self):
        diff = compare_summaries(extract(SIMPLE), extract(MODIFIED))
        assert "subtract" in diff["functions"]["added"]

    def test_no_changes_identical(self):
        diff = compare_summaries(extract(SIMPLE), extract(SIMPLE))
        assert diff["functions"]["added"] == [] and diff["functions"]["removed"] == []


class TestASTSimilarity:
    def test_identical(self): s = extract(SIMPLE); assert ast_similarity(s, s) == pytest.approx(1.0)
    def test_modified(self): assert 0.0 <= ast_similarity(extract(SIMPLE), extract(MODIFIED)) < 1.0
    def test_broken(self): assert ast_similarity(extract(BROKEN), extract(SIMPLE)) == 0.0


class TestCyclomatic:
    def test_simple(self):
        import ast
        tree = ast.parse("def foo(): return 1")
        assert _cyclomatic_complexity(tree) == 1

    def test_with_if(self):
        import ast
        tree = ast.parse("def foo(x):\n    if x:\n        return 1\n    return 0")
        assert _cyclomatic_complexity(tree) == 2
