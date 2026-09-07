# Public schema v1

`site/data.json` holds `schema_version`, `updated_at`, public methodology/notice, and `items`. Item IDs are stable research identifiers for merging updates, not ownership or purchase records. Each item has name, summary, evidence[], gaps, sources[{label,url}], category, scope, nullable fit rank, recommendation, status and nullable image {path,source_url,alt,kind}. URLs must be public HTTPS. Images must resolve within the media allowlist.

`site/procurement.json`: schema_version=1, destination_zip="10014", quantity=1, currency="USD", status, methodology, builds[]. Each build has:

- `id`, `name`, nullable `fit_rank`, `checked_at` (YYYY-MM-DD).
- `price_usd`: dated board/bundle subtotal or null; `price_status` explains included variant and partial totals.
- `wifi_total_usd`, `cellular_total_usd`, `shipping_usd`, `tax_usd`: number or null. Complete hardware totals exclude shipping and tax; those are added for affordability sorting. Separate service, tools, labor and engineering exclusions explicitly.
- `complete`: true only when the required Wi-Fi parts BOM is fully specified, compatible and costed. Never set true just because the board has a price.
- `arrival_earliest`, `arrival_latest`: ISO dates or null, for **all required parts**, not one board. `delivery_status` must label seller quote vs estimate, stock, origin, dispatch/transit scope and uncertainty. Do not infer free shipping or promised dates.
- `purchase_list`, `assembly_list`, `cellular_additions`: arrays of disclosed requirements; replace generic pending lists with exact cited parts as research lands.
- `sources`: public {label,url} evidence. Add source-specific dates in notes when observations differ.

`python3 scripts/update_procurement.py reviewed.json` accepts a document with `builds` containing full schema-compatible replacement rows, merged by ID. Unknown IDs are refused. The update validates before writing. Research fragments must be normalized/reviewed into this schema; do not blindly publish worker notes. Commit and redeploy after validation; the live origin serves the site directory.

Fit is a transparent desk-review priority, not a measured score. Affordability ranks only complete builds with known Wi-Fi/shipping/tax amounts. Fastest ranks complete builds with a known latest all-parts arrival date. Unresolved builds sort last; no winner is asserted when all are unknown. Cellular is unqualified and separate from Wi-Fi fit rankings.
