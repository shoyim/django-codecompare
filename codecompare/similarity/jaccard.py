"""Jaccard similarity for set-based code comparison."""
from __future__ import annotations
from collections import Counter


def _shingles(text: str, k: int = 3) -> set[str]:
    return {text[i:i+k] for i in range(len(text) - k + 1)}


def _token_shingles(tokens: list[str], k: int = 2) -> set[tuple[str, ...]]:
    return {tuple(tokens[i:i+k]) for i in range(len(tokens) - k + 1)}


def jaccard(set_a: set, set_b: set) -> float:
    if not set_a and not set_b: return 1.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union else 0.0


def jaccard_multiset(a: list, b: list) -> float:
    ca, cb = Counter(a), Counter(b)
    intersection = sum((ca & cb).values())
    union = sum((ca | cb).values())
    return intersection / union if union else 0.0


class JaccardSimilarity:
    def __init__(self, shingle_size: int = 3) -> None:
        self.shingle_size = shingle_size

    def score(self, a: str, b: str) -> float:
        if a == b: return 1.0
        return jaccard(_shingles(a, self.shingle_size), _shingles(b, self.shingle_size))

    def token_score(self, ta: list[str], tb: list[str]) -> float:
        if ta == tb: return 1.0
        return jaccard(_token_shingles(ta, 2), _token_shingles(tb, 2))

    def bag_score(self, ta: list[str], tb: list[str]) -> float:
        return jaccard_multiset(ta, tb)
