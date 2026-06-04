# Contributing

Thanks for helping improve Production Readiness Scorecard.

## Local Setup

```bash
pip install -e .
pytest
```

## Development Guidelines

- Keep the CLI output deterministic and easy to read in CI logs.
- Add or update tests for any behavior change.
- Prefer small, focused changes that are easy to review.
- Keep YAML schema changes aligned across `examples/`, `models.py`, and `tests/`.

## Suggested Workflow

1. Make the change.
2. Run `pytest`.
3. Verify the CLI still works with the example inputs.
4. Update docs when behavior or flags change.

## Pull Requests

- Describe the user-facing change.
- Mention any scoring or rule behavior changes.
- Include test results when possible.

