from pathlib import Path

from production_readiness_scorecard.parser import load_rules_config, load_service_metadata
from production_readiness_scorecard.scorer import evaluate_scorecard


def test_overall_score_calculation():
    service = load_service_metadata(Path("examples/checkout-service.yaml"))
    rules = load_rules_config(Path("examples/rules.yaml"))
    result = evaluate_scorecard(
        service,
        rules.rules,
        {name: category.weight for name, category in rules.scorecard.categories.items()},
    )
    assert 0 <= result.overall_score <= 100
    assert result.status in {"Ready", "Ready with Follow-ups", "Needs Attention", "Not Ready"}
    assert "security.retention_policy_required_for_pii" in result.blocking_failures


def test_blocking_failure_caps_status():
    service = load_service_metadata(Path("examples/checkout-service.yaml"))
    rules = load_rules_config(Path("examples/rules.yaml"))
    result = evaluate_scorecard(
        service,
        rules.rules,
        {name: category.weight for name, category in rules.scorecard.categories.items()},
    )
    assert result.status == "Needs Attention"

