# Freedom Lab hardware

Public, read-only voice-device research: https://hardware.freedomlab.nyc/

E-ink, physical push-to-talk, spoken replies and independent networking are the target. No ready cellular kit is verified. Prices are observed board/bundle prices, **not complete build quotes**. Shipping, tax, complete-build costs and arrival dates remain pending for quantity 1, ZIP 10014. Unknown does not mean free.

## Build and run

Python 3, no build dependencies:

```sh
python3 scripts/build.py
python3 tests/test_public.py
python3 -m http.server 8080 --bind 127.0.0.1 --directory site
```

Deploy only `site/`, never the repository root. There is no backend, login, database or write API. Sources and image provenance remain attached to each record. Product images belong to their respective owners; inclusion is research attribution, not a claim of a redistribution license or endorsement.

## Updates

See [data schema](docs/schema.md). Edit reviewed public data, then build and validate. `scripts/update_procurement.py` merges a reviewed procurement document by stable record ID. Do not import raw source collections. Unknown values stay null; dates and shipping labels must distinguish estimates from seller quotes.

The universal presentation is in `shared/styles.css` and `shared/display-template.css`; the build copies these byte-for-byte into the static bundle. To synchronize from another canonical template checkout, pass `--shared-source DIRECTORY` pointing to its CSS directory. This is an explicit two-file copy, not a project import. The renderer and procurement styles remain collection-specific. Breakpoints: 4 columns above 1100px, 3 above 900px, 2 above 600px, 1 on phones. Changes to shared geometry must be coordinated with every consumer.

Browser smoke (install Playwright + Chromium first): `python3 tests/browser_smoke.py http://127.0.0.1:8080`. Screenshots are saved outside the published tree.
