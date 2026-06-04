"""Report formatting helpers.

The reporter produces human-readable Markdown and machine-readable JSON
artifacts from a validated scorecard result. Keeping this separate from the
CLI makes the output easier to test and reuse.
"""

from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Template

from .models import ScorecardResult


MARKDOWN_TEMPLATE = Template(
    """# Production Readiness Report

Service: {{ result.service_name }}  
Tier: {{ result.tier }}  
Lifecycle: {{ result.lifecycle }}  

## Summary

Overall Score: {{ result.overall_score }}/100  
Status: {{ result.status }}  

| Category | Score |
|---|---:|
{% for category in result.category_scores -%}
| {{ category.category|capitalize }} | {{ category.score }} |
{% endfor %}

## Blocking Failures
{% if result.blocking_failures %}
{% for failure in result.blocking_failures -%}
- {{ failure }}
{% endfor %}
{% else %}
- None
{% endif %}

## Failed Checks
{% set failed = result.rule_results | selectattr("status", "equalto", "fail") | list %}
{% if failed %}
{% for rule in failed -%}
### {{ rule.rule_id }}

{{ rule.description }}

**Recommendation:**  
{{ rule.recommendation }}

{% endfor %}
{% else %}
- None
{% endif %}

## Warnings
{% set warned = result.rule_results | selectattr("status", "equalto", "warn") | list %}
{% if warned %}
{% for rule in warned -%}
### {{ rule.rule_id }}

{{ rule.description }}

**Recommendation:**  
{{ rule.recommendation }}

{% endfor %}
{% else %}
- None
{% endif %}

## Passed Checks
{% for rule in result.rule_results if rule.status == "pass" -%}
- {{ rule.rule_id }}
{% endfor %}

## Top Follow-ups
{% if result.recommendations %}
{% for recommendation in result.recommendations -%}
{{ loop.index }}. {{ recommendation }}
{% endfor %}
{% else %}
- None
{% endif %}
"""
)


def render_markdown_report(result: ScorecardResult) -> str:
    """Render the Markdown report body for a scorecard result."""

    return MARKDOWN_TEMPLATE.render(result=result)


def write_markdown_report(result: ScorecardResult, path: str | Path) -> Path:
    """Write a Markdown report to disk, creating parent folders as needed."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown_report(result))
    return output_path


def write_json_report(result: ScorecardResult, path: str | Path) -> Path:
    """Write the JSON report to disk, creating parent folders as needed."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result.model_dump(mode="json"), indent=2))
    return output_path
