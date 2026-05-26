"""Tests for the Myers diff engine."""
from __future__ import annotations
import pytest
from codecompare.diff_engine.myers import MyersDiff, side_by_side_diff, unified_diff
from codecompare.core.types import ChangeType, DiffMode


@pytest.fixture
def engine() -> MyersDiff:
    return MyersDiff()


class TestMyersDiff:
    def test_identical(self, engine):
        r = engine.diff(["a", "b", "c"], ["a", "b", "c"])
        assert r.added == 0 and r.removed == 0 and r.equal == 3

    def test_single_insertion(self, engine):
        r = engine.diff(["a", "b"], ["a", "x", "b"])
        assert r.added == 1 and r.removed == 0

    def test_single_deletion(self, engine):
        r = engine.diff(["a", "b", "c"], ["a", "c"])
        assert r.removed == 1 and r.added == 0

    def test_complete_change(self, engine):
        r = engine.diff(["a", "b"], ["c", "d"])
        assert r.added == 2 and r.removed == 2

    def test_empty_old(self, engine):
        r = engine.diff([], ["a", "b", "c"])
        assert r.added == 3 and r.removed == 0

    def test_empty_new(self, engine):
        r = engine.diff(["a", "b"], [])
        assert r.removed == 2 and r.added == 0

    def test_both_empty(self, engine):
        r = engine.diff([], [])
        assert r.added == 0 and r.removed == 0

    def test_mode_is_line(self, engine):
        assert engine.diff(["a"], ["b"]).mode == DiffMode.LINE

    def test_word_diff(self, engine):
        r = engine.word_diff("hello world", "hello Python")
        assert r.mode == DiffMode.WORD and r.added >= 1

    def test_inline_diff_equal(self, engine):
        tokens = engine.inline_diff("abc", "abc")
        assert all(t[0] == ChangeType.EQUAL for t in tokens)

    def test_inline_diff_change(self, engine):
        tokens = engine.inline_diff("abc", "axc")
        types = [t[0] for t in tokens]
        assert ChangeType.DELETE in types or ChangeType.INSERT in types


class TestUnifiedDiff:
    def test_produces_output(self):
        patch = unified_diff("a\nb\n", "a\nc\n")
        assert isinstance(patch, str)


class TestSideBySideDiff:
    def test_returns_rows(self):
        rows = side_by_side_diff("a\nb\n", "a\nc\n")
        assert isinstance(rows, list)
        for row in rows:
            assert "old" in row and "new" in row and "type" in row
