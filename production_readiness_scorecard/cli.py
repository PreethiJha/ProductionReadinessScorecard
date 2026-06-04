from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .models import ScorecardResult
from .parser import ScorecardInputError, load_rules_config, load_service_metadata
from .reporter import write_json_report, write_markdown_report
from .scorer import evaluate_scorecard

app = typer.Typer(add_completion=False, help="Evaluate production readiness from YAML metadata.")
evaluate_app = typer.Typer(add_completion=False)
console = Console()


def _print_summary(result: ScorecardResult) -> None:
    console.print("[bold]Production Readiness Scorecard[/bold]")
    console.print()
    console.print(f"Service: {result.service_name}")
    console.print(f"Tier: {result.tier}")
    console.print(f"Lifecycle: {result.lifecycle}")
    console.print()
    console.print(f"Overall Score: {result.overall_score}/100")
    console.print(f"Status: {result.status}")
    console.print()

    table = Table(title="Category Scores", show_lines=False)
    table.add_column("Category")
    table.add_column("Score", justify="right")
    for category in result.category_scores:
        table.add_row(category.category.capitalize(), str(category.score))
    console.print(table)

    if result.blocking_failures:
        console.print()
        console.print("[bold]Blocking Failures[/bold]")
        for failure in result.blocking_failures:
            console.print(f"- {failure}")

    failed = [rule for rule in result.rule_results if rule.status == "fail"]
    warnings = [rule for rule in result.rule_results if rule.status == "warn"]

    if failed:
        console.print()
        console.print("[bold]Failed Checks[/bold]")
        for rule in failed:
            console.print(f"- {rule.rule_id}: {rule.description}")

    if warnings:
        console.print()
        console.print("[bold]Warnings[/bold]")
        for rule in warnings:
            console.print(f"- {rule.rule_id}: {rule.description}")

    if result.recommendations:
        console.print()
        console.print("[bold]Top Follow-ups[/bold]")
        for index, recommendation in enumerate(result.recommendations, start=1):
            console.print(f"{index}. {recommendation}")


app.add_typer(evaluate_app, name="evaluate")


@evaluate_app.callback(invoke_without_command=True)
def evaluate(
    service: Path = typer.Option(..., "--service", exists=True, readable=True, help="Path to service YAML."),
    rules: Path = typer.Option(..., "--rules", exists=True, readable=True, help="Path to rules YAML."),
    output: Path | None = typer.Option(None, "--output", help="Optional Markdown report path."),
    json_output: Path | None = typer.Option(None, "--json-output", help="Optional JSON report path."),
    fail_below: int = typer.Option(80, "--fail-below", help="CI threshold."),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as failures."),
    include_recommendations: bool = typer.Option(True, "--include-recommendations/--no-include-recommendations", help="Show recommendations in the terminal output."),
    verbose: bool = typer.Option(False, "--verbose", help="Print detailed rule-by-rule output."),
) -> None:
    try:
        service_metadata = load_service_metadata(service)
        rules_config = load_rules_config(rules)
        result = evaluate_scorecard(
            service_metadata,
            rules_config.rules,
            {name: category.weight for name, category in rules_config.scorecard.categories.items()},
            strict=strict,
        )

        if output is not None:
            write_markdown_report(result, output)
        if json_output is not None:
            write_json_report(result, json_output)

        if not include_recommendations:
            result = result.model_copy(update={"recommendations": []})

        _print_summary(result)

        if verbose:
            console.print()
            console.print("[bold]Rule Details[/bold]")
            for rule in result.rule_results:
                console.print(
                    f"{rule.rule_id}: {rule.status} "
                    f"(severity={rule.severity}, impact={rule.score_impact}, blocking={rule.blocking})"
                )

        exit_code = 0
        if result.blocking_failures or result.overall_score < fail_below:
            exit_code = 1
        raise typer.Exit(code=exit_code)
    except ScorecardInputError as exc:
        console.print(f"[red]Invalid input:[/red] {exc}")
        raise typer.Exit(code=2)
    except typer.Exit:
        raise
    except Exception as exc:  # pragma: no cover - safety net for runtime faults
        console.print(f"[red]Runtime error:[/red] {exc}")
        raise typer.Exit(code=3)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
