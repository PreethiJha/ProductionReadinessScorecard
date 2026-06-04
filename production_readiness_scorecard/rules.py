from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .models import RuleConfig, RuleResult, RuleStatus, ServiceMetadata, Severity


def get_nested_value(data: Any, path: str) -> Any:
    current = data
    for part in path.split("."):
        if isinstance(current, Mapping):
            current = current.get(part)
        else:
            current = getattr(current, part, None)
        if current is None:
            return None
    return current


def is_present(value: Any) -> bool:
    if value is None:
        return False
    if value == "":
        return False
    if value == [] or value == {}:
        return False
    return True


def evaluate_condition(service: ServiceMetadata, condition_field: str, expected: Any) -> bool:
    actual = get_service_value(service, condition_field)
    return actual == expected


def get_service_value(service: ServiceMetadata, field_path: str) -> Any:
    return get_nested_value(service.model_dump(), field_path)


def rule_points(severity: Severity) -> int:
    return {"critical": 10, "high": 7, "medium": 4, "low": 2}[severity]


def is_blocking_failure(service: ServiceMetadata, rule: RuleConfig, actual: Any) -> bool:
    if rule.blocking:
        return True

    tier = service.service.tier
    if rule.id in {
        "ownership.owner_required",
        "ownership.on_call_required",
        "operations.runbook_required",
    }:
        return tier == "critical"

    if rule.id == "security.authentication_required":
        classification = (service.security.data_classification or "").lower()
        return classification in {"confidential", "restricted"}

    if rule.id == "security.retention_policy_required_for_pii":
        return bool(service.security.pii_access)

    return False


def evaluate_rule(service: ServiceMetadata, rule: RuleConfig, *, strict: bool = False) -> RuleResult:
    if service.service.tier not in rule.required_for_tiers:
        return RuleResult(
            rule_id=rule.id,
            category=rule.category,
            status="skip",
            severity=rule.severity,
            score_impact=0,
            description=rule.description,
            actual_value=get_service_value(service, rule.field),
            expected_value=rule.expected_value,
            recommendation=rule.recommendation,
            blocking=False,
        )

    if rule.condition is not None and not evaluate_condition(service, rule.condition.field, rule.condition.equals):
        return RuleResult(
            rule_id=rule.id,
            category=rule.category,
            status="skip",
            severity=rule.severity,
            score_impact=0,
            description=rule.description,
            actual_value=get_service_value(service, rule.field),
            expected_value=rule.expected_value,
            recommendation=rule.recommendation,
            blocking=False,
        )

    actual_value = get_service_value(service, rule.field)
    if rule.expected_value is not None:
        satisfied = actual_value == rule.expected_value
    else:
        satisfied = is_present(actual_value)

    if satisfied:
        return RuleResult(
            rule_id=rule.id,
            category=rule.category,
            status="pass",
            severity=rule.severity,
            score_impact=float(rule_points(rule.severity)),
            description=rule.description,
            actual_value=actual_value,
            expected_value=rule.expected_value,
            recommendation=rule.recommendation,
            blocking=False,
        )

    status: RuleStatus
    if rule.severity == "low" and not strict:
        status = "warn"
    else:
        status = "fail"

    blocking = is_blocking_failure(service, rule, actual_value)
    if status == "warn" and blocking:
        status = "fail"

    score_impact = float(rule_points(rule.severity) / 2 if status == "warn" else 0)
    return RuleResult(
        rule_id=rule.id,
        category=rule.category,
        status=status,
        severity=rule.severity,
        score_impact=score_impact,
        description=rule.description,
        actual_value=actual_value,
        expected_value=rule.expected_value,
        recommendation=rule.recommendation,
        blocking=blocking and status == "fail",
    )


def evaluate_rules(
    service: ServiceMetadata,
    rules: list[RuleConfig],
    *,
    strict: bool = False,
) -> list[RuleResult]:
    return [evaluate_rule(service, rule, strict=strict) for rule in rules]

