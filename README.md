# control-crosswalk

A small, dependency-free GRC utility that maps the complete ISO/IEC 27001:2022 Annex A (all 93 controls) across four frameworks:

- **ISO/IEC 27001:2022** (Annex A controls)
- **NIST Cybersecurity Framework 2.0** (Functions / Categories)
- **NIS2 Directive** — EU 2022/2555, Article 21(2) cyber risk-management measures
- **DORA** — EU 2022/2554 (Digital Operational Resilience Act), Articles 5-30

It does four things GRC teams actually need: look up how a control maps across frameworks, **search** the crosswalk by keyword, run a coverage **gap analysis** against your implemented controls, check aggregate **stats** on framework coverage, and **export** an audit-ready crosswalk to CSV or JSON.

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
DORA         :
   Art.9  Protection and prevention
============================================================
```

### List the mapped controls

```bash
python3 src/crosswalk.py list
python3 src/crosswalk.py list --theme Technological
```

### Search the crosswalk

```bash
python3 src/crosswalk.py search "backup"
```

Searches control names, themes, and every mapped framework reference (NIST, NIS2, DORA) for a keyword and prints the matching controls with their full cross-framework mapping.

### Run a coverage gap analysis

Create a text file of the ISO controls you have implemented (one id per line; `#` lines are ignored), then:

```bash
python3 src/crosswalk.py gap examples/implemented_controls.txt
```

The tool reports your coverage %, which controls are not yet implemented, and — usefully for EU scoping — **which NIS2 Article 21 measures and DORA articles still have an open ISO gap**.

### Check framework coverage stats

```bash
python3 src/crosswalk.py stats
```

Prints aggregate coverage numbers: how many controls have a NIST, NIS2, and DORA mapping, and how many distinct articles/measures are referenced across the crosswalk.

### Export the crosswalk

```bash
python3 src/crosswalk.py export -o crosswalk_export.csv
python3 src/crosswalk.py export -o crosswalk_export.json --format json
```

Produces a flat CSV (default) or structured JSON export you can drop into a risk register, control matrix, or audit evidence pack. Both formats include DORA article references alongside NIST and NIS2.

---

## How it's structured

```
control-crosswalk/
├── data/
│   └── crosswalk.json      # the mapping data (edit this to extend)
├── src/
│   └── crosswalk.py        # CLI: lookup / list / search / gap / stats / export
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

The tests validate data integrity: required fields present, themes valid, no duplicate control ids, every NIS2/DORA reference resolves to a defined measure/article, NIST CSF codes are well-formed, DORA mapping coverage stays above 90% (a handful of controls -- IP rights, PII privacy, NDAs -- genuinely sit outside DORA's ICT-risk scope and are documented exceptions, not gaps), and the full 93-control Annex A theme distribution (37/8/14/34) is intact.

---

## Scope and honesty about mappings

This crosswalk covers **all 93 ISO/IEC 27001:2022 Annex A controls** (37 Organizational, 8 People, 14 Physical, 34 Technological) — not a curated subset. That said, framework crosswalks are inherently interpretive: controls differ in scope and intent, and a one-to-one mapping is often an approximation rather than a precise equivalence.

NIST CSF 2.0 coverage is complete (every control maps to at least one subcategory, since CSF's outcomes are broad enough to touch almost any security practice). NIS2 and DORA coverage is intentionally *not* forced to 100%: a small number of controls (intellectual property rights, PII privacy, confidentiality/NDA agreements) are legal or privacy concerns that sit outside what either regulation actually governs, and mapping them anyway would be a stretch that undermines the crosswalk's credibility. Run `python3 src/crosswalk.py stats` to see current coverage numbers.

**Always validate mappings against the source standards before relying on them for audit or certification evidence.** Contributions that correct or refine a mapping (with the specific clause/article cited) are welcome.

## Roadmap

**Shipped**
- [x] DORA (EU 2022/2554) framework mapping
- [x] Full ISO/IEC 27001:2022 Annex A coverage (all 93 controls)

**Up next**
- [ ] Add SOC 2 Trust Services Criteria as a fifth framework
- [ ] Optional Excel export with conditional formatting
- [ ] Reverse lookup (NIST CSF / NIS2 / DORA → ISO)

## License

MIT — see [LICENSE](LICENSE).

---

*Built by [Mukul Chauhan](https://www.linkedin.com/in/mukul-chauhan-208/) — GRC & information security risk. Framework references: ISO/IEC 27001:2022, NIST CSF 2.0, Directive (EU) 2022/2555 (NIS2), Regulation (EU) 2022/2554 (DORA).*
