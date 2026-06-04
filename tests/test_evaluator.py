from pathlib import Path

from production_readiness_scorecard.parser import load_rules_config, load_service_metadata
from production_readiness_scorecard.rules import evaluate_rules


def test_evaluation_produces_expected_rule_mix():
    service = load_service_metadata(Path("examples/checkout-service.yaml"))
    rules = load_rules_config(Path("examples/rules.yaml"))
    results = evaluate_rules(service, rules.rules)
    assert any(result.status == "pass" for result in results)
    assert any(result.status == "fail" for result in results)
    assert any(result.status == "warn" for result in results)

