"""Regression tests for varying cyclone ensemble sizes and model metadata."""
import csv
import datetime as dt
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build as builder


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        assets = self.root / "assets"
        assets.mkdir()
        (assets / "app-fragment.html").write_text('<div class="gt-toolbar"></div>/*FORECAST*//*COAST*//*D3_EMBED*/')
        (assets / "coast.json").write_text("{}")
        (assets / "d3.js").write_text("/*test*/")
        (assets / "page-head.html").write_text("<html><main>")
        root_override = patch.object(builder, "ROOT", self.root)
        root_override.start()
        self.addCleanup(root_override.stop)

    def make_csv(self, members):
        csv_path = self.root / "latest.csv"
        init = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
        fieldnames = ["init_time", "track_id", "sample", "valid_time"] + builder.FIELDS
        with csv_path.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for member in range(members):
                for lead in (0, 6):
                    row = {field: "0" for field in builder.FIELDS}
                    row.update({
                        "init_time": init.isoformat(), "valid_time": (init + dt.timedelta(hours=lead)).isoformat(),
                        "track_id": "AL092026", "sample": str(member),
                        "lead_time_hours": str(lead), "lon": "-86", "lat": "30",
                        "maximum_sustained_wind_speed_knots": "55",
                        "minimum_sea_level_pressure_hpa": "990",
                    })
                    writer.writerow(row)
        return csv_path

    def test_50_member_model(self):
        path = self.make_csv(50)
        builder.build(path, "AL092026", self.root / "site", False, "FNV3P2")
        html = (self.root / "site/index.html").read_text()
        self.assertIn("WeatherNext 2 Cyclones (r2, FNV3P2)", html)
        self.assertIn('"model":"FNV3P2"', html)

    def test_64_member_model(self):
        path = self.make_csv(64)
        builder.build(path, "AL092026", self.root / "site", False, "WNV3")
        html = (self.root / "site/index.html").read_text()
        self.assertIn("WeatherNext 3 Cyclones (WNV3)", html)
        self.assertIn('"63":', html)

    def test_non_contiguous_member_ids_fail(self):
        path = self.make_csv(50)
        text = path.read_text()
        path.write_text(text.replace(",49,", ",99,"))
        with self.assertRaisesRegex(ValueError, "sequentially numbered"):
            builder.build(path, "AL092026", self.root / "site", False, "FNV3P2")


if __name__ == "__main__":
    unittest.main()
