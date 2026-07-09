"""
Tests for control-crosswalk.
Run with:  python -m pytest -q
"""

import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import crosswalk  # noqa: E402


def test_data_loads_and_is_consistent():
    data = crosswalk.load_crosswalk()
    assert "controls" in data
    assert len(data["controls"]) > 0


def test_every_control_has_required_fields():
    data = crosswalk.load_crosswalk()
    for ctrl in data["controls"]:
        assert ctrl["iso_id"]
        assert ctrl["iso_name"]
        assert ctrl["iso_theme"] in {
            "Organizational", "People", "Physical", "Technological"
        }
        assert isinstance(ctrl["nist_csf"], list)
        assert isinstance(ctrl["nis2"], list)
        assert isinstance(ctrl.get("soc2", []), list)


def test_every_nis2_reference_is_defined():
    data = crosswalk.load_crosswalk()
    valid = set(data["nis2_article21_measures"].keys())
    for ctrl in data["controls"]:
        for ref in ctrl["nis2"]:
            assert ref in valid, f"{ctrl['iso_id']} references unknown {ref}"


def test_every_dora_reference_is_defined():
    data = crosswalk.load_crosswalk()
    valid = set(data["dora_articles"].keys())
    for ctrl in data["controls"]:
        for ref in ctrl.get("dora", []):
            assert ref in valid, f"{ctrl['iso_id']} references unknown DORA {ref}"


def test_every_soc2_reference_is_defined():
    data = crosswalk.load_crosswalk()
    valid = set(data["soc2_trust_services_criteria"].keys())
    for ctrl in data["controls"]:
        for ref in ctrl.get("soc2", []):
            assert ref in valid, f"{ctrl['iso_id']} references unknown SOC2 {ref}"


def test_dora_mapping_coverage_is_high():
    # DORA is an ICT operational resilience regulation, not a general-purpose
    # security standard -- a small number of Annex A controls genuinely sit
    # outside its scope (e.g. intellectual property rights, PII privacy,
    # confidentiality agreements are legal/privacy concerns DORA doesn't
    # regulate). Rather than force a mapping onto every control, this test
    # asserts the overwhelming majority have a genuine DORA touchpoint, and
    # documents which ones don't.
    data = crosswalk.load_crosswalk()
    total = len(data["controls"])
    unmapped = [c["iso_id"] for c in data["controls"] if not c.get("dora")]
    coverage = (total - len(unmapped)) / total
    assert coverage >= 0.9, (
        f"DORA coverage dropped to {coverage:.1%}; unmapped: {unmapped}"
    )


def test_soc2_mapping_coverage_is_high():
    # Unlike NIS2/DORA, SOC 2's Confidentiality (C1) and Privacy (P1-P8)
    # categories actually do cover PII privacy and NDA/confidentiality
    # controls -- so SOC2 coverage should be even higher than DORA's. Only
    # intellectual property rights (A.5.32) genuinely sits outside all three
    # regulatory/framework scopes.
    data = crosswalk.load_crosswalk()
    total = len(data["controls"])
    unmapped = [c["iso_id"] for c in data["controls"] if not c.get("soc2")]
    coverage = (total - len(unmapped)) / total
    assert coverage >= 0.9, (
        f"SOC2 coverage dropped to {coverage:.1%}; unmapped: {unmapped}"
    )
    assert "A.5.32" in unmapped, (
        "A.5.32 (Intellectual property rights) is the documented SOC2 "
        "scope exception; if this changed, update the README's honesty section too"
    )


def test_all_defined_soc2_criteria_are_actually_used():
    # Sanity check: every SOC2 code we define in the reference dict should
    # be referenced by at least one control, otherwise it's dead data.
    data = crosswalk.load_crosswalk()
    defined = set(data["soc2_trust_services_criteria"].keys())
    used = {ref for c in data["controls"] for ref in c.get("soc2", [])}
    assert defined == used, f"defined-but-unused: {defined - used}; used-but-undefined: {used - defined}"


def test_nist_csf_codes_are_well_formed():
    import re
    pattern = re.compile(r"^(GV|ID|PR|DE|RS|RC)\.[A-Z]{2}-\d{2}$")
    data = crosswalk.load_crosswalk()
    for ctrl in data["controls"]:
        assert ctrl["nist_csf"], f"{ctrl['iso_id']} has no NIST CSF mapping"
        for code in ctrl["nist_csf"]:
            assert pattern.match(code), f"{ctrl['iso_id']} has malformed NIST code {code}"


