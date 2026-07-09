# control-crosswalk

A small GRC utility that maps the complete ISO/IEC 27001:2022 Annex A (all 93 controls) across five frameworks:

- **ISO/IEC 27001:2022** (Annex A controls)
- **NIST Cybersecurity Framework 2.0** (Functions / Categories)
- **NIS2 Directive** — EU 2022/2555, Article 21(2) cyber risk-management measures
- **DORA** — EU 2022/2554 (Digital Operational Resilience Act), Articles 5-30
- **SOC 2** — AICPA Trust Services Criteria (Security, Availability, Confidentiality, Processing Integrity, Privacy)

It does five things GRC teams actually need: look up how a control maps across frameworks, **search** the crosswalk by keyword, **reverse-lookup** from a NIST/NIS2/DORA/SOC2 reference back to the ISO controls that satisfy it, run a coverage **gap analysis** against your implemented controls, check aggregate **stats** on framework coverage, and **export** an audit-ready crosswalk to CSV, JSON, or XLSX.

> Why this exists: enterprises increasingly run a single ISMS that has to answer to ISO 27001 certification, NIST-aligned internal standards, EU NIS2/DORA obligations, and a customer-facing SOC 2 report at the same time. Maintaining that mapping by hand in spreadsheets is slow and error-prone. This tool keeps the crosswalk in version control as structured data and makes it queryable.

---

## Quick start

Core commands (`lookup`, `list`, `search`, `gap`, `stats`, `reverse`, and CSV/JSON export) need nothing beyond the Python standard library (Python 3.9+). XLSX export needs the optional `openpyxl` package (see below).

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
SOC 2 TSC    :
   CC7  System Operations — detecting, monitoring and responding to
        security events, incidents and vulnerabilities
   CC3  Risk Assessment — identification and analysis of risks to
        objectives, including fraud risk and risk from change
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

Searches control names, themes, and every mapped framework reference (NIST, NIS2, DORA, SOC2) for a keyword and prints the matching controls with their full cross-framework mapping.

### Reverse lookup

Going the other direction — "which ISO controls satisfy this NIST/NIS2/DORA/SOC2 requirement?" — is often what an auditor or a framework-first team actually needs:

```bash
python3 src/crosswalk.py reverse soc2 CC6
python3 src/crosswalk.py reverse dora Art.9
python3 src/crosswalk.py reverse nis2 21.2.e
python3 src/crosswalk.py reverse nist GV.PO-01
```

```
SOC2 CC6  —  Logical and Physical Access Controls — restricting logical
             and physical access to systems, data and facilities to authorized users
============================================================
  A.5.9    Inventory of information and other associated assets [Organizational]
  A.5.10   Acceptable use of information and other associated assets [Organizational]
  ...
  A.8.24   Use of cryptography                          [Technological]

33 ISO 27001:2022 control(s) map to SOC2 CC6.
```

The reference lookup is case-insensitive, and an unmatched reference prints every known reference code for that framework so you can find the right one.

### Run a coverage gap analysis

Create a text file of the ISO controls you have implemented (one id per line; `#` lines are ignored), then:

```bash
python3 src/crosswalk.py gap examples/implemented_controls.txt
```

The tool reports your coverage %, which controls are not yet implemented, and — usefully for compliance scoping — **which NIS2 Article 21 measures, DORA articles, and SOC 2 Trust Services Criteria still have an open ISO gap**.

### Check framework coverage stats

```bash
python3 src/crosswalk.py stats
```

Prints aggregate coverage numbers: how many controls have a NIST, NIS2, DORA, and SOC2 mapping, and how many distinct articles/measures/criteria are referenced across the crosswalk.

### Export the crosswalk

```bash
python3 src/crosswalk.py export -o crosswalk_export.csv
python3 src/crosswalk.py export -o crosswalk_export.json --format json
python3 src/crosswalk.py export -o crosswalk_export.xlsx --format xlsx
```

CSV and JSON have no extra dependencies and include DORA and SOC2 references alongside NIST and NIS2. The XLSX export additionally colour-codes every row by ISO theme (Organizational / People / Physical / Technological), freezes the header row, and adds an autofilter — ready to drop into a risk register or audit evidence pack as-is. It requires the optional `openpyxl` package:

```bash
pip install openpyxl
```

