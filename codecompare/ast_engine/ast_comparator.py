"""Language-agnostic AST comparator."""
from __future__ import annotations
from typing import Any
from codecompare.core.types import Language


def compare_ast(old_code: str, new_code: str, language: str) -> dict[str, Any]:
    lang = language.lower()
    if lang == Language.PYTHON:
        from codecompare.ast_engine.python_ast import ast_similarity, compare_summaries, extract
        old_s, new_s = extract(old_code), extract(new_code)
        return {
            "similarity": round(ast_similarity(old_s, new_s) * 100, 2),
            "changes": compare_summaries(old_s, new_s),
            "old_functions": len(old_s.functions), "new_functions": len(new_s.functions),
            "old_classes": len(old_s.classes), "new_classes": len(new_s.classes),
            "parse_errors": {"old": old_s.parse_error, "new": new_s.parse_error},
        }
    try:
        from codecompare.ast_engine.treesitter_engine import TreeSitterEngine
        return TreeSitterEngine().compare(old_code, new_code, language)
    except ImportError:
        pass
    old_lines = [l.strip() for l in old_code.splitlines() if l.strip()]
    new_lines = [l.strip() for l in new_code.splitlines() if l.strip()]
    common = set(old_lines) & set(new_lines)
    union = set(old_lines) | set(new_lines)
    sim = len(common) / len(union) if union else 1.0
    return {"similarity": round(sim * 100, 2), "changes": {}, "note": "Generic approximation"}
