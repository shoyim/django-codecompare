"""Shared type definitions used across the entire package."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    C = "c"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    KOTLIN = "kotlin"
    SWIFT = "swift"
    DART = "dart"
    RUBY = "ruby"
    SCALA = "scala"
    BASH = "bash"
    SQL = "sql"
    HTML = "html"
    CSS = "css"
    PHP = "php"
    VUE = "vue"
    JSX = "jsx"
    TSX = "tsx"
    UNKNOWN = "unknown"


class ChangeType(str, Enum):
    EQUAL = "equal"
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"


class DiffMode(str, Enum):
    LINE = "line"
    WORD = "word"
    TOKEN = "token"
    AST = "ast"
    SEMANTIC = "semantic"


@dataclass
class Token:
    type: str
    value: str
    line: int = 0
    column: int = 0
    normalized: str = ""

    def __post_init__(self) -> None:
        if not self.normalized:
            self.normalized = self.value.strip()


@dataclass
class ASTNode:
    type: str
    value: str = ""
    children: list["ASTNode"] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedCode:
    language: str
    raw: str
    normalized: str
    tokens: list[Token] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)
    ast: Optional[ASTNode] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def line_count(self) -> int:
        return len(self.lines)

    @property
    def token_count(self) -> int:
        return len(self.tokens)


@dataclass
class DiffLine:
    old_no: Optional[int]
    new_no: Optional[int]
    content: str
    change_type: ChangeType
    tokens: list[tuple[ChangeType, str]] = field(default_factory=list)


@dataclass
class DiffChunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    lines: list[DiffLine] = field(default_factory=list)

    @property
    def header(self) -> str:
        return f"@@ -{self.old_start},{self.old_count} +{self.new_start},{self.new_count} @@"


@dataclass
class DiffResult:
    chunks: list[DiffChunk] = field(default_factory=list)
    added: int = 0
    removed: int = 0
    equal: int = 0
    mode: DiffMode = DiffMode.LINE

    @property
    def total_changes(self) -> int:
        return self.added + self.removed


@dataclass
class SimilarityScores:
    overall: float = 0.0
    exact: float = 0.0
    semantic: float = 0.0
    structural: float = 0.0
    token: float = 0.0
    logic: float = 0.0
    levenshtein: float = 0.0
    jaccard: float = 0.0
    cosine: float = 0.0
    ast: float = 0.0


@dataclass
class ComplexityMetrics:
    cyclomatic: int = 0
    cognitive: int = 0
    lines_of_code: int = 0
    logical_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    functions: int = 0
    classes: int = 0
    max_nesting: int = 0
    maintainability_index: float = 0.0
    halstead_volume: float = 0.0
    halstead_difficulty: float = 0.0


@dataclass
class ChangeStatistics:
    lines_added: int = 0
    lines_removed: int = 0
    lines_modified: int = 0
    lines_equal: int = 0
    chars_added: int = 0
    chars_removed: int = 0
    tokens_added: int = 0
    tokens_removed: int = 0
    functions_added: list[str] = field(default_factory=list)
    functions_removed: list[str] = field(default_factory=list)
    functions_changed: list[str] = field(default_factory=list)
    classes_added: list[str] = field(default_factory=list)
    classes_removed: list[str] = field(default_factory=list)
    classes_changed: list[str] = field(default_factory=list)
    imports_added: list[str] = field(default_factory=list)
    imports_removed: list[str] = field(default_factory=list)
    renamed_symbols: list[dict[str, str]] = field(default_factory=list)
    complexity_delta: int = 0


@dataclass
class PlagiarismIndicators:
    is_plagiarism_suspected: bool = False
    confidence: float = 0.0
    matching_blocks: list[dict[str, Any]] = field(default_factory=list)
    renamed_identifiers: list[dict[str, str]] = field(default_factory=list)
    structural_fingerprint_match: float = 0.0
    comment_stripped_similarity: float = 0.0
    whitespace_stripped_similarity: float = 0.0


@dataclass
class ComparisonResult:
    language: str
    similarity: SimilarityScores = field(default_factory=SimilarityScores)
    diff: DiffResult = field(default_factory=DiffResult)
    ast_diff: dict[str, Any] = field(default_factory=dict)
    statistics: ChangeStatistics = field(default_factory=ChangeStatistics)
    old_complexity: ComplexityMetrics = field(default_factory=ComplexityMetrics)
    new_complexity: ComplexityMetrics = field(default_factory=ComplexityMetrics)
    plagiarism: PlagiarismIndicators = field(default_factory=PlagiarismIndicators)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
