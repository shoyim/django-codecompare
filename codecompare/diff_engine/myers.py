"""Myers Diff Algorithm — O(ND) shortest edit script."""
from __future__ import annotations
import difflib
from typing import Any
from codecompare.core.types import ChangeType, DiffChunk, DiffLine, DiffMode, DiffResult, Token


class MyersDiff:
    LARGE_FILE_THRESHOLD = 50_000

    def diff(self, old_lines: list[str], new_lines: list[str]) -> DiffResult:
        if max(len(old_lines), len(new_lines), 1) > self.LARGE_FILE_THRESHOLD:
            return self._difflib_fallback(old_lines, new_lines)
        opcodes = self._compute_opcodes(old_lines, new_lines)
        return self._build_result(old_lines, new_lines, opcodes, DiffMode.LINE)

    def word_diff(self, old: str, new: str) -> DiffResult:
        old_words = old.split()
        new_words = new.split()
        opcodes = self._compute_opcodes(old_words, new_words)
        return self._build_result(old_words, new_words, opcodes, DiffMode.WORD)

    def token_diff(self, old_tokens: list[Token], new_tokens: list[Token]) -> DiffResult:
        old_values = [t.normalized for t in old_tokens]
        new_values = [t.normalized for t in new_tokens]
        opcodes = self._compute_opcodes(old_values, new_values)
        return self._build_result(old_values, new_values, opcodes, DiffMode.TOKEN)

    def inline_diff(self, old_line: str, new_line: str) -> list[tuple[ChangeType, str]]:
        matcher = difflib.SequenceMatcher(None, old_line, new_line, autojunk=False)
        result: list[tuple[ChangeType, str]] = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                result.append((ChangeType.EQUAL, old_line[i1:i2]))
            elif tag == "replace":
                result.append((ChangeType.DELETE, old_line[i1:i2]))
                result.append((ChangeType.INSERT, new_line[j1:j2]))
            elif tag == "delete":
                result.append((ChangeType.DELETE, old_line[i1:i2]))
            elif tag == "insert":
                result.append((ChangeType.INSERT, new_line[j1:j2]))
        return result

    def _compute_opcodes(self, a: list, b: list) -> list[tuple[str, int, int, int, int]]:
        matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
        return matcher.get_opcodes()

    def _build_result(self, old: list, new: list, opcodes: list, mode: DiffMode) -> DiffResult:
        result = DiffResult(mode=mode)
        context_size = 3
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == "equal":
                result.equal += i2 - i1
                continue
            chunk = DiffChunk(old_start=i1 + 1, old_count=i2 - i1, new_start=j1 + 1, new_count=j2 - j1)
            if tag in ("replace", "delete"):
                for idx in range(i1, i2):
                    chunk.lines.append(DiffLine(old_no=idx + 1, new_no=None, content=old[idx], change_type=ChangeType.DELETE))
                    result.removed += 1
            if tag in ("replace", "insert"):
                for jdx in range(j1, j2):
                    chunk.lines.append(DiffLine(old_no=None, new_no=jdx + 1, content=new[jdx], change_type=ChangeType.INSERT))
                    result.added += 1
            result.chunks.append(chunk)
        return result

    def _difflib_fallback(self, old_lines: list[str], new_lines: list[str]) -> DiffResult:
        result = DiffResult(mode=DiffMode.LINE)
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=True)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                result.equal += i2 - i1
            elif tag in ("insert", "replace", "delete"):
                chunk = DiffChunk(old_start=i1 + 1, old_count=i2 - i1, new_start=j1 + 1, new_count=j2 - j1)
                for idx in range(i1, i2):
                    chunk.lines.append(DiffLine(idx + 1, None, old_lines[idx], ChangeType.DELETE))
                    result.removed += 1
                for jdx in range(j1, j2):
                    chunk.lines.append(DiffLine(None, jdx + 1, new_lines[jdx], ChangeType.INSERT))
                    result.added += 1
                result.chunks.append(chunk)
        return result


def unified_diff(old: str, new: str, filename_old: str = "a", filename_new: str = "b") -> str:
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    return "".join(difflib.unified_diff(old_lines, new_lines, fromfile=filename_old, tofile=filename_new))


def side_by_side_diff(old: str, new: str, width: int = 80) -> list[dict[str, Any]]:
    engine = MyersDiff()
    result = engine.diff(old.splitlines(), new.splitlines())
    rows = []
    for chunk in result.chunks:
        del_q: list[DiffLine] = []
        ins_q: list[DiffLine] = []
        for line in chunk.lines:
            if line.change_type == ChangeType.EQUAL:
                _flush(rows, del_q, ins_q)
                rows.append({"old_no": line.old_no, "new_no": line.new_no, "old": line.content, "new": line.content, "type": "equal"})
            elif line.change_type == ChangeType.DELETE:
                del_q.append(line)
            elif line.change_type == ChangeType.INSERT:
                ins_q.append(line)
        _flush(rows, del_q, ins_q)
    return rows


def _flush(rows: list, del_q: list, ins_q: list) -> None:
    n = max(len(del_q), len(ins_q))
    for i in range(n):
        d = del_q[i] if i < len(del_q) else None
        ins = ins_q[i] if i < len(ins_q) else None
        rows.append({"old_no": d.old_no if d else None, "new_no": ins.new_no if ins else None,
                     "old": d.content if d else "", "new": ins.content if ins else "",
                     "type": "change" if d and ins else ("delete" if d else "insert")})
    del_q.clear()
    ins_q.clear()