def test_full_annex_a_coverage():
    # This crosswalk is meant to cover the complete ISO/IEC 27001:2022 Annex A
    # (93 controls across 4 themes), not a curated subset.
    data = crosswalk.load_crosswalk()
    from collections import Counter
    themes = Counter(c["iso_theme"] for c in data["controls"])
    assert themes["Organizational"] == 37
    assert themes["People"] == 8
    assert themes["Physical"] == 14
    assert themes["Technological"] == 34
    assert len(data["controls"]) == 93


def test_iso_ids_are_unique():
    data = crosswalk.load_crosswalk()
    ids = [c["iso_id"] for c in data["controls"]]
    assert len(ids) == len(set(ids)), "duplicate ISO control ids found"


# --------------------------------------------------------------------------- #
# Reverse lookup
# --------------------------------------------------------------------------- #

def test_reverse_lookup_soc2_finds_known_controls(capsys):
    data = crosswalk.load_crosswalk()
    import argparse
    args = argparse.Namespace(framework="soc2", reference="C1")
    crosswalk.cmd_reverse(args, data)
    out = capsys.readouterr().out
    assert "A.6.6" in out  # Confidentiality / NDA control must map to C1
    assert "SOC2 C1" in out


def test_reverse_lookup_is_case_insensitive(capsys):
    data = crosswalk.load_crosswalk()
    import argparse
    args = argparse.Namespace(framework="dora", reference="art.9")
    crosswalk.cmd_reverse(args, data)
    out = capsys.readouterr().out
    assert "No ISO 27001 controls map" not in out
    assert "Art.9" in out


def test_reverse_lookup_unknown_reference_reports_no_matches(capsys):
    data = crosswalk.load_crosswalk()
    import argparse
    args = argparse.Namespace(framework="soc2", reference="NOTAREALCODE")
    crosswalk.cmd_reverse(args, data)
    out = capsys.readouterr().out
    assert "No ISO 27001 controls map" in out
    assert "Known SOC2 references" in out


def test_reverse_lookup_nist_finds_known_controls(capsys):
    data = crosswalk.load_crosswalk()
    import argparse
    args = argparse.Namespace(framework="nist", reference="GV.PO-01")
    crosswalk.cmd_reverse(args, data)
    out = capsys.readouterr().out
    assert "A.5.1" in out


# --------------------------------------------------------------------------- #
# Export
# --------------------------------------------------------------------------- #

def test_export_csv_includes_soc2_column(tmp_path):
    data = crosswalk.load_crosswalk()
    import argparse
    out_file = tmp_path / "export.csv"
    args = argparse.Namespace(output=str(out_file), format="csv")
    crosswalk.cmd_export(args, data)
    with open(out_file, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    assert "SOC 2 TSC" in rows[0]
    assert len(rows) == len(data["controls"]) + 1  # header + one row per control


def test_export_json_includes_soc2_refs(tmp_path):
    data = crosswalk.load_crosswalk()
    import argparse
    out_file = tmp_path / "export.json"
    args = argparse.Namespace(output=str(out_file), format="json")
    crosswalk.cmd_export(args, data)
    exported = json.loads(out_file.read_text(encoding="utf-8"))
    assert exported["total"] == len(data["controls"])
    assert "soc2_refs" in exported["controls"][0]
    assert "soc2_criteria" in exported["controls"][0]


def test_export_xlsx_creates_colour_coded_workbook(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    data = crosswalk.load_crosswalk()
    import argparse
    out_file = tmp_path / "export.xlsx"
    args = argparse.Namespace(output=str(out_file), format="xlsx")
    crosswalk.cmd_export(args, data)
    assert out_file.exists()

    wb = openpyxl.load_workbook(out_file)
    ws = wb.active
    assert ws.max_row == len(data["controls"]) + 1  # header + rows
    header = [c.value for c in ws[1]]
    assert "SOC 2 TSC" in header
    # First data row should be colour-filled according to its theme
    first_theme = data["controls"][0]["iso_theme"]
    expected_colour = crosswalk.THEME_COLOURS[first_theme]
    actual_fill = ws.cell(row=2, column=1).fill.fgColor.rgb
    assert actual_fill.endswith(expected_colour)
    assert ws.freeze_panes == "A2"
