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


def test_iso_ids_are_unique():
    data = crosswalk.load_crosswalk()
    ids = [c["iso_id"] for c in data["controls"]]
    assert len(ids) == len(set(ids)), "duplicate ISO control ids found"
