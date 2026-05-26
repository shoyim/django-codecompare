"""Automatic language detection from extension, shebang, and syntax heuristics."""
from __future__ import annotations
import re
from pathlib import Path
from codecompare.core.types import Language

_EXT_MAP: dict[str, Language] = {
    ".py": Language.PYTHON, ".pyw": Language.PYTHON,
    ".js": Language.JAVASCRIPT, ".mjs": Language.JAVASCRIPT, ".cjs": Language.JAVASCRIPT,
    ".ts": Language.TYPESCRIPT, ".jsx": Language.JSX, ".tsx": Language.TSX,
    ".java": Language.JAVA, ".c": Language.C, ".h": Language.C,
    ".cpp": Language.CPP, ".cc": Language.CPP, ".cxx": Language.CPP, ".hpp": Language.CPP,
    ".cs": Language.CSHARP, ".go": Language.GO, ".rs": Language.RUST,
    ".kt": Language.KOTLIN, ".kts": Language.KOTLIN, ".swift": Language.SWIFT,
    ".dart": Language.DART, ".rb": Language.RUBY, ".scala": Language.SCALA,
    ".sh": Language.BASH, ".bash": Language.BASH, ".zsh": Language.BASH,
    ".sql": Language.SQL, ".html": Language.HTML, ".htm": Language.HTML,
    ".css": Language.CSS, ".scss": Language.CSS, ".sass": Language.CSS,
    ".php": Language.PHP, ".vue": Language.VUE,
}

_CONTENT_HEURISTICS: list[tuple[re.Pattern, Language, int]] = [
    (re.compile(r"^(def |class |import |from .+ import|if __name__)"), Language.PYTHON, 3),
    (re.compile(r"^(function |const |let |var |=>|require\(|module\.exports)"), Language.JAVASCRIPT, 2),
    (re.compile(r"^(interface |type |enum |namespace )"), Language.TYPESCRIPT, 2),
    (re.compile(r"^(public class |@Override|System\.out)"), Language.JAVA, 3),
    (re.compile(r"^(fn |let mut |impl |use std::|#\[derive)"), Language.RUST, 3),
    (re.compile(r"^(func |package |import \")"), Language.GO, 3),
    (re.compile(r"^(#include|int main\(|std::|cout)"), Language.CPP, 3),
    (re.compile(r"^(using namespace|namespace |Console\.Write)"), Language.CSHARP, 3),
    (re.compile(r"^(<\?php|namespace .+;|\$[a-z])"), Language.PHP, 3),
    (re.compile(r"^(fun |val |data class)"), Language.KOTLIN, 3),
    (re.compile(r"^(SELECT |INSERT |UPDATE |DELETE |CREATE TABLE)", re.I), Language.SQL, 3),
    (re.compile(r"^<!DOCTYPE|^<html|^<head"), Language.HTML, 3),
    (re.compile(r"^(<template>|<script setup|<style scoped)"), Language.VUE, 3),
    (re.compile(r"^(#!/|set -e|echo |grep )"), Language.BASH, 2),
]


def from_extension(path: str) -> Language:
    return _EXT_MAP.get(Path(path).suffix.lower(), Language.UNKNOWN)


def from_content(code: str, max_lines: int = 30) -> Language:
    scores: dict[Language, int] = {}
    for line in [l.strip() for l in code.splitlines()[:max_lines] if l.strip()]:
        for pattern, lang, weight in _CONTENT_HEURISTICS:
            if pattern.search(line):
                scores[lang] = scores.get(lang, 0) + weight
    return max(scores, key=lambda k: scores[k]) if scores else Language.UNKNOWN


def detect(code: str, filename: str | None = None, hint: str | None = None) -> Language:
    if hint:
        try: return Language(hint.lower())
        except ValueError: pass
    if filename:
        lang = from_extension(filename)
        if lang != Language.UNKNOWN: return lang
    return from_content(code)


def detect_str(code: str, filename: str | None = None, hint: str | None = None) -> str:
    return detect(code, filename, hint).value
