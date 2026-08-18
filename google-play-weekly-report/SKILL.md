---
name: google-play-weekly-report
description: Create a configurable Google Play rating and review Word report from a previous DOCX template, a processed XLSX workbook, and a local JSON configuration. Use when Codex must audit row-level review data, calculate organization-defined metrics, collect configured Play Console ratings or reviews with the in-app browser, update charts and narrative, and verify that the final DOCX fits the page. No company-specific countries, periods, categories, or thresholds are built in.
---

# Google Play Weekly Report

Produce one final Word report. Treat the current workbook as the row-level data authority, the previous report as the layout and historical-data authority, and the local configuration as the only authority for organization-specific rules.

## Companion skills

Use these skills in order:

1. `spreadsheets` to inspect and verify the XLSX.
2. `browser:control-in-app-browser` to obtain configured Play Console data.
3. `documents` to edit, render, and verify the DOCX.

Read [references/workflow-contract.md](references/workflow-contract.md), [references/metric-definitions.md](references/metric-definitions.md), and [references/document-layout.md](references/document-layout.md) before acting. Read [references/browser-backend.md](references/browser-backend.md) before browser work.

## Required inputs

Require one previous-period `.docx` report, one current processed `.xlsx` workbook, and one local JSON configuration based on [assets/config.template.json](assets/config.template.json).

Never infer or embed a product name, reporting period, country list, rating group, category taxonomy, ranking limit, chart label, or output filename. Pause when a required configuration value is blank, empty, null, or still contains angle-bracket placeholders.

## Workflow

### 1. Validate configuration and period

Confirm that the configured start and end dates match the intended report period. Use `require_every_date` only as configured. Pause if workbook rows fall outside the configured period or the intended period is ambiguous.

### 2. Audit inputs

Create a task-local work directory outside the Skill repository. Run:

```powershell
python scripts/audit_week_inputs.py `
  --workbook "<current.xlsx>" `
  --previous-report "<previous.docx>" `
  --config "<report-config.json>" `
  --output "<workdir>\input-audit.json"
```

Stop for any `needs_user` issue. Do not silently remove duplicates, repair dates, change classifications, or fill missing fields.

### 3. Calculate metrics

```powershell
python scripts/build_week_metrics.py `
  --audit "<workdir>\input-audit.json" `
  --config "<report-config.json>" `
  --output "<workdir>\metrics-base.json"
```

Recompute summaries from row-level sheets. Treat workbook summary sheets only as optional cross-checks.

### 4. Read the previous report

```powershell
python scripts/extract_previous_report.py `
  --input "<previous.docx>" `
  --output "<workdir>\previous-report.json"
```

Use the previous report only for prior-period values, reliable historical values, wording style, and layout. Pause if a required value cannot be identified reliably.

### 5. Obtain configured Play Console data

Use only the current signed-in in-app browser tab and the target app supplied by the user. Collect only fields explicitly requested under `console` in the local configuration. Skip empty lists. Never substitute public web-search data for Console data.

If authentication, permission, two-factor verification, CAPTCHA, or session expiry blocks access, ask the user to complete it. Never inspect cookies, passwords, tokens, or session storage. Store normalized results only in the task work directory.

### 6. Handle classifications

Preserve workbook classifications exactly. Never replace manual classifications with an automated classifier. Classify newly collected rows only when the user supplies a taxonomy and rules outside this repository. Otherwise ask whether those rows should be excluded or manually classified.

### 7. Select representative issues

Use the configured `representative_category`, `issue_top_n`, and comment-length bounds. Rank exact subcategory names by count, use an alphabetical tie-break unless another rule is supplied, select clear comments, redact personal identifiers, and never manufacture categories or examples.

### 8. Update history and charts

Continue historical values only when the previous report provides a reliable source. Do not fabricate missing months.

```powershell
python scripts/generate_report_charts.py `
  --metrics "<workdir>\metrics.json" `
  --config "<report-config.json>" `
  --output-dir "<workdir>\charts"

python scripts/generate_monthly_score_chart.py `
  --metrics "<workdir>\metrics.json" `
  --config "<report-config.json>" `
  --output "<workdir>\charts\monthly-score-trend.png"
```

Label every existing monthly point with its exact score using configured precision. Offset close labels and leave unavailable future months blank.

### 9. Build the report

Copy the previous DOCX and make minimal local edits. Preserve page setup, title hierarchy, table structure, colors, fonts, and reliable historical values. Update only sections supported by current data and configured Console collection. Use the configured title and filename. Do not overwrite an existing output without asking.

Write only evidence-supported facts. Do not infer root causes or recommend product changes unless requested.

### 10. Validate and render

```powershell
python scripts/validate_final_report.py `
  --report "<final.docx>" `
  --metrics "<workdir>\metrics.json" `
  --config "<report-config.json>"
```

Use the `documents` render workflow and inspect every page at 100%. Do not call the report final until visual QA or explicit user confirmation is complete.

## Deliverable

Return only the final DOCX link unless supporting data is requested. Keep configuration, audits, JSON, charts, previews, and reports outside the Skill repository.

