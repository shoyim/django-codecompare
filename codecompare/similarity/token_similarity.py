"""Token-level similarity using normalised token sequences."""
from __future__ import annotations
import difflib


class TokenSimilarity:
    def score(self, a: str, b: str) -> float:
        return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()

    def token_score(self, ta: list[str], tb: list[str]) -> float:
        if not ta and not tb: return 1.0
        if not ta or not tb: return 0.0
        return difflib.SequenceMatcher(None, ta, tb, autojunk=False).ratio()

    def longest_common_subsequence_ratio(self, a: list[str], b: list[str]) -> float:
        if not a and not b: return 1.0
        m, n = len(a), len(b)
        dp = [0] * (n + 1)
        for i in range(1, m + 1):
            prev = 0
            for j in range(1, n + 1):
                temp = dp[j]
                dp[j] = prev + 1 if a[i-1] == b[j-1] else max(dp[j], dp[j-1])
                prev = temp
        return dp[n] / max(m, n)
