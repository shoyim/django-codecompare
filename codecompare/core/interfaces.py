"""Protocol definitions (interfaces) for the comparison engine."""
from __future__ import annotations
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Parser(Protocol):
    language: str
    extensions: list[str]

    def parse(self, code: str) -> Any: ...
    def tokenize(self, code: str) -> list: ...
    def get_ast(self, code: str) -> Any | None: ...
    def normalize(self, code: str) -> str: ...


@runtime_checkable
class DiffEngine(Protocol):
    def diff(self, old_lines: list[str], new_lines: list[str]) -> Any: ...
    def word_diff(self, old: str, new: str) -> Any: ...


@runtime_checkable
class SimilarityEngine(Protocol):
    def score(self, a: Any, b: Any) -> float: ...


@runtime_checkable
class Analyzer(Protocol):
    def analyze(self, parsed: Any) -> dict[str, Any]: ...


@runtime_checkable
class ComparisonService(Protocol):
    def compare(self, old_code: str, new_code: str, language: str | None = None, options: dict | None = None) -> Any: ...
