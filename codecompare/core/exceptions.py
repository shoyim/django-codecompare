"""Custom exception hierarchy for codecompare."""
from __future__ import annotations


class CodeCompareError(Exception):
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code

    def to_dict(self) -> dict:
        return {"error": self.code, "message": self.message}


class LanguageDetectionError(CodeCompareError):
    def __init__(self, message: str = "Cannot detect language") -> None:
        super().__init__(message, "LANGUAGE_DETECTION_ERROR")


class ParseError(CodeCompareError):
    def __init__(self, message: str, language: str = "") -> None:
        super().__init__(message, "PARSE_ERROR")
        self.language = language


class UnsupportedLanguageError(CodeCompareError):
    def __init__(self, language: str) -> None:
        super().__init__(f"Language '{language}' is not supported", "UNSUPPORTED_LANGUAGE")
        self.language = language


class ComparisonError(CodeCompareError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "COMPARISON_ERROR")


class FileSizeLimitError(CodeCompareError):
    def __init__(self, size: int, limit: int) -> None:
        super().__init__(
            f"File size {size} bytes exceeds limit {limit} bytes", "FILE_SIZE_LIMIT"
        )
        self.size = size
        self.limit = limit


class SecurityError(CodeCompareError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "SECURITY_ERROR")


class ASTError(CodeCompareError):
    def __init__(self, message: str, language: str = "") -> None:
        super().__init__(message, "AST_ERROR")
        self.language = language


class SimilarityError(CodeCompareError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "SIMILARITY_ERROR")
