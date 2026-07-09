# Contributing to control-crosswalk

Thank you for your interest in contributing! This project maps security controls across ISO 27001:2022, NIST CSF 2.0, NIS2, DORA, and SOC 2 — contributions that improve accuracy, coverage, or usability are very welcome.

---

## Ways to contribute

- **Fix a mapping error** — if a control is mapped incorrectly or to the wrong category, open an issue or submit a PR
- **Add a new framework** — PCI DSS and CIS Controls are on the roadmap
- **Refine SOC 2 granularity** — current SOC2 mapping is at the Trust Services Category level (e.g. `CC6`); point-of-focus-level mapping (e.g. `CC6.1`, `CC6.2`) is a welcome but more involved contribution
- **Improve documentation** — clearer README sections, usage examples, or docstrings
- **Report bugs** — unexpected output, edge cases, or CLI errors

---

## Getting started

```bash
git clone https://github.com/workmcg/control-crosswalk
cd control-crosswalk
python3 src/crosswalk.py --help
```

Core commands need no dependencies beyond the Python standard library. XLSX export uses the optional `openpyxl` package — install it with `pip install openpyxl` if you're working on that code path or its tests.

---

## Submitting a pull request

1. Fork the repo and create a branch: `git checkout -b fix/iso-5.1-mapping`
2. Make your changes
3. Run the test suite: `python -m pytest tests/ -v`
4. Test that the CLI output is correct for the affected frameworks (`lookup`, `reverse`, `stats` are good sanity checks after any mapping change)
5. Submit a PR with a clear description of what changed and why

**PR title format:** `fix:`, `feat:`, or `docs:` prefix (e.g. `feat: add PCI DSS framework`)

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
- NIST CSF 2.0
- NIS2 Directive 2022/2555
- DORA — Regulation (EU) 2022/2554
- AICPA SOC 2 Trust Services Criteria (2017, as revised)

If you're adding or modifying a mapping, cite the specific clause/article/criterion number in your PR description. If a control genuinely doesn't map to a framework (see the README's "Scope and honesty about mappings" section), leaving it unmapped is preferred over a forced, low-confidence mapping.

---

## Code style

- Python: follow PEP 8, keep functions small and well-named
- Core CLI must stay dependency-free; any new feature that needs an external package (like `openpyxl` for XLSX export) must degrade gracefully with a clear install message when the package is missing, not a stack trace
- Add or update tests in `tests/test_crosswalk.py` for any behavioural change

---

Questions? Open an issue or reach out via [LinkedIn](https://www.linkedin.com/in/mukul-chauhan-208/).
