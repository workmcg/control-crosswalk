# control-crosswalk

A small, dependency-free GRC utility that maps and analyses security controls across three frameworks:

- **ISO/IEC 27001:2022** (Annex A controls)
- **NIST Cybersecurity Framework 2.0** (Functions / Categories)
- **NIS2 Directive** — EU 2022/2555, Article 21(2) cyber risk-management measures

It does three things GRC teams actually need: look up how a control maps across frameworks, run a coverage **gap analysis** against your implemented controls, and **export** an audit-ready crosswalk to CSV.

> Why this exists: enterprises increasingly run a single ISMS that has to answer to ISO 27001 certification, NIST-aligned internal standards, and EU NIS2 obligations at the same time. Maintaining that mapping by hand in spreadsheets is slow and error-prone. This tool keeps the crosswalk in version control as structured data and makes it queryable.

---

## Quick start

No dependencies beyond the Python standard library (Python 3.9+).

```bash
git clone https://github.com/workmcg/control-crosswalk.git
cd control-crosswalk
```

### Look up a control

```bash
python3 src/crosswalk.py lookup A.8.8
```

```
============================================================
A.8.8  Management of technical vulnerabilities
Theme: Technological
------------------------------------------------------------
NIST CSF 2.0 : ID.RA-01, ID.RA-06
NIS2 Art.21  :
   21.2.e  Security in network and information systems acquisition,
           development and maintenance, including vulnerability handling
============================================================
```

### List the mapped controls

```bash
python3 src/crosswalk.py list
python3 src/crosswalk.py list --theme Technological
```

### Run a coverage gap analysis

Create a text file of the ISO controls you have implemented (one id per line; `#` lines are ignored), then:

```bash
python3 src/crosswalk.py gap examples/implemented_controls.txt
```

The tool reports your coverage %, which controls are not yet implemented, and — usefully for EU scoping — **which NIS2 Article 21 measures still have an open ISO gap**.

### Export the crosswalk

```bash
python3 src/crosswalk.py export -o crosswalk_export.csv
```

Produces a flat CSV you can drop into a risk register, control matrix, or audit evidence pack.

---

## How it's structured

```
control-crosswalk/
├── data/
│   └── crosswalk.json      # the mapping data (edit this to extend)
├── src/
│   └── crosswalk.py        # CLI: lookup / list / gap / export
├── examples/
│   ├── implemented_controls.txt
│   └── crosswalk_export.csv
└── tests/
    └── test_crosswalk.py   # data-integrity tests
```

The mapping lives in `data/crosswalk.json` as structured data, separate from the code — so extending the crosswalk is a data edit, not a code change.

## Tests

```bash
python -m pytest -q
```

The tests validate data integrity: required fields present, themes valid, no duplicate control ids, and every NIS2 reference resolves to a defined measure.

---

## Scope and honesty about mappings

This is a **curated starter crosswalk** covering a representative subset of ISO 27001:2022 Annex A controls — not an exhaustive or authoritative mapping. Framework crosswalks are inherently interpretive: controls differ in scope and intent, and a one-to-one mapping is often an approximation.

**Always validate mappings against the source standards before relying on them for audit or certification evidence.** Contributions that extend or correct the crosswalk are welcome.

## Roadmap

- [ ] Extend coverage to the full 93 Annex A controls
- [ ] Add SOC 2 Trust Services Criteria as a fourth framework
- [ ] Optional Excel export with conditional formatting
- [ ] Reverse lookup (NIST CSF / NIS2 → ISO)

## License

MIT — see [LICENSE](LICENSE).

---

*Built by [Mukul Chauhan](https://www.linkedin.com/in/mukul-chauhan-208/) — GRC & information security risk. Framework references: ISO/IEC 27001:2022, NIST CSF 2.0, Directive (EU) 2022/2555 (NIS2).*
