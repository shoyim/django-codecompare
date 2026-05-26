"""Utilities for streaming large files in chunks."""
from __future__ import annotations
import io
from typing import Generator, Iterator

CHUNK_SIZE = 65_536  # 64 KB
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def read_in_chunks(file_obj: io.IOBase, chunk_size: int = CHUNK_SIZE) -> Generator[bytes, None, None]:
    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        yield chunk


def stream_lines(file_obj: io.TextIOBase) -> Iterator[str]:
    for line in file_obj:
        yield line


def file_to_string(file_obj: io.IOBase, max_bytes: int = MAX_FILE_SIZE) -> str:
    """Read a file object into a string, enforcing a size limit."""
    from codecompare.core.exceptions import FileSizeLimitError

    buf = io.BytesIO()
    total = 0
    for chunk in read_in_chunks(file_obj):
        total += len(chunk)
        if total > max_bytes:
            raise FileSizeLimitError(total, max_bytes)
        buf.write(chunk)
    raw = buf.getvalue()
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def split_into_lines(code: str) -> list[str]:
    return code.splitlines(keepends=False)


def truncate_lines(lines: list[str], max_lines: int) -> tuple[list[str], bool]:
    if len(lines) <= max_lines:
        return lines, False
    return lines[:max_lines], True
