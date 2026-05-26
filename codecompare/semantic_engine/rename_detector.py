"""Renamed variable/function/class detector."""
from __future__ import annotations
import ast, re
from collections import Counter
from difflib import SequenceMatcher
from typing import Any


def _extract_python_identifiers(code: str) -> list[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return re.findall(r"\b[a-zA-Z_]\w+\b", code)
    ids: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name): ids.append(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)): ids.append(node.name)
        elif isinstance(node, ast.arg): ids.append(node.arg)
    return ids


def detect_renames(old_code: str, new_code: str, language: str = "python") -> list[dict[str, str]]:
    extract = _extract_python_identifiers if language == "python" else lambda c: re.findall(r"\b[a-zA-Z_]\w+\b", c)
    old_ids, new_ids = extract(old_code), extract(new_code)
    old_counts, new_counts = Counter(old_ids), Counter(new_ids)
    old_unique = set(old_counts) - set(new_counts)
    new_unique = set(new_counts) - set(old_counts)
    renames: list[dict[str, str]] = []
    for old_name in old_unique:
        best_match, best_score = None, 0.0
        for new_name in new_unique:
            name_sim = SequenceMatcher(None, old_name, new_name).ratio()
            old_freq, new_freq = old_counts[old_name], new_counts[new_name]
            freq_sim = min(old_freq, new_freq) / max(old_freq, new_freq)
            combined = 0.6 * freq_sim + 0.4 * name_sim
            if combined > best_score: best_score = combined; best_match = new_name
        if best_match and best_score > 0.5:
            renames.append({"old_name": old_name, "new_name": best_match, "confidence": round(best_score * 100, 1)})
    return renames
