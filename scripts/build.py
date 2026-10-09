"""Build a self-contained dashboard from Google's cyclone CSV. No dependencies."""
import argparse
import csv
import datetime as dt
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["lead_time_hours", "lon", "lat", "maximum_sustained_wind_speed_knots",
          "minimum_sea_level_pressure_hpa", "radius_of_maximum_winds_km"] + [
    f"radius_{w}_knot_winds_{q}_km" for w in (34, 50, 64) for q in ("ne", "se", "sw", "nw")]

def timestamp(value):
    result = dt.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    return result.replace(tzinfo=dt.timezone.utc) if result.tzinfo is None else result

def build(csv_path, storm, output, public):
    with csv_path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(line for line in source if line.strip() and not line.lstrip().startswith("#"))
        required = {"init_time", "track_id", "sample", "valid_time", *FIELDS}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Missing required CSV fields")
        rows = [row for row in reader if row["track_id"] == storm]
    if not rows:
        raise ValueError(f"No data for {storm}")
    inits = {timestamp(row["init_time"]) for row in rows}
    if len(inits) != 1:
        raise ValueError("Supply one forecast initialization")
    init = inits.pop()
    tracks = {}
    for row in rows:
        member = row["sample"].strip()
        values = [float(row[c]) if row[c].strip() else None for c in FIELDS]
        if not member or not all(v is not None and math.isfinite(v) for v in values[:4]):
            raise ValueError("Invalid required numeric value")
        lead, lon, lat, wind = values[:4]
        if not (lead >= 0 and -180 <= lon <= 180 and -90 <= lat <= 90 and 0 <= wind <= 250):
            raise ValueError("Required value outside accepted range")
        if timestamp(row["valid_time"]) != init + dt.timedelta(hours=lead):
            raise ValueError("Valid time does not match initialization plus lead time")
        for i, value in enumerate(values[4:], 4):
            if value is not None and (not math.isfinite(value) or value < 0 or (i == 4 and not 800 <= value <= 1100)):
                raise ValueError("Invalid pressure or radius value")
        if any(p[0] == lead for p in tracks.setdefault(member, [])):
            raise ValueError("Duplicate forecast point")
        tracks[member].append(values)
    if set(tracks) != {str(i) for i in range(64)} or any(len(t) < 2 for t in tracks.values()):
        raise ValueError("Expected 64 ensemble tracks with at least two positions each")
    for track in tracks.values():
        track.sort(key=lambda point: point[0])
    now = dt.datetime.now(dt.timezone.utc)
    latest = max(timestamp(row["valid_time"]) for row in rows)
    # The supplied CSV header specifies 48 hours. Respect it conservatively,
    # even though the currently linked terms state a shorter historical window.
    if public and latest > now - dt.timedelta(hours=48):
        raise ValueError("Public embedded-data publishing blocked: CSV includes recent/future data subject to controlled-sharing terms. See README.")
    forecast = {"init": init.isoformat().replace("+00:00", "Z"), "storm": storm,
                "label": "WeatherNext 3 Cyclones", "tracks": tracks}
    source = (ROOT / "assets/app-fragment.html").read_text()
    stamp = now.strftime("%Y-%m-%d %H:%M UTC")
    source = source.replace('<div class="gt-toolbar">',
                            f'<p class="text-small text-muted">Site built: {stamp}</p><div class="gt-toolbar">', 1)
    source = source.replace("/*D3_EMBED*/", (ROOT / "assets/d3.js").read_text())
    source = source.replace("/*COAST*/", (ROOT / "assets/coast.json").read_text())
    source = source.replace("/*FORECAST*/", json.dumps(forecast, separators=(",", ":"), allow_nan=False))
    output.mkdir(parents=True, exist_ok=True)
    html = (ROOT / "assets/page-head.html").read_text() + source + "</main></body></html>"
    (output / "index.html").write_text(html)
    (output / ".nojekyll").touch()
    print(f"Built {output / 'index.html'}: {len(tracks)} members, {len(rows)} positions, initialized {forecast['init']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=ROOT / "data/latest.csv")
    parser.add_argument("--storm", default="AL092026")
    parser.add_argument("--output", type=Path, default=ROOT / "site")
    parser.add_argument("--public", action="store_true", help="Check historical-data eligibility before a public build")
    args = parser.parse_args()
    build(args.csv, args.storm, args.output, args.public)
