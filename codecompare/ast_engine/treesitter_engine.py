"""Tree-sitter based multi-language AST engine."""
from __future__ import annotations
import hashlib, importlib, logging
from typing import Any
logger = logging.getLogger(__name__)

_GRAMMAR_MAP = {
    "python": ("tree_sitter_python", "language"),
    "javascript": ("tree_sitter_javascript", "language"),
    "typescript": ("tree_sitter_typescript", "language_typescript"),
    "java": ("tree_sitter_java", "language"), "go": ("tree_sitter_go", "language"),
    "rust": ("tree_sitter_rust", "language"), "cpp": ("tree_sitter_cpp", "language"),
    "c": ("tree_sitter_c", "language"), "ruby": ("tree_sitter_ruby", "language"),
    "php": ("tree_sitter_php", "language_php"), "bash": ("tree_sitter_bash", "language"),
    "html": ("tree_sitter_html", "language"), "css": ("tree_sitter_css", "language"),
}


class TreeSitterEngine:
    def __init__(self) -> None: self._parsers: dict[str, Any] = {}

    def _get_parser(self, language: str):
        if language in self._parsers: return self._parsers[language]
        try:
            from tree_sitter import Language as TSLanguage, Parser
        except ImportError as exc:
            raise ImportError("tree-sitter not installed: pip install tree-sitter") from exc
        grammar_info = _GRAMMAR_MAP.get(language.lower())
        if not grammar_info: raise ValueError(f"No grammar for language: {language}")
        module_name, attr_name = grammar_info
        try:
            mod = importlib.import_module(module_name)
            ts_lang = TSLanguage(getattr(mod, attr_name)())
            parser = Parser(ts_lang)
            self._parsers[language] = parser
            return parser
        except (ImportError, AttributeError) as exc:
            raise ImportError(f"Tree-sitter grammar for '{language}' not installed: pip install {module_name}") from exc

    def parse(self, code: str, language: str) -> Any:
        return self._get_parser(language).parse(code.encode())

    def compare(self, old_code: str, new_code: str, language: str) -> dict[str, Any]:
        try:
            old_tree = self.parse(old_code, language)
            new_tree = self.parse(new_code, language)
        except (ImportError, ValueError) as exc:
            return {"error": str(exc), "similarity": 0.0}
        old_sig = self._tree_signature(old_tree.root_node)
        new_sig = self._tree_signature(new_tree.root_node)
        all_types = set(old_sig) | set(new_sig)
        common = sum(min(old_sig.get(t, 0), new_sig.get(t, 0)) for t in all_types)
        total = sum(max(old_sig.get(t, 0), new_sig.get(t, 0)) for t in all_types)
        sim = common / total if total else 1.0
        return {"similarity": round(sim * 100, 2), "old_node_types": old_sig, "new_node_types": new_sig,
                "changes": {"added_types": {t: new_sig[t] for t in new_sig if t not in old_sig},
                            "removed_types": {t: old_sig[t] for t in old_sig if t not in new_sig}}}

    def _tree_signature(self, node) -> dict[str, int]:
        counts: dict[str, int] = {}
        def _walk(n):
            counts[n.type] = counts.get(n.type, 0) + 1
            for child in n.children: _walk(child)
        _walk(node)
        return counts
