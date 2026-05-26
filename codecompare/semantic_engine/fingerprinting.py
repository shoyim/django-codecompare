"""Semantic fingerprinting using Rabin-Karp rolling hash + Winnowing."""
from __future__ import annotations
import re

_PRIME, _BASE = 101, 256
_WINNOW_K, _WINNOW_W = 5, 4


def _normalise_and_tokenise(code: str) -> list[str]:
    code = re.sub(r"(//.*|#.*|--.*)", "", code)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return [t.lower() for t in re.findall(r"[a-zA-Z_]\w*|\d+|[^\w\s]", code)]


def _rolling_hash(tokens: list[str], k: int) -> list[int]:
    if len(tokens) < k: return []
    h_power = pow(_BASE, k - 1, _PRIME)
    h = 0
    for i in range(k):
        h = (h * _BASE + abs(hash(tokens[i])) % _PRIME) % _PRIME
    hashes = [h]
    for i in range(1, len(tokens) - k + 1):
        old_val = abs(hash(tokens[i-1])) % _PRIME
        new_val = abs(hash(tokens[i+k-1])) % _PRIME
        h = (h - old_val * h_power % _PRIME + _PRIME) % _PRIME
        h = (h * _BASE + new_val) % _PRIME
        hashes.append(h)
    return hashes


def winnow(tokens: list[str], k: int = _WINNOW_K, w: int = _WINNOW_W) -> set[int]:
    kgram_hashes = _rolling_hash(tokens, k)
    if not kgram_hashes: return set()
    fp: set[int] = set()
    for i in range(len(kgram_hashes) - w + 1):
        fp.add(min(kgram_hashes[i:i+w]))
    return fp


def fingerprint_similarity(fp_a: set[int], fp_b: set[int]) -> float:
    if not fp_a and not fp_b: return 1.0
    inter = len(fp_a & fp_b)
    union = len(fp_a | fp_b)
    return inter / union if union else 0.0


def compute_fingerprint(code: str) -> set[int]:
    return winnow(_normalise_and_tokenise(code))


def code_similarity(code_a: str, code_b: str) -> float:
    return fingerprint_similarity(compute_fingerprint(code_a), compute_fingerprint(code_b))


def find_matching_blocks(code_a: str, code_b: str, min_block_tokens: int = 5) -> list[dict]:
    ta = _normalise_and_tokenise(code_a)
    tb = _normalise_and_tokenise(code_b)
    k = min_block_tokens
    if len(ta) < k or len(tb) < k: return []
    hashes_b: dict[int, list[int]] = {}
    for i, h in enumerate(_rolling_hash(tb, k)): hashes_b.setdefault(h, []).append(i)
    matches = []
    for i, h in enumerate(_rolling_hash(ta, k)):
        if h in hashes_b:
            for j in hashes_b[h]:
                if ta[i:i+k] == tb[j:j+k]:
                    matches.append({"a_token_start": i, "b_token_start": j, "length": k, "tokens": ta[i:i+k]})
    matches.sort(key=lambda m: (m["a_token_start"], m["b_token_start"]))
    merged, seen = [], set()
    for m in matches:
        key = (m["a_token_start"], m["b_token_start"])
        if key not in seen: seen.add(key); merged.append(m)
    return merged
