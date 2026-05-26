"""Performance benchmarks for the comparison pipeline."""
from __future__ import annotations
import pytest
from codecompare.core.services import compare
from codecompare.diff_engine.myers import MyersDiff
from codecompare.similarity.levenshtein import wagner_fischer, normalised_similarity
from codecompare.similarity.cosine import CosineSimilarity
from codecompare.similarity.jaccard import JaccardSimilarity

SMALL = "def foo(x):\n    return x + 1\n" * 5
MEDIUM = "def foo(x):\n    return x + 1\n" * 100
LARGE = "def foo(x):\n    return x + 1\n" * 1000

SMALL_LINES = SMALL.splitlines()
MEDIUM_LINES = MEDIUM.splitlines()
LARGE_LINES = LARGE.splitlines()


@pytest.mark.benchmark(group="diff")
class TestMyersDiffBenchmarks:
    def test_small(self, benchmark):
        engine = MyersDiff()
        benchmark(engine.diff, SMALL_LINES, SMALL_LINES)

    def test_medium(self, benchmark):
        engine = MyersDiff()
        benchmark(engine.diff, MEDIUM_LINES, MEDIUM_LINES)

    def test_large(self, benchmark):
        engine = MyersDiff()
        benchmark(engine.diff, LARGE_LINES, LARGE_LINES)


@pytest.mark.benchmark(group="levenshtein")
class TestLevenshteinBenchmarks:
    def test_small(self, benchmark):
        benchmark(normalised_similarity, SMALL, SMALL)

    def test_medium(self, benchmark):
        benchmark(normalised_similarity, MEDIUM[:5000], MEDIUM[:5000])


@pytest.mark.benchmark(group="cosine")
class TestCosineBenchmarks:
    def test_small(self, benchmark):
        engine = CosineSimilarity()
        benchmark(engine.score, SMALL, SMALL)

    def test_medium(self, benchmark):
        engine = CosineSimilarity()
        benchmark(engine.score, MEDIUM, MEDIUM)


@pytest.mark.benchmark(group="jaccard")
class TestJaccardBenchmarks:
    def test_small(self, benchmark):
        engine = JaccardSimilarity()
        benchmark(engine.score, SMALL, SMALL)


@pytest.mark.benchmark(group="pipeline")
class TestPipelineBenchmarks:
    def test_small_pipeline(self, benchmark):
        benchmark(compare, SMALL, SMALL, "python")

    def test_medium_pipeline(self, benchmark):
        benchmark(compare, MEDIUM, MEDIUM, "python")
