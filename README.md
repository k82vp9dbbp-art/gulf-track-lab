# Gulf Track Lab

Self-contained cyclone forecast explorer with bounded map zoom, movable location reference, contextual help, intensity charts, and ensemble coverage calculations.

## Data-sharing status

Google’s terms for real-time experimental data restrict public sharing of retrievable future forecasts. Public deployment does not establish redistribution rights. The current deployment workflow retains the previously supplied WNV3 data; do not replace it with a current/future FNV3P2 or OPER export on a public branch. A local-only build can use fresh data, or an eligible historical export can be published when all forecast valid times are at least one hour old under the linked September 2026 terms. The `--public` option enforces that age check. Retain source notices and attribution.

## Build

Run `python3 scripts/build.py`, then open `site/index.html`. Python 3.9+ is sufficient; no third-party Python packages are required. All forecast data, geographic geometry and D3 are embedded, so the dashboard has no network dependency.

The initial published forecast is AL092026, initialized 2026-10-09 00:00 UTC, with 64 ensemble members and 446 positions. The reference defaults to a public street-level point on Dawn Lane, not a house address. It can be moved or entered as coordinates.

## Repeatable updates

The build supports different ensemble sizes, including the 64-member WNV3 and 50-member FNV3P2 and OPER cyclone forecast products. It validates field names, time consistency, numeric bounds, unique points and sequential ensemble member IDs before producing the dashboard. Forecast model identity is explicit: `--model WNV3`, `--model FNV3P2`, or `--model OPER`. The filename can supply an identity when building a specifically named CSV locally, but `data/latest.csv` does not encode the model: update the workflow’s `--model` argument whenever you replace the forecast source. The model name, ensemble count and initialization are shown in the dashboard; the site build time is separate.

Enable GitHub Pages with Source set to GitHub Actions. The included workflow builds and deploys on pushes to `main`. A failed data validation prevents deployment. Viewers reload the same link to see updates.

## Sources and limitations

Google DeepMind Weather Lab / WeatherNext 3 Cyclones experimental forecast data, copyright 2024–2026 Google LLC. Data rights are separate from application code. Retain the notices in the source CSV and follow the linked terms. Historical data is identified in the supplied export as CC BY 4.0: https://creativecommons.org/licenses/by/4.0/.

Natural Earth geographic coastline; D3 7.9.0 (ISC license, notice retained in bundled script).

Interpolated tracks, pointwise medians and percentile ranges are computed locally. Wind footprint counts are model coverage counts, not calibrated probabilities or exact local wind predictions. Coastline landfall estimates omit some small islands. Use official advisories for preparation and safety decisions.
