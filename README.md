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

## How The Code Is Structured

- `production_readiness_scorecard/parser.py` reads YAML and validates inputs
- `production_readiness_scorecard/rules.py` evaluates each rule against metadata
- `production_readiness_scorecard/scorer.py` computes category and overall scores
- `production_readiness_scorecard/reporter.py` renders Markdown and JSON reports
- `production_readiness_scorecard/cli.py` wires the user-facing command

## Project Layout

- `production_readiness_scorecard/` core implementation
- `examples/` sample service and rule inputs
- `tests/` unit and integration coverage
- `docs/` usage and scoring notes
- `CONTRIBUTING.md` project contribution guide
- `LICENSE` project license text
