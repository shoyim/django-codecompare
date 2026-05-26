"""Plagiarism detection engine combining multiple signals."""
from __future__ import annotations
import re
from typing import Any

PLAGIARISM_THRESHOLD = 0.70


def _strip_identifiers(code: str) -> str:
    return re.sub(r"\b[a-zA-Z_]\w*\b", "X", code)


def _strip_whitespace_and_comments(code: str) -> str:
    code = re.sub(r"(//.*|#.*|--.*)", "", code)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return re.sub(r"\s+", "", code)


def analyse(old_code: str, new_code: str) -> dict[str, Any]:
    from codecompare.semantic_engine.fingerprinting import code_similarity, find_matching_blocks
    from codecompare.similarity.levenshtein import normalised_similarity
    fp_sim = code_similarity(old_code, new_code)
    structural_sim = code_similarity(_strip_identifiers(old_code), _strip_identifiers(new_code))
    ws_sim = normalised_similarity(_strip_whitespace_and_comments(old_code), _strip_whitespace_and_comments(new_code))
    blocks = find_matching_blocks(old_code, new_code, min_block_tokens=6)
    confidence = fp_sim * 0.35 + structural_sim * 0.40 + ws_sim * 0.25
    return {
        "is_plagiarism_suspected": confidence >= PLAGIARISM_THRESHOLD,
        "confidence": round(confidence * 100, 2),
        "fingerprint_similarity": round(fp_sim * 100, 2),
        "structural_similarity": round(structural_sim * 100, 2),
        "whitespace_stripped_similarity": round(ws_sim * 100, 2),
        "matching_blocks": blocks[:20],
        "matching_block_count": len(blocks),
    }
