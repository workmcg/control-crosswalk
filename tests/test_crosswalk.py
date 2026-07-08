"""
Minimal tests for control-crosswalk.
Run with:  python -m pytest -q
"""

import sys
from pathlib import Path

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
