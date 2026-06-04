from pathlib import Path

import pytest

from production_readiness_scorecard.parser import ScorecardInputError, load_rules_config, load_service_metadata


def test_load_service_metadata():
    service = load_service_metadata(Path("examples/checkout-service.yaml"))
    assert service.service.name == "checkout-service"
    assert service.service.tier == "critical"


def test_load_rules_config():
    rules = load_rules_config(Path("examples/rules.yaml"))
    assert len(rules.rules) > 0
    assert rules.scorecard.categories["ownership"].weight == 15


def test_invalid_yaml_raises(tmp_path: Path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("service: [")
    with pytest.raises(ScorecardInputError):
        load_service_metadata(bad)

