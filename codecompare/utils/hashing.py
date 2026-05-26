"""Hashing utilities."""
from __future__ import annotations
import hashlib

def sha256(text: str) -> str: return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
def sha256_short(text: str, length: int = 16) -> str: return sha256(text)[:length]
def md5(text: str) -> str: return hashlib.md5(text.encode("utf-8", errors="replace")).hexdigest()
def content_hash(old_code: str, new_code: str, language: str) -> str:
    return sha256_short(f"{sha256_short(old_code)}:{sha256_short(new_code)}:{language}", 24)
