# Scoring Model

The scorecard evaluates each rule as `pass`, `fail`, `warn`, or `skip`.

## Rule Scoring

- `pass` earns the full points for the rule severity
- `warn` earns half the points
- `fail` earns zero points
- `skip` does not count toward the category

Severity points:

- critical: 10
- high: 7
- medium: 4
- low: 2

## Category Score

Category score is calculated from earned points divided by possible points for that category.

## Overall Score

Overall score is a weighted average of the category scores.

## Status Bands

- 90-100: Ready
- 80-89: Ready with Follow-ups
- 60-79: Needs Attention
- 0-59: Not Ready

Blocking failures cap the final status at Needs Attention.

