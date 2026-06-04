from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .models import (
    CategoryScore,
    ReadinessStatus,
    RuleConfig,
    RuleResult,
    ScorecardResult,
    ServiceMetadata,
)
from .rules import evaluate_rules, rule_points


def _rule_weight(result: RuleResult) -> float:
    if result.status == "pass":
        return float(rule_points(result.severity))
    if result.status == "warn":
        return float(rule_points(result.severity) / 2)
    return 0.0


def _category_score(results: Iterable[RuleResult], category: str) -> CategoryScore:
    category_results = [result for result in results if result.category == category]
    if not category_results:
        return CategoryScore(category=category, score=100, passed=0, failed=0, warnings=0, skipped=0)

    possible = sum(rule_points(result.severity) for result in category_results if result.status != "skip")
    earned = sum(_rule_weight(result) for result in category_results if result.status != "skip")
    score = 100 if possible == 0 else round((earned / possible) * 100)

    return CategoryScore(
        category=category,
        score=int(score),
        passed=sum(1 for result in category_results if result.status == "pass"),
        failed=sum(1 for result in category_results if result.status == "fail"),
        warnings=sum(1 for result in category_results if result.status == "warn"),
        skipped=sum(1 for result in category_results if result.status == "skip"),
    )


def _overall_status(score: int, blocking_failures: list[str]) -> ReadinessStatus:
    if blocking_failures and score >= 80:
        return "Needs Attention"
    if score >= 90:
        return "Ready"
    if score >= 80:
        return "Ready with Follow-ups"
    if score >= 60:
        return "Needs Attention"
    return "Not Ready"


def _recommendations(results: list[RuleResult]) -> list[str]:
    actionable = [result for result in results if result.status in {"fail", "warn"}]
    actionable.sort(
        key=lambda result: (
            not result.blocking,
            0 if result.status == "fail" else 1,
            -rule_points(result.severity),
            result.rule_id,
        )
    )
    seen: set[str] = set()
    recommendations: list[str] = []
    for result in actionable:
        if result.recommendation in seen:
            continue
        seen.add(result.recommendation)
        recommendations.append(result.recommendation)
    return recommendations


def evaluate_scorecard(
    service: ServiceMetadata,
    rules_config: list[RuleConfig],
    category_weights: dict[str, int],
    *,
    strict: bool = False,
) -> ScorecardResult:
    results = evaluate_rules(service, rules_config, strict=strict)

    category_scores = [
        _category_score(results, category)
        for category in category_weights
    ]
    weighted_total = sum(
        category.score * category_weights[category.category] for category in category_scores
    )
    overall_score = round(weighted_total / sum(category_weights.values()))

    blocking_failures = [result.rule_id for result in results if result.blocking and result.status == "fail"]
    status = _overall_status(int(overall_score), blocking_failures)

    recommendations = _recommendations(results)
    return ScorecardResult(
        service_name=service.service.name,
        tier=service.service.tier,
        lifecycle=service.service.lifecycle,
        overall_score=int(overall_score),
        status=status,
        category_scores=category_scores,
        rule_results=results,
        blocking_failures=blocking_failures,
        recommendations=recommendations,
    )

