# Production Readiness Scorecard

CLI-first tool for evaluating whether a service is ready for production using YAML metadata and tier-aware readiness rules.

## Install

```bash
pip install -e .
```

## Run

```bash
production-readiness-scorecard evaluate \
  --service examples/checkout-service.yaml \
  --rules examples/rules.yaml \
  --output reports/checkout-readiness.md \
  --json-output reports/checkout-readiness.json \
  --fail-below 80
```

## What it does

- loads `service.yaml`
- loads `rules.yaml`
- evaluates readiness checks
- computes category and overall scores
- generates terminal, Markdown, and JSON reports
- exits with CI-friendly status codes

## Project Layout

- `production_readiness_scorecard/` core implementation
- `examples/` sample service and rule inputs
- `tests/` unit and integration coverage
- `docs/` usage and scoring notes

