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

The image-led procurement comparison joins each build to `data.json` by stable ID and reuses its exact existing image. Missing source images stay explicit; no substitute is invented. The original catalog remains separate and its filters do not hide procurement cards. Both use the shared four-column display template (one column on phones).

Additive audited procurement fields (schema v1):

- `build_status`, `bom[]`: exact line items with `name`, `quantity`, nullable `unit_price_usd`, `role` (purchase, included / verify package, unresolved purchase, not required), stock/qualification `status`, nullable public `source_url`, nullable `shipment_group`, and `note` describing included components and compatibility gaps. Included lines cost zero additional dollars, not zero replacement cost.
- `known_parts_subtotal_usd`: sum of priced BOM lines; may include an explicitly out-of-stock reference price. Null for uncosted reference-only directions. Never implies qualification or procurement readiness.
- `shipments[]`: seller, scope, nullable shipping_usd, quote/policy/unknown status, explanatory note, source_url and nullable arrival dates for that shipment only. Optional `services[]` preserves alternate quoted rates, duty inclusion, cart day ranges/units and separate policy processing/transit days. These are alternatives, never summed. Grouped freight is charged once, not per component. Cart day ranges and policy business-day ranges remain distinct; do not manufacture calendar arrival dates.
- `known_shipping_usd`: sum of known freight portions (unknown if none quoted). `known_parts_plus_quoted_shipping_usd` is the partial priced-parts subtotal plus those portions. Unknown remaining freight, required unpriced parts and tax are not zero. `delivered_total_usd` is null unless the qualified full Wi-Fi BOM plus all freight and tax is known.
- `offers[]`: separately scoped exact or near-match packages, with source_url, price_usd, shipping_usd, item_plus_shipping_usd, nullable package arrival dates, match, status and note. Prime and minimum-order conditions must remain visible. These never populate row-level all-parts dates or complete-build totals.
- `alternatives[]`: mutually exclusive hardware scenarios with name, known_parts_subtotal_usd, nullable known_parts_plus_quoted_shipping_usd, note and full bom. Never sum these scenarios with the baseline.

`python3 scripts/update_procurement.py reviewed.json` accepts a document with `builds` containing full schema-compatible replacement rows, merged by ID. Unknown IDs are refused. The update validates before writing. Research fragments must be normalized/reviewed into this schema; do not blindly publish worker notes. Commit and redeploy after validation; the live origin serves the site directory.

Fit is a transparent desk-review priority, not a measured score. The separate known-subtotal control sorts priced lines only and is explicitly not an affordability ranking. Affordability ranks only complete builds with known Wi-Fi/shipping/tax amounts. Fastest ranks complete builds with a known latest all-parts arrival date. Unresolved builds sort last; no winner is asserted when all are unknown. Cellular is unqualified and separate from Wi-Fi fit rankings.
