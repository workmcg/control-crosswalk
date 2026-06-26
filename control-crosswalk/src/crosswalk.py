#!/usr/bin/env python3
"""
control-crosswalk: map and analyse security controls across
ISO/IEC 27001:2022, NIST CSF 2.0 and the NIS2 Directive (Art. 21).

A small, dependency-free GRC utility for control mapping, coverage
gap analysis and exporting an audit-ready crosswalk.

Author: Mukul Chauhan
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "crosswalk.json"


# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #
def load_crosswalk(path: Path = DATA_FILE) -> dict:
    """Load the crosswalk JSON from disk."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        sys.exit(f"[error] crosswalk data not found at: {path}")
    except json.JSONDecodeError as exc:
        sys.exit(f"[error] crosswalk data is not valid JSON: {exc}")


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #
def cmd_lookup(args: argparse.Namespace, data: dict) -> None:
    """Show framework equivalents for one ISO 27001 control."""
    query = args.control.strip().upper()
    nis2_text = data["nis2_article21_measures"]
    matches = [c for c in data["controls"] if c["iso_id"].upper() == query]

    if not matches:
        print(f"No control found for '{args.control}'.")
        print("Tip: try an ISO 27001:2022 Annex A id such as A.5.1 or A.8.8.")
        return

    for ctrl in matches:
        print("=" * 60)
        print(f"{ctrl['iso_id']}  {ctrl['iso_name']}")
        print(f"Theme: {ctrl['iso_theme']}")
        print("-" * 60)
        print("NIST CSF 2.0 :", ", ".join(ctrl["nist_csf"]) or "(none)")
        print("NIS2 Art.21  :")
        for ref in ctrl["nis2"]:
            print(f"   {ref}  {nis2_text.get(ref, '')}")
        print("=" * 60)


def cmd_list(args: argparse.Namespace, data: dict) -> None:
    """List all mapped controls, optionally filtered by theme."""
    theme = (args.theme or "").strip().lower()
    rows = data["controls"]
    if theme:
        rows = [c for c in rows if c["iso_theme"].lower() == theme]
        if not rows:
            print(f"No controls found for theme '{args.theme}'.")
            return
    for ctrl in rows:
        print(f"{ctrl['iso_id']:<8} {ctrl['iso_name']:<55} "
              f"[{ctrl['iso_theme']}]")
    print(f"\n{len(rows)} control(s).")


def cmd_gap(args: argparse.Namespace, data: dict) -> None:
    """
    Coverage gap analysis.

    Reads a file of implemented ISO 27001 control ids (one per line)
    and reports coverage against the mapped control set, plus the
    NIST CSF / NIS2 areas left uncovered.
    """
    impl_path = Path(args.implemented)
    if not impl_path.exists():
        sys.exit(f"[error] implemented-controls file not found: {impl_path}")

    implemented = {
        line.strip().upper()
        for line in impl_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }

    all_ids = {c["iso_id"].upper() for c in data["controls"]}
    covered = sorted(implemented & all_ids)
    missing = sorted(all_ids - implemented)
    unknown = sorted(implemented - all_ids)

    pct = (len(covered) / len(all_ids) * 100) if all_ids else 0

    print("Coverage gap analysis")
    print("=" * 60)
    print(f"Mapped controls in scope : {len(all_ids)}")
    print(f"Implemented & in scope   : {len(covered)}")
    print(f"Coverage                 : {pct:.1f}%")
    print("-" * 60)

    if missing:
        print(f"\nNot yet implemented ({len(missing)}):")
        by_id = {c["iso_id"].upper(): c for c in data["controls"]}
        for cid in missing:
            print(f"  {cid:<8} {by_id[cid]['iso_name']}")

    # Which NIS2 measures still have an open ISO gap?
    nis2_text = data["nis2_article21_measures"]
    open_nis2: dict[str, list[str]] = {}
    by_id = {c["iso_id"].upper(): c for c in data["controls"]}
    for cid in missing:
        for ref in by_id[cid]["nis2"]:
            open_nis2.setdefault(ref, []).append(cid)
    if open_nis2:
        print("\nNIS2 Art.21 measures with open ISO gaps:")
        for ref in sorted(open_nis2):
            print(f"  {ref}  {nis2_text.get(ref, '')}")

    if unknown:
        print(f"\nNote: {len(unknown)} listed control(s) not in the "
              f"crosswalk and ignored: {', '.join(unknown)}")


def cmd_export(args: argparse.Namespace, data: dict) -> None:
    """Flatten the crosswalk to a CSV for use in a risk register / audit pack."""
    out_path = Path(args.output)
    nis2_text = data["nis2_article21_measures"]
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            ["ISO 27001:2022", "Control name", "Theme",
             "NIST CSF 2.0", "NIS2 Art.21", "NIS2 measure"]
        )
        for ctrl in data["controls"]:
            writer.writerow([
                ctrl["iso_id"],
                ctrl["iso_name"],
                ctrl["iso_theme"],
                "; ".join(ctrl["nist_csf"]),
                "; ".join(ctrl["nis2"]),
                " | ".join(nis2_text.get(r, "") for r in ctrl["nis2"]),
            ])
    print(f"Exported {len(data['controls'])} controls to {out_path}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crosswalk",
        description="Map and analyse controls across ISO 27001:2022, "
                    "NIST CSF 2.0 and NIS2.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_lookup = sub.add_parser("lookup", help="show framework equivalents "
                                             "for an ISO 27001 control")
    p_lookup.add_argument("control", help="ISO 27001 control id, e.g. A.8.8")
    p_lookup.set_defaults(func=cmd_lookup)

    p_list = sub.add_parser("list", help="list all mapped controls")
    p_list.add_argument("--theme", help="filter by theme "
                                        "(Organizational/People/Physical/Technological)")
    p_list.set_defaults(func=cmd_list)

    p_gap = sub.add_parser("gap", help="coverage gap analysis from a file "
                                       "of implemented controls")
    p_gap.add_argument("implemented", help="path to a text file of "
                                           "implemented ISO control ids")
    p_gap.set_defaults(func=cmd_gap)

    p_export = sub.add_parser("export", help="export the full crosswalk to CSV")
    p_export.add_argument("-o", "--output", default="crosswalk_export.csv",
                          help="output CSV path")
    p_export.set_defaults(func=cmd_export)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    data = load_crosswalk()
    args.func(args, data)


if __name__ == "__main__":
    main()
