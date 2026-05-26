"""Levenshtein / Wagner-Fischer edit distance and similarity."""
from __future__ import annotations


def wagner_fischer(s1: str, s2: str) -> int:
    m, n = len(s1), len(s2)
    if m == 0: return n
    if n == 0: return m
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]; dp[0] = i
        for j in range(1, n + 1):
            temp = dp[j]
            dp[j] = prev if s1[i-1] == s2[j-1] else 1 + min(prev, dp[j], dp[j-1])
            prev = temp
    return dp[n]


def damerau_levenshtein(s1: str, s2: str) -> int:
    m, n = len(s1), len(s2)
    if m == 0: return n
    if n == 0: return m
    d = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): d[i][0] = i
    for j in range(n + 1): d[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + cost)
            if i > 1 and j > 1 and s1[i-1] == s2[j-2] and s1[i-2] == s2[j-1]:
                d[i][j] = min(d[i][j], d[i-2][j-2] + cost)
    return d[m][n]


def normalised_similarity(s1: str, s2: str, *, use_damerau: bool = False) -> float:
    if not s1 and not s2: return 1.0
    if not s1 or not s2: return 0.0
    if s1 == s2: return 1.0
    dist_fn = damerau_levenshtein if use_damerau else wagner_fischer
    return 1.0 - dist_fn(s1, s2) / max(len(s1), len(s2))


def token_edit_similarity(tokens_a: list[str], tokens_b: list[str]) -> float:
    if not tokens_a and not tokens_b: return 1.0
    if not tokens_a or not tokens_b: return 0.0
    if tokens_a == tokens_b: return 1.0
    m, n = len(tokens_a), len(tokens_b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]; dp[0] = i
        for j in range(1, n + 1):
            temp = dp[j]
            dp[j] = prev if tokens_a[i-1] == tokens_b[j-1] else 1 + min(prev, dp[j], dp[j-1])
            prev = temp
    return 1.0 - dp[n] / max(m, n)


class LevenshteinSimilarity:
    def score(self, a: str, b: str) -> float: return normalised_similarity(a, b)
    def token_score(self, a: list[str], b: list[str]) -> float: return token_edit_similarity(a, b)
    def distance(self, a: str, b: str) -> int: return wagner_fischer(a, b)