If `openpyxl` isn't installed, `--format xlsx` prints a clear error telling you to install it rather than failing silently.

---

## How it's structured

```
control-crosswalk/
├── data/
│   └── crosswalk.json      # the mapping data (edit this to extend)
├── src/
│   └── crosswalk.py        # CLI: lookup / list / search / reverse / gap / stats / export
├── examples/
│   ├── implemented_controls.txt
│   └── crosswalk_export.csv
└── tests/
    └── test_crosswalk.py   # data-integrity + CLI-behaviour tests
```

The mapping lives in `data/crosswalk.json` as structured data, separate from the code — so extending the crosswalk is a data edit, not a code change.

## Tests

```bash
pip install pytest openpyxl   # openpyxl only needed for the xlsx export tests
python -m pytest tests/ -v
```

18 tests covering: data integrity (required fields present, themes valid, no duplicate control ids, every NIS2/DORA/SOC2 reference resolves to a defined measure/article/criterion, NIST CSF codes are well-formed, the full 93-control Annex A theme distribution is intact), DORA and SOC2 mapping coverage staying above 90% with documented exceptions, reverse-lookup behaviour (including case-insensitivity and "no match" handling), and CSV/JSON/XLSX export correctness (the XLSX test is skipped automatically if `openpyxl` isn't installed).

---

## Scope and honesty about mappings

This crosswalk covers **all 93 ISO/IEC 27001:2022 Annex A controls** (37 Organizational, 8 People, 14 Physical, 34 Technological) — not a curated subset. That said, framework crosswalks are inherently interpretive: controls differ in scope and intent, and a one-to-one mapping is often an approximation rather than a precise equivalence.

NIST CSF 2.0 coverage is complete (every control maps to at least one subcategory, since CSF's outcomes are broad enough to touch almost any security practice). NIS2 and DORA coverage is intentionally *not* forced to 100%: a small number of controls (intellectual property rights, PII privacy, confidentiality/NDA agreements) are legal or privacy concerns that sit outside what either regulation actually governs, and mapping them anyway would be a stretch that undermines the crosswalk's credibility.

SOC 2 is the interesting exception to that pattern: because the AICPA Trust Services Criteria include dedicated **Confidentiality (C1)** and **Privacy (P1-P8)** categories, SOC 2 actually *does* cover the confidentiality/NDA (A.6.6) and PII privacy (A.5.34) controls that NIS2 and DORA legitimately exclude — so SOC2 coverage (98.9%) comes out even higher than DORA's. The one control that remains genuinely unmapped across *all three* frameworks is **A.5.32 (Intellectual property rights)** — none of NIST CSF's security outcomes, NIS2's cyber risk-management measures, DORA's ICT resilience articles, or SOC 2's trust criteria actually govern IP ownership, and mapping it anyway would be dishonest padding. SOC2 mapping is done at the **Trust Services Category level** (e.g. `CC6`, `A1`, `P3`) rather than the individual point-of-focus level (e.g. `CC6.1`) — a level of granularity comparable to NIS2's measure-level and DORA's article-level mappings, and one we can stand behind without over-claiming precision.

Run `python3 src/crosswalk.py stats` to see current coverage numbers.

**Always validate mappings against the source standards before relying on them for audit or certification evidence.** Contributions that correct or refine a mapping (with the specific clause/article/criterion cited) are welcome.

## Roadmap

**Shipped**
- [x] DORA (EU 2022/2554) framework mapping
- [x] Full ISO/IEC 27001:2022 Annex A coverage (all 93 controls)
- [x] SOC 2 Trust Services Criteria as a fifth framework
- [x] Reverse lookup (NIST CSF / NIS2 / DORA / SOC2 → ISO)
- [x] XLSX export with theme-based conditional formatting

**Up next**
- [ ] PCI DSS or CIS Controls as a sixth framework
- [ ] Point-of-focus-level SOC 2 mapping (CC6.1, CC6.2, ... ) for teams that need finer granularity than the category level

## License

MIT — see [LICENSE](LICENSE).

---

*Built by [Mukul Chauhan](https://www.linkedin.com/in/mukul-chauhan-208/) — GRC & information security risk. Framework references: ISO/IEC 27001:2022, NIST CSF 2.0, Directive (EU) 2022/2555 (NIS2), Regulation (EU) 2022/2554 (DORA), AICPA SOC 2 Trust Services Criteria.*
