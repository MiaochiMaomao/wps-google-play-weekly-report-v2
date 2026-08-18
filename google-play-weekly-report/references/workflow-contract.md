# Workflow contract

## Authority order

Use this priority:

1. Local configuration for period, mappings, categories, thresholds, countries, labels, and output rules.
2. Current workbook classified rows for manual classifications.
3. Current workbook all-review rows for current rating and comment metrics.
4. Current authorized Play Console data for configured live metrics.
5. Previous report for prior-period values, reliable history, wording style, and layout.

Never let automated classification overwrite workbook classifications.

## Pause gates

Pause and ask when:

- a required configuration value is blank, null, empty, or still a placeholder;
- the configured period is ambiguous or workbook rows fall outside it;
- a required sheet, column, previous value, or configured Console metric is missing;
- an exact duplicate row, invalid date, or invalid rating exists;
- classified row coverage does not match the configured low-rating comment population;
- a category or required subcategory is invalid or blank;
- Play Console authentication or permission blocks access;
- the output file already exists;
- final visual rendering cannot be completed.

## Inputs and outputs

Do not alter input files. Keep task data outside the Skill repository. Deliver one final DOCX by default and intermediate files only when requested.

## Writing

Match the previous report's tone and length. State only supported facts. Cover only sections enabled by the configuration and available evidence. Do not infer product causes or recommend changes without a user request.

