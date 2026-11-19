"""Text from someone else's drawing must not break or hijack an export.

CSV cells that a spreadsheet would run as a formula get a leading
apostrophe, and names with markup characters must not stop the PDF
writers (reportlab reads Paragraph text as markup)."""

from __future__ import annotations

import csv
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cwt import bom, export

SYM = {"MD": {"label": "=HYPERLINK(\"http://x\")", "shape": "ellipse",
              "color": "#FFFF00", "is_camera": True}}


def _read(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.reader(f))


@pytest.mark.parametrize("value, expected", [
    ("=1+1", "'=1+1"),
    ("+cmd", "'+cmd"),
    ("@SUM(A1)", "'@SUM(A1)"),
    ("-Lobby", "'-Lobby"),
    ("\tx", "'\tx"),
    # Left alone: numbers, numeric text, dash placeholders, normal text.
    ("-12.5", "-12.5"),
    ("+3", "+3"),
    ("-", "-"),
    ("--", "--"),
    ("MD-1", "MD-1"),
    ("", ""),
    (7, 7),
    (None, None),
])
def test_csv_safe(value, expected):
    assert bom.csv_safe(value) == expected


def test_devices_csv_neutralises_formulas(tmp_path):
    devices = [{"id": "=A1", "type": "MD", "x": "bad", "y": 2}]
    p = str(tmp_path / "devices.csv")
    export.write_devices_csv(devices, SYM, [], lambda v: f"{v} in", p)
    row = _read(p)[1]
    assert row[0] == "'=A1"
    assert row[2].startswith("'=HYPERLINK")
    assert row[3] == "-"       # the "no position" placeholder is untouched
    assert row[7] == "--"


def test_bom_csv_neutralises_formulas(tmp_path):
    cables = {"=X": {"label": "@evil", "color": "#000000", "cost_per_ft": 1.0}}
    routes = [{"device_id": "d", "length_in": 12, "cable_type": "=X",
               "points": [[0, 0], [1, 1]]}]
    rep = bom.rollup(routes, [{"id": "d", "type": "MD"}], SYM, cables)
    p = str(tmp_path / "bom.csv")
    bom.write_csv(rep, p)
    row = _read(p)[1]
    assert row[0] == "'=X"
    assert row[1] == "'@evil"


def test_pdf_writers_accept_markup_characters(tmp_path):
    pytest.importorskip("reportlab")
    rep = bom.rollup([], [], SYM, {})
    name = "Bldg <B & more <b"
    p1 = str(tmp_path / "report.pdf")
    export.write_pdf_report(
        p1, project_name=name, devices=[], symbol_types=SYM, wire_routes=[],
        bom_report=rep, format_length=lambda v: f"{v} in",
        floor_label="1 <i", scale_factor=0.5)
    assert os.path.getsize(p1) > 0
    p2 = str(tmp_path / "map.pdf")
    export.write_map_pdf(
        p2, project_name=name, map_pages=None, devices=[], symbol_types=SYM,
        wire_routes=[], bom_report=rep, model_lines=None,
        include_summary=True, floor_label="1 <i", currency="<$")
    assert os.path.getsize(p2) > 0
