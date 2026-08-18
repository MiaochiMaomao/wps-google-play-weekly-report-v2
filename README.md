# Google Play Weekly Report Skill

**Author:** 潘鑫

A reusable Codex Skill for producing a Google Play review and rating report from a previous DOCX template, a processed XLSX workbook, and a user-supplied configuration file.

The public repository contains no company name, product name, app identifier, fixed country list, reporting calendar, classification taxonomy, rating threshold, ranking threshold, or real business data. Every organization-specific rule is supplied at runtime through a local configuration file that must not be committed.

## Capabilities

- Audit row-level review and rating data before report generation.
- Recalculate rating, comment, classification, subcategory, and version metrics.
- Reuse the previous DOCX report as the layout and historical-data template.
- Collect only the Play Console metrics and countries requested in the local configuration.
- Generate category, subcategory, and monthly rating charts.
- Validate report dates, figures, placeholders, document integrity, and page geometry.
- Require visual rendering before final delivery.

## Required inputs

1. A previous-period Word report used as the layout template.
2. A processed Excel workbook containing one row-level all-reviews sheet and one row-level classified-reviews sheet.
3. A local JSON configuration derived from [`config.template.json`](google-play-weekly-report/assets/config.template.json).

The configuration defines the reporting period, sheet and column mappings, rating groups, category labels, subcategory mappings, ranking limits, countries, chart labels, and output filename. Placeholder or missing values cause the Skill to pause instead of guessing.

## Repository structure

```text
.
├── README.md
├── .gitignore
└── google-play-weekly-report/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── assets/config.template.json
    ├── references/
    └── scripts/
```

## Installation

```powershell
git clone https://github.com/YOUR_GITHUB_USERNAME/google-play-weekly-report.git
Copy-Item -Recurse -Force `
  '.\google-play-weekly-report\google-play-weekly-report' `
  "$env:USERPROFILE\.codex\skills\google-play-weekly-report"
```

Restart or refresh Codex, then invoke `$google-play-weekly-report`.

## Example request

```text
Use $google-play-weekly-report with my previous DOCX, processed XLSX,
and local report-config.json to create this period's Google Play report.
```

## Data protection

- Keep runtime configuration, reports, workbooks, exports, screenshots, browser profiles, logs, and generated JSON outside this repository.
- Never commit app IDs, developer IDs, account indexes, package names, private Console URLs, credentials, session data, personal information, real reviews, or real metrics.
- Redact personal identifiers before placing representative comments in a report.
- Inspect the Git staging area and reachable history before every public push.
- If sensitive data enters Git history, rewrite the history; a later deletion commit is insufficient.

This repository does not grant access to Google Play Console and does not bypass authentication, authorization, two-factor authentication, or CAPTCHA controls.
