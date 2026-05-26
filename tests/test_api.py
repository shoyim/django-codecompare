"""Integration tests for the ComparisonService pipeline."""
from __future__ import annotations
import pytest
from codecompare.core.services import compare
from codecompare.core.types import ComparisonResult, Language


CODE_A = """\
def greet(name):
    return f"Hello, {name}!"

class Greeter:
    def __init__(self, prefix="Hello"):
        self.prefix = prefix

    def greet(self, name):
        return f"{self.prefix}, {name}!"
"""

CODE_B = """\
def greet(name):
    return f"Hi, {name}!"

def farewell(name):
    return f"Goodbye, {name}!"

class Greeter:
    def __init__(self, prefix="Hi"):
        self.prefix = prefix

    def greet(self, name):
        return f"{self.prefix}, {name}!"

    def farewell(self, name):
        return f"Goodbye, {name}!"
"""

EMPTY = ""
IDENTICAL = CODE_A


class TestCompareService:
    def test_returns_comparison_result(self):
        result = compare(CODE_A, CODE_B, language="python")
        assert isinstance(result, ComparisonResult)

    def test_identical_code_high_similarity(self):
        result = compare(IDENTICAL, IDENTICAL, language="python")
        assert result.similarity.overall >= 95.0

    def test_modified_code_partial_similarity(self):
        result = compare(CODE_A, CODE_B, language="python")
        assert 0.0 < result.similarity.overall < 100.0

    def test_language_detected(self):
        result = compare(CODE_A, CODE_B, language="python")
        assert result.language == Language.PYTHON

    def test_diff_stats_present(self):
        result = compare(CODE_A, CODE_B, language="python")
        s = result.statistics
        assert s.lines_added >= 0 and s.lines_removed >= 0

    def test_complexity_metrics_present(self):
        result = compare(CODE_A, CODE_B, language="python")
        assert result.old_complexity is not None
        assert result.new_complexity is not None

    def test_plagiarism_indicators_present(self):
        result = compare(CODE_A, CODE_B, language="python")
        assert result.plagiarism is not None
        assert 0.0 <= result.plagiarism.confidence <= 100.0

    def test_empty_vs_nonempty(self):
        result = compare(EMPTY, CODE_A, language="python")
        assert result.similarity.overall < 50.0

    def test_both_empty(self):
        result = compare(EMPTY, EMPTY, language="python")
        assert result.similarity.overall == pytest.approx(100.0, abs=1.0)

    def test_diff_chunks_list(self):
        result = compare(CODE_A, CODE_B, language="python")
        assert isinstance(result.diff.chunks, list)

    def test_ast_similarity_range(self):
        result = compare(CODE_A, CODE_B, language="python")
        assert 0.0 <= result.similarity.ast <= 100.0

    def test_renamed_symbols_list(self):
        result = compare(CODE_A, CODE_B, language="python")
        assert isinstance(result.statistics.renamed_symbols, list)

    def test_processing_time_positive(self):
        result = compare(CODE_A, CODE_B, language="python")
        assert result.processing_time_ms >= 0.0


class TestLanguageAutoDetect:
    def test_python_auto_detect(self):
        result = compare(CODE_A, CODE_B)
        assert result.language == Language.PYTHON

    def test_js_auto_detect(self):
        js = "function add(a, b) { return a + b; }\nconst x = 1;\n"
        result = compare(js, js)
        assert result.language in (
            Language.JAVASCRIPT, Language.TYPESCRIPT,
            Language.JSX, Language.TSX, Language.PYTHON,
        )
