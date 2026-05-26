"""Generic parser for languages without a dedicated implementation."""
from __future__ import annotations
import re
from codecompare.core.types import ASTNode, Language, ParsedCode, Token

_COMMENT_PATTERNS: dict[str, list[re.Pattern]] = {
    "default": [re.compile(r"//[^\n]*"), re.compile(r"/\*.*?\*/", re.DOTALL), re.compile(r"#[^\n]*")],
    "html": [re.compile(r"<!--.*?-->", re.DOTALL)],
    "sql": [re.compile(r"--[^\n]*"), re.compile(r"/\*.*?\*/", re.DOTALL)],
}


class GenericParser:
    extensions: list[str] = []

    def __init__(self, language: Language = Language.UNKNOWN) -> None:
        self._language = language
        self.language = language.value

    def parse(self, code: str) -> ParsedCode:
        return ParsedCode(language=self.language, raw=code, normalized=self.normalize(code),
                          tokens=self.tokenize(code), lines=code.splitlines())

    def tokenize(self, code: str) -> list[Token]:
        try: return self._pygments_tokenize(code)
        except Exception: return self._regex_tokenize(code)

    def _pygments_tokenize(self, code: str) -> list[Token]:
        from pygments import lex
        from pygments.lexers import get_lexer_by_name, guess_lexer
        from pygments.token import Token as PygToken
        from pygments.util import ClassNotFound
        lmap = {"cpp": "cpp", "csharp": "csharp", "java": "java", "go": "go", "rust": "rust",
                "kotlin": "kotlin", "ruby": "ruby", "php": "php", "bash": "bash", "sql": "sql",
                "html": "html", "css": "css"}
        try: lexer = get_lexer_by_name(lmap.get(self._language.value, "text"), stripall=False)
        except ClassNotFound: lexer = guess_lexer(code)
        tokens: list[Token] = []
        line = 1
        for ttype, value in lex(code, lexer):
            newlines = value.count("\n")
            if not (str(ttype).startswith("Token.Text") or "Comment" in str(ttype) or not value.strip()):
                tokens.append(Token(type=str(ttype).replace("Token.", ""), value=value, line=line))
            line += newlines
        return tokens

    def _regex_tokenize(self, code: str) -> list[Token]:
        pattern = re.compile(r"\"[^\"\\]*(?:\\.[^\"\\]*)*\"|'[^'\\]*(?:\\.[^'\\]*)*'|\d+(?:\.\d+)?|[a-zA-Z_]\w*|[^\w\s]")
        tokens: list[Token] = []
        line = 1
        for m in pattern.finditer(code):
            tokens.append(Token(type="TOKEN", value=m.group(), line=line))
            line += m.group().count("\n")
        return tokens

    def get_ast(self, code: str) -> ASTNode | None:
        try:
            from codecompare.ast_engine.treesitter_engine import TreeSitterEngine
            engine = TreeSitterEngine()
            tree = engine.parse(code, self._language.value)
            root = tree.root_node
            return ASTNode(type=root.type, start_line=root.start_point[0], end_line=root.end_point[0])
        except Exception:
            return None

    def normalize(self, code: str) -> str:
        lang_key = self._language.value if self._language.value in _COMMENT_PATTERNS else "default"
        for pat in _COMMENT_PATTERNS[lang_key]: code = pat.sub("", code)
        return "\n".join(l.rstrip() for l in code.splitlines() if l.strip())
