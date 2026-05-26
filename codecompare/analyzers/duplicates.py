"""Duplicated logic detection using token hashing."""
from __future__ import annotations
import hashlib
from collections import defaultdict
from typing import Any


def find_duplicates(tokens: list[str], min_chunk: int = 10) -> list[dict[str, Any]]:
    hash_positions: dict[str, list[int]] = defaultdict(list)
    for i in range(len(tokens) - min_chunk + 1):
        h = hashlib.md5(" ".join(tokens[i:i+min_chunk]).encode()).hexdigest()
        hash_positions[h].append(i)
    dups = []
    for h, positions in hash_positions.items():
        if len(positions) >= 2:
            dups.append({"hash": h[:8], "occurrences": len(positions), "token_positions": positions,
                         "sample": " ".join(tokens[positions[0]:positions[0]+5]) + "...", "length": min_chunk})
    dups.sort(key=lambda d: -d["occurrences"])
    return dups


def cross_file_duplicates(ta: list[str], tb: list[str], min_chunk: int = 8) -> list[dict[str, Any]]:
    hashes_b = set()
    for i in range(len(tb) - min_chunk + 1):
        hashes_b.add(hashlib.md5(" ".join(tb[i:i+min_chunk]).encode()).hexdigest())
    dups, seen = [], set()
    for i in range(len(ta) - min_chunk + 1):
        h = hashlib.md5(" ".join(ta[i:i+min_chunk]).encode()).hexdigest()
        if h in hashes_b and h not in seen:
            seen.add(h)
            block = ta[i:i+min_chunk]
            dups.append({"hash": h[:8], "a_start": i, "length": min_chunk,
                         "sample": " ".join(block[:8]) + ("..." if len(block) > 8 else "")})
    return dups
