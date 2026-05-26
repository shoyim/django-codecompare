"""Cosine similarity with TF-IDF weighting."""
from __future__ import annotations
import math, re
from collections import Counter


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z_]\w*|\d+|[^\w\s]", text)


def tf(tokens: list[str]) -> dict[str, float]:
    total = len(tokens)
    if total == 0: return {}
    counts = Counter(tokens)
    return {t: c / total for t, c in counts.items()}


def idf(documents: list[list[str]]) -> dict[str, float]:
    n = len(documents)
    term_doc = Counter()
    for doc in documents:
        for term in set(doc): term_doc[term] += 1
    return {t: math.log((1 + n) / (1 + c)) + 1.0 for t, c in term_doc.items()}


def tfidf_vector(tokens: list[str], idf_weights: dict[str, float]) -> dict[str, float]:
    tf_scores = tf(tokens)
    return {t: s * idf_weights.get(t, 1.0) for t, s in tf_scores.items()}


def cosine(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    common = set(vec_a) & set(vec_b)
    if not common: return 0.0
    dot = sum(vec_a[t] * vec_b[t] for t in common)
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))
    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0


class CosineSimilarity:
    def score(self, a: str, b: str) -> float:
        ta, tb = _tokenize(a), _tokenize(b)
        if not ta and not tb: return 1.0
        if not ta or not tb: return 0.0
        idf_w = idf([ta, tb])
        return cosine(tfidf_vector(ta, idf_w), tfidf_vector(tb, idf_w))

    def token_score(self, ta: list[str], tb: list[str]) -> float:
        if not ta and not tb: return 1.0
        if not ta or not tb: return 0.0
        idf_w = idf([ta, tb])
        return cosine(tfidf_vector(ta, idf_w), tfidf_vector(tb, idf_w))
