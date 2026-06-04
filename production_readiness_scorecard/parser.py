from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .models import RulesConfig, ServiceMetadata


class ScorecardInputError(ValueError):
    """Raised when YAML input cannot be parsed or validated."""


def _load_yaml(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        raise ScorecardInputError(f"File not found: {file_path}")
    try:
        raw = yaml.safe_load(file_path.read_text())
    except yaml.YAMLError as exc:  # pragma: no cover - exercised via invalid-yaml test
        raise ScorecardInputError(f"Invalid YAML in {file_path}: {exc}") from exc
    if raw is None:
        raise ScorecardInputError(f"Empty YAML file: {file_path}")
    if not isinstance(raw, dict):
        raise ScorecardInputError(f"Expected a YAML mapping in {file_path}")
    return raw


def load_service_metadata(path: str | Path) -> ServiceMetadata:
    try:
        return ServiceMetadata.model_validate(_load_yaml(path))
    except ValidationError as exc:
        raise ScorecardInputError(str(exc)) from exc


def load_rules_config(path: str | Path) -> RulesConfig:
    try:
        return RulesConfig.model_validate(_load_yaml(path))
    except ValidationError as exc:
        raise ScorecardInputError(str(exc)) from exc

