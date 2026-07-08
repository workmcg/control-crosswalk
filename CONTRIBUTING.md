# Contributing to control-crosswalk

Thank you for your interest in contributing! This project maps security controls across ISO 27001:2022, NIST CSF 2.0, and NIS2 — contributions that improve accuracy, coverage, or usability are very welcome.

---

## Ways to contribute

- **Fix a mapping error** — if a control is mapped incorrectly or to the wrong category, open an issue or submit a PR
- **Add a new framework** — PCI-DSS, SOC 2, CIS Controls are on the roadmap
- **Improve documentation** — clearer README sections, usage examples, or docstrings
- **Report bugs** — unexpected output, edge cases, or CLI errors

---

## Getting started

```bash
git clone https://github.com/workmcg/control-crosswalk
cd control-crosswalk
python3 src/crosswalk.py --help
```

No dependencies to install — this tool is deliberately kept to the Python standard library only.

---

## Submitting a pull request

1. Fork the repo and create a branch: `git checkout -b fix/iso-5.1-mapping`
2. Make your changes
3. Test that the CLI output is correct for the affected frameworks
4. Submit a PR with a clear description of what changed and why

**PR title format:** `fix:`, `feat:`, or `docs:` prefix (e.g. `feat: add DORA framework`)

---

## Reporting issues

Please include:
- Your Python version (`python --version`)
- The command you ran
- The output you expected vs. what you got

---

## Accuracy standard

Control mappings must be traceable to the official source documents:
- ISO/IEC 27001:2022 (Annex A)
- NIST CSF 2.0 (NIST SP 800-53)
- NIS2 Directive 2022/2555
- DORA — Regulation (EU) 2022/2554

If you're adding or modifying a mapping, cite the specific clause or article number in your PR description.

---

## Code style

- Python: follow PEP 8, keep functions small and well-named
- No external dependencies without discussion first (this tool is designed to be dependency-free)

---

Questions? Open an issue or reach out via [LinkedIn](https://www.linkedin.com/in/mukul-chauhan-208/).
