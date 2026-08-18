# Configurable metric definitions

All organization-specific definitions come from the local JSON configuration. The Skill repository contains no fixed rating threshold, category taxonomy, minimum sample size, ranking limit, country list, or report calendar.

## Core rows

- Rating row: a configured all-reviews row with a valid rating from 1 through 5.
- Comment row: a rating row whose configured review-text field is nonblank after trimming.
- Low and high rating groups: the exact integer lists in `metrics.low_ratings` and `metrics.high_ratings`.
- Classified-row denominator: the validated rows in the configured classified-reviews sheet.

## Classifications

Require exact labels from `classification.categories`. Resolve the subcategory field through `classification.subcategory_columns`, keyed by category label. Keep workbook labels unchanged except surrounding whitespace.

Use `classification.representative_category` only for representative-issue ranking. Do not assume any category meaning from its name.

## Percentages and changes

- Score precision: `format.score_decimals`.
- Percentage precision: `format.percentage_decimals`.
- Count change: `(current - previous) / previous` when the previous value is nonzero.
- Rate change: current rate minus previous rate.
- Missing or zero denominators: display the configured unavailable marker.

## Version metrics

Use the configured comment-only or all-rating scope. Exclude blank version names. Apply `metrics.version_min_comments`, rank by configured keys, and keep `metrics.version_top_n` rows. Never substitute repository defaults.

## Representative issues

Use `metrics.issue_top_n` subcategories from the configured representative category. Select only comments within the configured length bounds. Redact direct and indirect personal identifiers before report insertion.

## Monthly score history

Store year-series values in `metrics.json`:

```json
{
  "monthly_score_history": {
    "<YEAR>": ["<JAN_SCORE>", "<FEB_SCORE>"]
  },
  "monthly_score_note": "<DATA_CUTOFF_NOTE>"
}
```

The placeholders above are schema markers, not real data. Replace them only in task-local files. Store numeric scores from 1 to 5, keep months in January-onward order, label existing points to the configured precision, and leave unavailable future months absent.

