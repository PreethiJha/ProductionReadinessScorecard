from pathlib import Path

from typer.testing import CliRunner

from production_readiness_scorecard.cli import app


def test_cli_generates_reports_and_exit_code(tmp_path: Path):
    runner = CliRunner()
    output_md = tmp_path / "report.md"
    output_json = tmp_path / "report.json"
    service_path = Path("examples/checkout-service.yaml").resolve()
    rules_path = Path("examples/rules.yaml").resolve()
    result = runner.invoke(
        app,
        [
            "evaluate",
            "--service",
            str(service_path),
            "--rules",
            str(rules_path),
            "--output",
            str(output_md),
            "--json-output",
            str(output_json),
            "--fail-below",
            "80",
        ],
    )
    assert result.exit_code == 1
    assert "Needs Attention" in result.output
    assert output_md.exists()
    assert output_json.exists()


def test_cli_invalid_input_exit_code(tmp_path: Path):
    runner = CliRunner()
    bad = tmp_path / "bad.yaml"
    bad.write_text("service: [")
    rules_path = Path("examples/rules.yaml").resolve()
    result = runner.invoke(
        app,
        [
            "evaluate",
            "--service",
            str(bad),
            "--rules",
            str(rules_path),
        ],
    )
    assert result.exit_code == 2
