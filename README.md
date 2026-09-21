# dqcheck

**A fast, friendly command-line tool for profiling datasets and enforcing practical data-quality rules.**

`dqcheck` helps analysts, analytics engineers, data engineers and developers catch common data problems before they reach dashboards, models or production pipelines.

> Status: early alpha. The project is intentionally small, useful and contributor-friendly.

## Why dqcheck?

Many data-quality tools are powerful but heavy. `dqcheck` aims to make the first 80% of checks easy:

- Profile CSV, Excel, JSON and Parquet files
- Find missing values and duplicate rows
- Measure column cardinality
- Flag numeric outliers using the IQR method
- Enforce rules from a human-readable YAML file
- Return a non-zero exit code when checks fail, making it CI-friendly
- Export Markdown or JSON reports

## Quick start

```bash
python -m pip install dqcheck

dqcheck profile data.csv
```

From source:

```bash
git clone https://github.com/aaronpius/data-quality-cli.git
cd data-quality-cli
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"

dqcheck profile examples/customers.csv
```

## Run quality rules

Create a YAML rules file:

```yaml
dataset:
  max_duplicate_percent: 0

columns:
  id:
    max_null_percent: 0
    unique: true
  status:
    allowed_values: [active, inactive]
  amount:
    min: 0
```

Then run:

```bash
dqcheck check data.csv --rules rules.yaml
```

A failed rule exits with status code `1`, so you can use it in GitHub Actions, pre-commit hooks and data pipelines.

## Reports

```bash
dqcheck profile examples/customers.csv --output report.md
dqcheck check examples/customers.csv --rules examples/rules.yaml --output report.json --format json
```

## Commands

```text
dqcheck profile FILE
dqcheck check FILE --rules RULES.yaml
dqcheck sample-rules
dqcheck version
```

## Supported sources

| Format | Support |
|---|---|
| CSV | Yes |
| Excel `.xlsx` / `.xlsm` | Yes |
| JSON | Yes |
| Parquet | Optional: `pip install 'dqcheck[parquet]'` |
| SQL databases | Planned |
| Snowflake | Planned |

## Roadmap

The project is deliberately being built in small, useful releases.

- [x] File profiling
- [x] YAML quality rules
- [x] Markdown and JSON reports
- [x] CI-compatible exit codes
- [ ] Regex and pattern checks
- [ ] Date freshness checks
- [ ] Referential integrity across files
- [ ] PostgreSQL support
- [ ] Snowflake support
- [ ] HTML reports
- [ ] Plugin API for custom rules

See open GitHub issues for work that is ready for contributors.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
```

## Contributing

Contributions are welcome. Good first contributions include new rule types, source connectors, tests, documentation and sample datasets.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Security

Please do not post sensitive datasets or credentials in public issues. See [SECURITY.md](SECURITY.md) for reporting guidance.

## License

MIT. See [LICENSE](LICENSE).
