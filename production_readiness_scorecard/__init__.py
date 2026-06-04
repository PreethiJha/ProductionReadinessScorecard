"""Production Readiness Scorecard.

This package provides a CLI-first evaluator for service readiness metadata.
The main public entry points are:

- ``load_service_metadata``: parse and validate a service YAML file
- ``load_rules_config``: parse and validate the rules YAML file
- ``evaluate_scorecard``: compute rule results, category scores, and status
"""

from .models import ScorecardResult
from .parser import load_rules_config, load_service_metadata
from .scorer import evaluate_scorecard

__all__ = [
    "ScorecardResult",
    "evaluate_scorecard",
    "load_rules_config",
    "load_service_metadata",
]
