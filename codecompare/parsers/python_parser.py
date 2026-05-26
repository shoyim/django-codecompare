"""Python-specific parser using the stdlib ast and tokenize modules."""
from __future__ import annotations
import ast, io, re
import tokenize as py_tokenize
from codecompare.core.types import ASTNode, Language, ParsedCode, Token


class PythonParser:
    language = Language.PYTHON.value
    extensions = [".py", ".pyw"]

    def __init__(self, language: Language = Language.PYTHON) -> None:
        self._language = language

    def parse(self, code: str) -> ParsedCode:
        return ParsedCode(
            language=self.language, raw=code, normalized=self.normalize(code),
            tokens=self.tokenize(code), lines=code.splitlines(), ast=self.get_ast(code))

    def tokenize(self, code: str) -> list[Token]:
        tokens: list[Token] = []
        try:
            gen = py_tokenize.generate_tokens(io.StringIO(code).readline)
            for tok in gen:
                if tok.type in (py_tokenize.ENCODING, py_tokenize.ENDMARKER,
                                py_tokenize.NL, py_tokenize.NEWLINE,
                                py_tokenize.INDENT, py_tokenize.DEDENT):
                    continue
                tokens.append(Token(type=py_tokenize.tok_name[tok.type], value=tok.string,
                                    line=tok.start[0], column=tok.start[1]))
        except py_tokenize.TokenError:
            pass
        return tokens

    def get_ast(self, code: str) -> ASTNode | None:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return None
        return self._convert(tree)

    def normalize(self, code: str) -> str:
        lines = []
        for line in code.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"): continue
            stripped = re.sub(r"\s+#[^\"']*$", "", line)
            if stripped.strip(): lines.append(stripped)
        return "\n".join(lines)

    def _convert(self, node: ast.AST) -> ASTNode:
        children = [self._convert(c) for c in ast.iter_child_nodes(node)]
        value = ""
        if isinstance(node, ast.Name): value = node.id
        elif isinstance(node, ast.Constant): value = repr(node.value)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)): value = node.name
        return ASTNode(type=type(node).__name__, value=value, children=children,
                       start_line=getattr(node, "lineno", 0), end_line=getattr(node, "end_lineno", 0))
