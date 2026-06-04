from pathlib import Path

from production_readiness_scorecard.parser import load_rules_config, load_service_metadata
from production_readiness_scorecard.rules import evaluate_rule


def test_required_field_passes_when_present():
    service = load_service_metadata(Path("examples/checkout-service.yaml"))
    rules = load_rules_config(Path("examples/rules.yaml"))
    owner_rule = next(rule for rule in rules.rules if rule.id == "ownership.owner_required")
    result = evaluate_rule(service, owner_rule)
    assert result.status == "pass"


def test_required_field_fails_when_missing():
    service = load_service_metadata(Path("examples/checkout-service.yaml"))
    rules = load_rules_config(Path("examples/rules.yaml"))
    retention_rule = next(rule for rule in rules.rules if rule.id == "security.retention_policy_required_for_pii")
    result = evaluate_rule(service, retention_rule)
    assert result.status == "fail"
    assert result.blocking is True


def test_expected_value_rule_fails():
    service = load_service_metadata(Path("examples/checkout-service.yaml"))
    rules = load_rules_config(Path("examples/rules.yaml"))
    saturation_rule = next(rule for rule in rules.rules if rule.id == "alerts.saturation_required")
    result = evaluate_rule(service, saturation_rule)
    assert result.status == "fail"


def test_condition_rule_skips_when_condition_does_not_match():
    service = load_service_metadata(Path("examples/checkout-service.yaml"))
    rules = load_rules_config(Path("examples/rules.yaml"))
    retention_rule = next(rule for rule in rules.rules if rule.id == "security.retention_policy_required_for_pii")
    service = service.model_copy(update={"security": service.security.model_copy(update={"pii_access": False})})
    result = evaluate_rule(service, retention_rule)
    assert result.status == "skip"


def test_rule_skips_for_non_applicable_tier():
    service = load_service_metadata(Path("examples/checkout-service.yaml"))
    rules = load_rules_config(Path("examples/rules.yaml"))
    api_rule = next(rule for rule in rules.rules if rule.id == "api.openapi_spec_required")
    low_tier = service.model_copy(update={"service": service.service.model_copy(update={"tier": "low"})})
    result = evaluate_rule(low_tier, api_rule)
    assert result.status == "skip"

