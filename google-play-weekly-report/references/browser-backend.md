# Play Console browser collection

Start from the user's active, signed-in Play Console tab for the target app, or a target-app page explicitly supplied by the user.

Never hardcode or publish an account index, developer ID, app ID, package name, private URL, or organization-specific navigation path.

## Collection scope

Read the local configuration before browser work. Collect only:

- rating fields named in `console.rating_fields`;
- country or region ratings listed in `console.rating_countries`;
- review rows for countries or regions listed in `console.review_countries`;
- release metadata requested in `console.release_fields`.

Skip empty lists. Do not add countries, metrics, versions, or date rules from memory.

For review collection, use the configured start and end dates. Capture only the configured review fields and paginate through the final page. Do not capture developer replies unless the configuration explicitly requests them.

Prefer a supported batch call from the signed-in page when available. Verify totals, filters, and pagination completion.

## Authentication

Use the in-app browser only. If authentication or permission blocks access, ask the user to complete it. Do not inspect cookies, storage, credentials, tokens, or passwords.

