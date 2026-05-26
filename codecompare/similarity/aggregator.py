"""Aggregates multiple similarity scores into a composite result."""
from __future__ import annotations
from codecompare.core.types import SimilarityScores

_WEIGHTS = {"token": 0.30, "cosine": 0.20, "jaccard": 0.15, "levenshtein": 0.15, "ast": 0.20}


def aggregate(levenshtein: float = 0.0, cosine: float = 0.0, jaccard: float = 0.0,
              token: float = 0.0, ast: float = 0.0, semantic: float = 0.0,
              structural: float = 0.0, logic: float = 0.0) -> SimilarityScores:
    overall = min(1.0, max(0.0,
        _WEIGHTS["token"] * token + _WEIGHTS["cosine"] * cosine +
        _WEIGHTS["jaccard"] * jaccard + _WEIGHTS["levenshtein"] * levenshtein +
        _WEIGHTS["ast"] * ast))
    exact = min(levenshtein, token, jaccard) if all([levenshtein, token, jaccard]) else 0.0
    return SimilarityScores(
        overall=round(overall * 100, 2), exact=round(exact * 100, 2),
        semantic=round(semantic * 100, 2), structural=round(structural * 100, 2),
        token=round(token * 100, 2), logic=round(logic * 100, 2),
        levenshtein=round(levenshtein * 100, 2), jaccard=round(jaccard * 100, 2),
        cosine=round(cosine * 100, 2), ast=round(ast * 100, 2),
    )
