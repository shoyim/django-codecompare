"""Plugin registry for parsers, analyzers, and diff engines."""
from __future__ import annotations
import importlib
import logging
from typing import Any, ClassVar
from codecompare.core.exceptions import UnsupportedLanguageError

logger = logging.getLogger(__name__)


class Registry:
    _instances: ClassVar[dict[str, "Registry"]] = {}

    def __init__(self, name: str) -> None:
        self.name = name
        self._plugins: dict[str, Any] = {}
        self._aliases: dict[str, str] = {}

    @classmethod
    def get(cls, name: str) -> "Registry":
        if name not in cls._instances:
            cls._instances[name] = cls(name)
        return cls._instances[name]

    def register(self, key: str, plugin: Any, aliases: list[str] | None = None) -> None:
        self._plugins[key.lower()] = plugin
        if aliases:
            for alias in aliases:
                self._aliases[alias.lower()] = key.lower()

    def get_plugin(self, key: str) -> Any:
        k = key.lower()
        k = self._aliases.get(k, k)
        if k not in self._plugins:
            raise UnsupportedLanguageError(key)
        return self._plugins[k]

    def has(self, key: str) -> bool:
        k = key.lower()
        return k in self._plugins or k in self._aliases

    def list_keys(self) -> list[str]:
        return list(self._plugins.keys())

    def register_from_module(self, module_path: str, class_name: str, key: str) -> None:
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            self.register(key, cls())
        except (ImportError, AttributeError) as exc:
            logger.warning("Could not load plugin %s.%s: %s", module_path, class_name, exc)


parser_registry = Registry.get("parsers")
analyzer_registry = Registry.get("analyzers")
diff_registry = Registry.get("diff_engines")
similarity_registry = Registry.get("similarity_engines")

_plugins_loaded = False


def load_default_plugins() -> None:
    global _plugins_loaded
    if _plugins_loaded:
        return
    _plugins_loaded = True
    _load_parsers()
    _load_similarity_engines()


def _load_parsers() -> None:
    from codecompare.core.types import Language
    parser_modules = [
        ("codecompare.parsers.python_parser", "PythonParser", Language.PYTHON),
        ("codecompare.parsers.javascript_parser", "JavaScriptParser", Language.JAVASCRIPT),
        ("codecompare.parsers.javascript_parser", "TypeScriptParser", Language.TYPESCRIPT),
        ("codecompare.parsers.javascript_parser", "JSXParser", Language.JSX),
        ("codecompare.parsers.javascript_parser", "TSXParser", Language.TSX),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.JAVA),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.GO),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.RUST),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.CPP),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.C),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.CSHARP),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.PHP),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.RUBY),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.KOTLIN),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.SWIFT),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.DART),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.SCALA),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.BASH),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.SQL),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.HTML),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.CSS),
        ("codecompare.parsers.generic_parser", "GenericParser", Language.VUE),
    ]
    for module_path, cls_name, lang in parser_modules:
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, cls_name)
            instance = cls(language=lang)
            parser_registry.register(lang.value, instance)
        except Exception as exc:
            logger.warning("Parser load failed for %s: %s", lang.value, exc)


def _load_similarity_engines() -> None:
    engines = [
        ("codecompare.similarity.levenshtein", "LevenshteinSimilarity", "levenshtein"),
        ("codecompare.similarity.cosine", "CosineSimilarity", "cosine"),
        ("codecompare.similarity.jaccard", "JaccardSimilarity", "jaccard"),
        ("codecompare.similarity.token_similarity", "TokenSimilarity", "token"),
    ]
    for module_path, cls_name, key in engines:
        similarity_registry.register_from_module(module_path, cls_name, key)
