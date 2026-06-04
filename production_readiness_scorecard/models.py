from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

Tier = Literal["critical", "high", "medium", "low"]
Severity = Literal["critical", "high", "medium", "low"]
RuleStatus = Literal["pass", "fail", "warn", "skip"]
ReadinessStatus = Literal["Ready", "Ready with Follow-ups", "Needs Attention", "Not Ready"]

DEFAULT_CATEGORY_WEIGHTS: dict[str, int] = {
    "ownership": 15,
    "operations": 15,
    "slo": 15,
    "observability": 15,
    "alerts": 15,
    "dependencies": 10,
    "security": 10,
    "api": 5,
}

SEVERITY_POINTS: dict[str, int] = {
    "critical": 10,
    "high": 7,
    "medium": 4,
    "low": 2,
}


class ServiceInfo(BaseModel):
    """Top-level service identity and ownership metadata."""

    model_config = ConfigDict(extra="ignore")

    name: str
    owner: str | None = None
    tier: Tier
    lifecycle: str
    language: str | None = None
    repository: str | HttpUrl | None = None


class OwnershipMetadata(BaseModel):
    """Human ownership and escalation metadata for a service."""

    model_config = ConfigDict(extra="ignore")

    slack_channel: str | None = None
    on_call_rotation: str | None = None
    business_owner: str | None = None
    escalation_policy: str | None = None


class OperationsMetadata(BaseModel):
    """Operational recovery and deployment metadata."""

    model_config = ConfigDict(extra="ignore")

    runbook: str | None = None
    dashboard: str | None = None
    rollback_plan: str | None = None
    rollback_tested: bool | None = None
    deployment_strategy: str | None = None
    known_failure_modes: str | None = None


class SloMetadata(BaseModel):
    """Service-level objective targets used to assess reliability posture."""

    model_config = ConfigDict(extra="ignore")

    availability_target: float | None = None
    latency_p95_ms: int | None = None
    error_rate_percent: float | None = None


class ObservabilityMetadata(BaseModel):
    """Telemetry and operator visibility signals."""

    model_config = ConfigDict(extra="ignore")

    health_endpoint: str | None = None
    readiness_endpoint: str | None = None
    dashboard: str | None = None
    metrics_enabled: bool | None = None
    tracing_enabled: bool | None = None
    logs_structured: bool | None = None


class AlertsMetadata(BaseModel):
    """Alerting posture for the service."""

    model_config = ConfigDict(extra="ignore")

    high_error_rate: bool | None = None
    high_latency: bool | None = None
    dependency_failure: bool | None = None
    saturation: bool | None = None
    routed_to_on_call: bool | None = None


class DependenciesMetadata(BaseModel):
    """Downstream and upstream dependency references."""

    model_config = ConfigDict(extra="ignore")

    services: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)
    external: list[str] = Field(default_factory=list)
    timeout_strategy: str | None = None
    retry_strategy: str | None = None


class SecurityMetadata(BaseModel):
    """Security and data-handling posture."""

    model_config = ConfigDict(extra="ignore")

    authentication_required: bool | None = None
    authorization_model: str | None = None
    data_classification: str | None = None
    secrets_managed: bool | None = None
    pii_access: bool | None = None
    retention_policy: str | None = None


class ApiMetadata(BaseModel):
    """API compatibility and lifecycle metadata."""

    model_config = ConfigDict(extra="ignore")

    openapi_spec: str | None = None
    versioning_strategy: str | None = None
    backward_compatibility_notes: str | None = None
    deprecation_policy: str | None = None


class ServiceMetadata(BaseModel):
    """Validated service metadata loaded from ``service.yaml``."""

    model_config = ConfigDict(extra="ignore")

    service: ServiceInfo
    ownership: OwnershipMetadata = Field(default_factory=OwnershipMetadata)
    operations: OperationsMetadata = Field(default_factory=OperationsMetadata)
    slo: SloMetadata = Field(default_factory=SloMetadata)
    observability: ObservabilityMetadata = Field(default_factory=ObservabilityMetadata)
    alerts: AlertsMetadata = Field(default_factory=AlertsMetadata)
    dependencies: DependenciesMetadata = Field(default_factory=DependenciesMetadata)
    security: SecurityMetadata = Field(default_factory=SecurityMetadata)
    api: ApiMetadata = Field(default_factory=ApiMetadata)


class RuleCondition(BaseModel):
    """Optional predicate that gates whether a rule applies."""

    model_config = ConfigDict(extra="ignore")

    field: str
    equals: Any


class CategoryWeight(BaseModel):
    """Configured weight for a scorecard category."""

    model_config = ConfigDict(extra="ignore")

    weight: int


class RuleConfig(BaseModel):
    """A single production-readiness rule definition."""

    model_config = ConfigDict(extra="ignore")

    id: str
    category: str
    description: str
    field: str
    required_for_tiers: list[Tier]
    severity: Severity
    recommendation: str
    expected_value: Any | None = None
    condition: RuleCondition | None = None
    blocking: bool = False

    @field_validator("required_for_tiers")
    @classmethod
    def ensure_required_tiers(cls, value: list[Tier]) -> list[Tier]:
        if not value:
            raise ValueError("required_for_tiers must not be empty")
        return value


class ScorecardConfig(BaseModel):
    """Top-level scorecard settings and category weighting."""

    model_config = ConfigDict(extra="ignore")

    passing_score: int = 80
    categories: dict[str, CategoryWeight] = Field(default_factory=dict)

    @model_validator(mode="after")
    def ensure_categories(self) -> "ScorecardConfig":
        merged = {
            name: self.categories.get(name, CategoryWeight(weight=weight))
            for name, weight in DEFAULT_CATEGORY_WEIGHTS.items()
        }
        extra_categories = {name: cfg for name, cfg in self.categories.items() if name not in merged}
        merged.update(extra_categories)
        self.categories = merged
        total = sum(category.weight for category in self.categories.values())
        if total != 100:
            raise ValueError(f"category weights must sum to 100, got {total}")
        return self


class RulesConfig(BaseModel):
    """Validated rule document loaded from ``rules.yaml``."""

    model_config = ConfigDict(extra="ignore")

    scorecard: ScorecardConfig
    rules: list[RuleConfig]

    @model_validator(mode="after")
    def ensure_rules_present(self) -> "RulesConfig":
        if not self.rules:
            raise ValueError("rules must not be empty")
        return self


class RuleResult(BaseModel):
    """Result of evaluating one rule against one service."""

    model_config = ConfigDict(extra="ignore")

    rule_id: str
    category: str
    status: RuleStatus
    severity: Severity
    score_impact: float
    description: str
    actual_value: Any | None = None
    expected_value: Any | None = None
    recommendation: str
    blocking: bool = False


class CategoryScore(BaseModel):
    """Score and counters for one readiness category."""

    model_config = ConfigDict(extra="ignore")

    category: str
    score: int
    passed: int
    failed: int
    warnings: int
    skipped: int


class ScorecardResult(BaseModel):
    """Full evaluation output returned by the scoring engine."""

    model_config = ConfigDict(extra="ignore")

    service_name: str
    tier: Tier
    lifecycle: str
    overall_score: int
    status: ReadinessStatus
    category_scores: list[CategoryScore]
    rule_results: list[RuleResult]
    blocking_failures: list[str]
    recommendations: list[str]
