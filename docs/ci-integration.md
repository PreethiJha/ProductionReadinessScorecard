# CI Integration

The CLI is designed to run inside CI and return one of these exit codes:

- `0` success
- `1` score below threshold or blocking failures
- `2` invalid input
- `3` runtime error

Example:

```bash
production-readiness-scorecard evaluate \
  --service examples/checkout-service.yaml \
  --rules examples/rules.yaml \
  --output reports/checkout-readiness.md \
  --json-output reports/checkout-readiness.json \
  --fail-below 80
```

