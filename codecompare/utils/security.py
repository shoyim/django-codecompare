"""Security utilities: upload validation, malicious content detection."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Any
from codecompare.core.exceptions import SecurityError

_MAX_UPLOAD_SIZE = 100 * 1024 * 1024
_BLOCKED_EXTENSIONS = {".exe", ".dll", ".so", ".dylib", ".bin", ".zip", ".tar", ".gz", ".jpg", ".png", ".gif", ".pdf"}
_SUSPICIOUS = [
    re.compile(r"__import__\s*\(\s*['\"]os['\"]"),
    re.compile(r"eval\s*\(\s*compile"),
    re.compile(r"os\.(?:system|popen|execv?)"),
]


def validate_upload(file_obj: Any, max_size: int = _MAX_UPLOAD_SIZE) -> None:
    size = getattr(file_obj, "size", 0) or 0
    try:
        if size == 0: content = file_obj.read(); size = len(content); file_obj.seek(0)
    except Exception: pass
    if size > max_size:
        from codecompare.core.exceptions import FileSizeLimitError
        raise FileSizeLimitError(size, max_size)
    name = getattr(file_obj, "name", "") or ""
    if Path(name).suffix.lower() in _BLOCKED_EXTENSIONS:
        raise SecurityError(f"File extension '{Path(name).suffix}' not allowed")


def sanitise_code(code: str, max_size: int = _MAX_UPLOAD_SIZE) -> str:
    if len(code.encode()) > max_size:
        raise SecurityError(f"Code snippet exceeds maximum size of {max_size} bytes")
    return code.replace("\x00", "")


def is_suspicious(code: str) -> list[str]:
    return [p.pattern for p in _SUSPICIOUS if p.search(code)]
