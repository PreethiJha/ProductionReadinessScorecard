# Rule Authoring

Rules live in `examples/rules.yaml` for the MVP and follow this structure:

- `id`
- `category`
- `description`
- `field`
- `required_for_tiers`
- `severity`
- `recommendation`
- optional `expected_value`
- optional `condition`

## Tips

- Keep field paths dot-separated, such as `security.retention_policy`
- Use `condition` for checks that only apply when another field has a specific value
- Use `severity` to control score impact
- Use `blocking: true` for rules that should cap launch readiness when they fail

