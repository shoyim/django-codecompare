"""Basic usage examples for codecompare."""
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django
django.setup()

from codecompare.core.services import compare

CODE_A = """\
def calculate(a, b):
    result = a + b
    return result

class MathHelper:
    def square(self, n):
        return n * n
"""

CODE_B = """\
def calculate(x, y):
    total = x + y
    return total

def cube(n):
    return n ** 3

class MathHelper:
    def square(self, n):
        return n * n

    def cube(self, n):
        return n ** 3
"""


def main():
    print("=== CodeCompare Basic Example ===\n")

    result = compare(CODE_A, CODE_B, language="python")

    print(f"Language detected : {result.language.value}")
    print(f"Overall similarity: {result.similarity.overall:.1f}%")
    print(f"Token similarity  : {result.similarity.token:.1f}%")
    print(f"Cosine similarity : {result.similarity.cosine:.1f}%")
    print(f"AST similarity    : {result.similarity.ast:.1f}%")
    print(f"Jaccard similarity: {result.similarity.jaccard:.1f}%")
    print()

    s = result.stats
    print(f"Lines added   : {s.lines_added}")
    print(f"Lines removed : {s.lines_removed}")
    print(f"Lines equal   : {s.lines_equal}")
    print()

    p = result.plagiarism
    print(f"Plagiarism score     : {p.score:.2f}")
    print(f"Plagiarism confidence: {p.confidence}")
    print(f"Is suspicious        : {p.is_suspicious}")
    print()

    c = result.complexity_new
    if c:
        print(f"Cyclomatic complexity : {c.cyclomatic:.1f}")
        print(f"Halstead volume      : {c.halstead_volume:.1f}")
        print(f"Maintainability index: {c.maintainability_index:.1f}")
    print()

    if result.renamed_symbols:
        print("Renamed symbols:")
        for r in result.renamed_symbols:
            print(f"  {r}")
    else:
        print("No renamed symbols detected.")

    print(f"\nProcessing time: {result.processing_time_ms:.1f} ms")


if __name__ == "__main__":
    main()
