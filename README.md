# Gulf Track Lab

Self-contained cyclone forecast explorer with bounded map zoom, movable location reference, contextual help, intensity charts, and ensemble coverage calculations.

## Data-sharing status

Google’s recent/future forecast sharing restriction remains unresolved. The owner requested public publication now and will address it separately. Public deployment does not establish permission to redistribute the embedded data. The deployment workflow validates and builds the supplied forecast without invoking the optional historical-data age check. Source CSV notices are retained.

## Build

Run `python3 scripts/build.py`, then open `site/index.html`. Python 3.9+ is sufficient; no third-party Python packages are required. All forecast data, geographic geometry and D3 are embedded, so the dashboard has no network dependency.

The initial forecast is AL092026, initialized 2026-10-09 00:00 UTC, with 64 ensemble members and 446 positions. The reference defaults to a public street-level point on Dawn Lane, not a house address. It can be moved or entered as coordinates.

## Repeatable updates

Replace `data/latest.csv` with a newly validated WeatherNext Cyclones ensemble export and run the build script. It validates the field names, time consistency, numeric bounds, duplicate points and all 64 members before producing the dashboard. It records the build time; the dashboard displays forecast initialization separately.

Enable GitHub Pages with Source set to GitHub Actions. The included workflow builds and deploys on pushes to `main`. A failed data validation prevents deployment. Viewers reload the same link to see updates.

## Sources and limitations

Google DeepMind Weather Lab / WeatherNext 3 Cyclones experimental forecast data, copyright 2024–2026 Google LLC. Data rights are separate from application code. Retain the notices in the source CSV and follow the linked terms. Historical data is identified in the supplied export as CC BY 4.0: https://creativecommons.org/licenses/by/4.0/.

Natural Earth geographic coastline; D3 7.9.0 (ISC license, notice retained in bundled script).

Interpolated tracks, pointwise medians and percentile ranges are computed locally. Wind footprint counts are model coverage counts, not calibrated probabilities or exact local wind predictions. Coastline landfall estimates omit some small islands. Use official advisories for preparation and safety decisions.
