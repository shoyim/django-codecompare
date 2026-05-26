"""JavaScript/TypeScript/JSX/TSX parser."""
from __future__ import annotations
import re
from codecompare.core.types import ASTNode, Language, ParsedCode, Token


class JavaScriptParser:
    language = Language.JAVASCRIPT.value
    extensions = [".js", ".mjs"]

    def __init__(self, language: Language = Language.JAVASCRIPT) -> None:
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
        from pygments.lexers import get_lexer_by_name
        from pygments.token import Token as PygToken
        lname = {"typescript": "typescript", "jsx": "jsx", "tsx": "tsx"}.get(self._language.value, "javascript")
        try: lexer = get_lexer_by_name(lname, stripall=False)
        except Exception: lexer = get_lexer_by_name("javascript", stripall=False)
        tokens: list[Token] = []
        line = 1
        for ttype, value in lex(code, lexer):
            if str(ttype).startswith("Token.Text") or "Comment" in str(ttype) or not value.strip():
                line += value.count("\n"); continue
            tokens.append(Token(type=str(ttype).replace("Token.", ""), value=value, line=line))
            line += value.count("\n")
        return tokens

    def _regex_tokenize(self, code: str) -> list[Token]:
        pattern = re.compile(
            r"(?P<STRING>\"[^\"\\]*(?:\\.[^\"\\]*)*\"|'[^'\\]*(?:\\.[^'\\]*)*'|`[^`]*`)"
            r"|(?P<COMMENT>//[^\n]*|/\*.*?\*/)"
            r"|(?P<NUMBER>\d+(?:\.\d+)?)"
            r"|(?P<IDENTIFIER>[a-zA-Z_$]\w*)"
            r"|(?P<OP>[+\-*/%=<>!&|^~?:]+)"
            r"|(?P<PUNCT>[(){}\[\];,.])", re.DOTALL)
        tokens: list[Token] = []
        line = 1
        for m in pattern.finditer(code):
            tok_type = m.lastgroup or "UNKNOWN"
            value = m.group()
            if tok_type == "COMMENT": line += value.count("\n"); continue
            tokens.append(Token(type=tok_type, value=value, line=line))
            line += value.count("\n")
        return tokens

    def get_ast(self, code: str) -> ASTNode | None:
        try:
            from codecompare.ast_engine.treesitter_engine import TreeSitterEngine
            tree = TreeSitterEngine().parse(code, "javascript")
            root = tree.root_node
            return ASTNode(type=root.type, start_line=root.start_point[0], end_line=root.end_point[0])
        except Exception: return None

    def normalize(self, code: str) -> str:
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        code = re.sub(r"//[^\n]*", "", code)
        return "\n".join(l.rstrip() for l in code.splitlines() if l.strip())


class TypeScriptParser(JavaScriptParser):
    language = Language.TYPESCRIPT.value
    extensions = [".ts"]
    def __init__(self, language: Language = Language.TYPESCRIPT) -> None: super().__init__(language)


class JSXParser(JavaScriptParser):
    language = Language.JSX.value
    extensions = [".jsx"]
    def __init__(self, language: Language = Language.JSX) -> None: super().__init__(language)


class TSXParser(JavaScriptParser):
    language = Language.TSX.value
    extensions = [".tsx"]
    def __init__(self, language: Language = Language.TSX) -> None: super().__init__(language)
