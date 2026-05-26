"""CLI interface for codecompare."""
from __future__ import annotations
import json, sys
from pathlib import Path

try:
    import click
    _CLICK = True
except ImportError:
    _CLICK = False

if _CLICK:
    @click.group()
    @click.version_option(version="1.0.0", prog_name="codecompare")
    def cli() -> None:
        """CodeCompare — production-grade code diff and similarity engine."""

    @cli.command("compare")
    @click.argument("old_file", type=click.Path(exists=True))
    @click.argument("new_file", type=click.Path(exists=True))
    @click.option("--language", "-l", default=None)
    @click.option("--json", "output_json", is_flag=True)
    @click.option("--no-diff", is_flag=True)
    @click.option("--plagiarism", is_flag=True)
    def compare_cmd(old_file, new_file, language, output_json, no_diff, plagiarism):
        """Compare two code files."""
        import dataclasses
        old_code = Path(old_file).read_text(encoding="utf-8", errors="replace")
        new_code = Path(new_file).read_text(encoding="utf-8", errors="replace")
        from codecompare.core.services import ComparisonService
        result = ComparisonService().compare(old_code, new_code, language)
        if output_json:
            click.echo(json.dumps(dataclasses.asdict(result), indent=2, default=str))
            return
        click.echo(f"\n{'='*60}")
        click.echo(f"  Language   : {result.language}")
        click.echo(f"  Similarity : {result.similarity.overall:.1f}% overall")
        click.echo(f"  Exact      : {result.similarity.exact:.1f}%")
        click.echo(f"  Semantic   : {result.similarity.semantic:.1f}%")
        click.echo(f"  AST        : {result.similarity.ast:.1f}%")
        click.echo(f"{'='*60}")
        s = result.statistics
        click.echo(f"  Lines added    : {s.lines_added}")
        click.echo(f"  Lines removed  : {s.lines_removed}")
        if s.functions_added:   click.echo(f"  Functions added   : {', '.join(s.functions_added)}")
        if s.functions_removed: click.echo(f"  Functions removed : {', '.join(s.functions_removed)}")
        if s.functions_changed: click.echo(f"  Functions changed : {', '.join(s.functions_changed)}")
        oc, nc = result.old_complexity, result.new_complexity
        click.echo(f"\n  Cyclomatic (old→new): {oc.cyclomatic} → {nc.cyclomatic} (Δ{nc.cyclomatic-oc.cyclomatic:+d})")
        click.echo(f"  Maintainability    : {oc.maintainability_index:.1f} → {nc.maintainability_index:.1f}")
        if plagiarism:
            p = result.plagiarism
            click.echo(f"\n  Plagiarism suspected: {p.is_plagiarism_suspected} ({p.confidence:.1f}%)")
        if result.warnings:
            for w in result.warnings: click.echo(f"  WARNING: {w}")
        if not no_diff:
            from codecompare.diff_engine.myers import unified_diff
            click.echo(unified_diff(old_code, new_code, old_file, new_file))

    @cli.command("diff")
    @click.argument("old_file", type=click.Path(exists=True))
    @click.argument("new_file", type=click.Path(exists=True))
    def diff_cmd(old_file, new_file):
        """Output unified diff."""
        from codecompare.diff_engine.myers import unified_diff
        old = Path(old_file).read_text(encoding="utf-8", errors="replace")
        new = Path(new_file).read_text(encoding="utf-8", errors="replace")
        click.echo(unified_diff(old, new, old_file, new_file), nl=False)

    @cli.command("languages")
    def languages_cmd():
        """List supported languages."""
        from codecompare.core.types import Language
        for lang in Language:
            if lang != Language.UNKNOWN: click.echo(f"  {lang.value}")

    @cli.command("serve")
    @click.option("--host", default="0.0.0.0")
    @click.option("--port", "-p", default=8000)
    @click.option("--workers", "-w", default=4)
    @click.option("--reload", is_flag=True)
    def serve_cmd(host, port, workers, reload):
        """Start the Django ASGI server."""
        try:
            import uvicorn
        except ImportError:
            click.echo("uvicorn required: pip install uvicorn", err=True); sys.exit(1)
        uvicorn.run("config.asgi:application", host=host, port=port,
                    workers=1 if reload else workers, reload=reload, log_level="info")

    def main() -> None: cli()

else:
    def main() -> None:
        print("click is required: pip install click"); sys.exit(1)

if __name__ == "__main__":
    main()
