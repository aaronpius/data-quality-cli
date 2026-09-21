from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from dqcheck.io import load_dataframe
from dqcheck.profile import profile_dataframe
from dqcheck.report import build_report, write_report
from dqcheck.rules import evaluate_rules, load_rules

app = typer.Typer(
    add_completion=False,
    help="Profile datasets and enforce practical data-quality rules.",
)
console = Console()


def _show_profile(report: dict) -> None:
    summary = report["summary"]
    duplicate_text = (
        f"[bold]Duplicate rows:[/] {summary['duplicate_rows']} "
        f"({summary['duplicate_percent']:.2f}%)"
    )
    console.print(
        f"[bold]Rows:[/] {summary['rows']}  "
        f"[bold]Columns:[/] {summary['columns']}  "
        f"{duplicate_text}"
    )

    table = Table(title="Column profile")
    table.add_column("Column")
    table.add_column("Type")
    table.add_column("Null %", justify="right")
    table.add_column("Unique", justify="right")
    table.add_column("Outliers", justify="right")
    for item in report["columns"]:
        table.add_row(
            item["name"],
            item["dtype"],
            f"{item['null_percent']:.2f}",
            str(item["unique_count"]),
            "" if item["outlier_count"] is None else str(item["outlier_count"]),
        )
    console.print(table)


@app.command()
def profile(
    file: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Write report to a file.",
    ),
    format: str = typer.Option(
        "markdown",
        "--format",
        "-f",
        help="markdown or json",
    ),
) -> None:
    """Profile a dataset for nulls, duplicates, cardinality and numeric outliers."""
    df = load_dataframe(file)
    report = build_report(profile_dataframe(df))
    _show_profile(report)
    if output:
        write_report(report, output, format)
        console.print(f"[green]Report written to {output}[/green]")


@app.command()
def check(
    file: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    rules: Path = typer.Option(
        ...,
        "--rules",
        "-r",
        exists=True,
        dir_okay=False,
    ),
    output: Path | None = typer.Option(None, "--output", "-o"),
    format: str = typer.Option("markdown", "--format", "-f"),
) -> None:
    """Run YAML-defined data-quality rules. Exits with code 1 when any rule fails."""
    df = load_dataframe(file)
    results = evaluate_rules(df, load_rules(rules))
    report = build_report(profile_dataframe(df), results)
    _show_profile(report)

    for result in results:
        icon = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
        target = f" ({result.column})" if result.column else ""
        console.print(f"{icon} {result.rule}{target}: {result.message}")

    if output:
        write_report(report, output, format)
        console.print(f"Report written to {output}")

    if any(not result.passed for result in results):
        raise typer.Exit(code=1)


@app.command("sample-rules")
def sample_rules() -> None:
    """Print a starter YAML rules file."""
    console.print(
        """dataset:
  min_rows: 1
  max_duplicate_percent: 0
columns:
  id:
    max_null_percent: 0
    unique: true
  status:
    allowed_values: [active, inactive]
  amount:
    min: 0
"""
    )


@app.command()
def version() -> None:
    """Show dqcheck version."""
    from dqcheck import __version__

    console.print(__version__)


if __name__ == "__main__":
    app()
