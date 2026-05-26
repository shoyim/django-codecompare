"""Main comparison service — orchestrates the full pipeline."""
from __future__ import annotations
import hashlib, time
from typing import Any
from codecompare.analyzers import complexity as complexity_analyzer
from codecompare.analyzers.duplicates import cross_file_duplicates
from codecompare.ast_engine.ast_comparator import compare_ast
from codecompare.core.types import (ChangeStatistics, ComparisonResult, PlagiarismIndicators, SimilarityScores)
from codecompare.diff_engine.myers import MyersDiff
from codecompare.parsers.language_detector import detect_str
from codecompare.semantic_engine import fingerprinting, plagiarism
from codecompare.semantic_engine.rename_detector import detect_renames
from codecompare.similarity.aggregator import aggregate
from codecompare.similarity.cosine import CosineSimilarity
from codecompare.similarity.jaccard import JaccardSimilarity
from codecompare.similarity.levenshtein import LevenshteinSimilarity
from codecompare.similarity.token_similarity import TokenSimilarity


class ComparisonService:
    def __init__(self) -> None:
        self._diff = MyersDiff()
        self._lev = LevenshteinSimilarity()
        self._cos = CosineSimilarity()
        self._jac = JaccardSimilarity()
        self._tok = TokenSimilarity()

    def compare(self, old_code: str, new_code: str, language: str | None = None, options: dict | None = None) -> ComparisonResult:
        opts = options or {}
        t_start = time.perf_counter()
        lang = language or detect_str(old_code)

        old_parsed = self._parse(old_code, lang)
        new_parsed = self._parse(new_code, lang)
        old_tokens = [t.normalized for t in (old_parsed.tokens if old_parsed else [])]
        new_tokens = [t.normalized for t in (new_parsed.tokens if new_parsed else [])]

        old_lines = old_code.splitlines()
        new_lines = new_code.splitlines()
        diff_result = self._diff.diff(old_lines, new_lines)

        lev_score = self._lev.score(old_code, new_code)
        cos_score = self._cos.score(old_code, new_code)
        jac_score = self._jac.score(old_code, new_code)
        tok_score = self._tok.token_score(old_tokens, new_tokens)

        ast_result: dict[str, Any] = {}
        ast_score = 0.0
        try:
            ast_result = compare_ast(old_code, new_code, lang)
            ast_score = ast_result.get("similarity", 0.0) / 100.0
        except Exception:
            pass

        fp_sim = fingerprinting.code_similarity(old_code, new_code)
        plag_report = plagiarism.analyse(old_code, new_code)
        plag_indicators = PlagiarismIndicators(
            is_plagiarism_suspected=plag_report["is_plagiarism_suspected"],
            confidence=plag_report["confidence"],
            matching_blocks=plag_report["matching_blocks"],
            structural_fingerprint_match=plag_report["structural_similarity"],
            whitespace_stripped_similarity=plag_report["whitespace_stripped_similarity"],
        )

        try: renamed = detect_renames(old_code, new_code, lang); plag_indicators.renamed_identifiers = renamed
        except Exception: renamed = []

        old_metrics = complexity_analyzer.analyse(old_code, lang)
        new_metrics = complexity_analyzer.analyse(new_code, lang)
        complexity_delta = new_metrics.cyclomatic - old_metrics.cyclomatic

        stats = self._build_stats(old_lines, new_lines, diff_result, old_tokens, new_tokens, ast_result, renamed, complexity_delta)
        scores = aggregate(levenshtein=lev_score, cosine=cos_score, jaccard=jac_score, token=tok_score,
                           ast=ast_score, semantic=fp_sim, structural=ast_score, logic=tok_score)
        cross_dups = cross_file_duplicates(old_tokens, new_tokens, min_chunk=8)
        elapsed_ms = (time.perf_counter() - t_start) * 1000

        result = ComparisonResult(
            language=lang, similarity=scores, diff=diff_result, ast_diff=ast_result,
            statistics=stats, old_complexity=old_metrics, new_complexity=new_metrics,
            plagiarism=plag_indicators,
            metadata={"old_hash": hashlib.sha256(old_code.encode()).hexdigest()[:16],
                      "new_hash": hashlib.sha256(new_code.encode()).hexdigest()[:16],
                      "duplicate_blocks": cross_dups[:10], "renamed_identifiers": renamed},
            processing_time_ms=round(elapsed_ms, 2),
        )
        if opts.get("warnings", True): result.warnings = self._warnings(result)
        return result

    def _parse(self, code: str, language: str):
        try:
            from codecompare.core.registry import parser_registry, load_default_plugins
            load_default_plugins()
            return parser_registry.get_plugin(language).parse(code)
        except Exception: return None

    def _build_stats(self, old_lines, new_lines, diff_result, old_tokens, new_tokens, ast_result, renamed, complexity_delta) -> ChangeStatistics:
        stats = ChangeStatistics(
            lines_added=diff_result.added, lines_removed=diff_result.removed, lines_equal=diff_result.equal,
            tokens_added=max(0, len(new_tokens) - len(old_tokens)),
            tokens_removed=max(0, len(old_tokens) - len(new_tokens)),
            renamed_symbols=renamed, complexity_delta=complexity_delta,
            chars_added=max(0, sum(len(l) for l in new_lines) - sum(len(l) for l in old_lines)),
            chars_removed=max(0, sum(len(l) for l in old_lines) - sum(len(l) for l in new_lines)),
        )
        changes = ast_result.get("changes", {})
        if changes:
            stats.functions_added = changes.get("functions", {}).get("added", [])
            stats.functions_removed = changes.get("functions", {}).get("removed", [])
            stats.functions_changed = changes.get("functions", {}).get("changed", [])
            stats.classes_added = changes.get("classes", {}).get("added", [])
            stats.classes_removed = changes.get("classes", {}).get("removed", [])
            stats.classes_changed = changes.get("classes", {}).get("changed", [])
            stats.imports_added = changes.get("imports", {}).get("added", [])
            stats.imports_removed = changes.get("imports", {}).get("removed", [])
        return stats

    def _warnings(self, result: ComparisonResult) -> list[str]:
        w = []
        if result.similarity.overall > 95: w.append("Very high similarity — possible duplicate.")
        if result.new_complexity.cyclomatic > 20: w.append(f"High cyclomatic complexity ({result.new_complexity.cyclomatic}).")
        if result.new_complexity.maintainability_index < 20: w.append("Low maintainability index.")
        if result.plagiarism.is_plagiarism_suspected: w.append(f"Plagiarism suspected ({result.plagiarism.confidence:.1f}% confidence).")
        return w


_svc: ComparisonService | None = None


def get_comparison_service() -> ComparisonService:
    global _svc
    if _svc is None: _svc = ComparisonService()
    return _svc


def compare(old_code: str, new_code: str, language: str | None = None, **kwargs: Any) -> ComparisonResult:
    return get_comparison_service().compare(old_code, new_code, language, kwargs)
