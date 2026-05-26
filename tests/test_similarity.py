"""Tests for all similarity engines."""
from __future__ import annotations
import pytest
from codecompare.similarity.levenshtein import LevenshteinSimilarity, damerau_levenshtein, normalised_similarity, wagner_fischer
from codecompare.similarity.cosine import CosineSimilarity
from codecompare.similarity.jaccard import JaccardSimilarity, jaccard
from codecompare.similarity.token_similarity import TokenSimilarity
from codecompare.similarity.aggregator import aggregate


class TestWagnerFischer:
    def test_identical(self): assert wagner_fischer("abc", "abc") == 0
    def test_empty(self): assert wagner_fischer("", "") == 0 and wagner_fischer("abc", "") == 3
    def test_one_substitution(self): assert wagner_fischer("abc", "axc") == 1
    def test_kitten_sitting(self): assert wagner_fischer("kitten", "sitting") == 3
    def test_symmetric(self): assert wagner_fischer("hello", "world") == wagner_fischer("world", "hello")


class TestDamerau:
    def test_transposition(self): assert damerau_levenshtein("ab", "ba") == 1
    def test_identical(self): assert damerau_levenshtein("abc", "abc") == 0


class TestNormalised:
    def test_identical(self): assert normalised_similarity("abc", "abc") == 1.0
    def test_both_empty(self): assert normalised_similarity("", "") == 1.0
    def test_range(self): assert 0.0 <= normalised_similarity("hello", "world") <= 1.0


class TestCosine:
    def test_identical(self):
        code = "def foo(x): return x + 1"
        assert CosineSimilarity().score(code, code) == pytest.approx(1.0, abs=0.01)
    def test_empty(self): assert CosineSimilarity().score("", "") == 1.0


class TestJaccard:
    def test_identical(self): assert JaccardSimilarity().score("hello", "hello") == 1.0
    def test_empty_sets(self): assert jaccard(set(), set()) == 1.0
    def test_disjoint(self): assert jaccard({"a"}, {"b"}) == 0.0
    def test_partial(self): assert jaccard({"a", "b"}, {"b", "c"}) == pytest.approx(1/3, abs=0.01)


class TestTokenSim:
    def test_identical(self): assert TokenSimilarity().token_score(["a", "b"], ["a", "b"]) == 1.0
    def test_lcs(self):
        r = TokenSimilarity().longest_common_subsequence_ratio(["a", "b", "c"], ["a", "c"])
        assert r == pytest.approx(2/3, abs=0.01)


class TestAggregator:
    def test_all_ones(self):
        s = aggregate(levenshtein=1.0, cosine=1.0, jaccard=1.0, token=1.0, ast=1.0)
        assert s.overall == pytest.approx(100.0, abs=1.0)
    def test_all_zeros(self):
        s = aggregate(levenshtein=0.0, cosine=0.0, jaccard=0.0, token=0.0, ast=0.0)
        assert s.overall == 0.0
