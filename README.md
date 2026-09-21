# dqcheck

[![CI](https://github.com/aaronpius/data-quality-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/aaronpius/data-quality-cli/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](pyproject.toml)

**A fast, friendly command-line tool for profiling datasets and enforcing practical data-quality rules.**

`dqcheck` helps analysts, analytics engineers and data engineers catch common data problems before they reach dashboards, models or production pipelines.

> Status: **v0.1.0 alpha**. The core file-based workflow is usable today, and the project is actively growing.

## Why dqcheck?

Many data-quality tools are powerful but heavy. `dqcheck` focuses on a simple workflow that is easy to understand, automate and extend:

- Profile CSV, Excel, JSON and Parquet files
- Find missing values and duplicate rows
- Measure column cardinality
- Flag numeric outliers using the IQR method
- Enforce rules from human-readable YAML
- Return non-zero exit codes when checks fail
- Export Markdown or JSON reports
- Run cleanly in CI pipelines

## Terminal demo

The repository includes a deliberately imperfect sample dataset so you can see both profiling and rule failures immediately.

### 1. Install from source

```console
$ git clone https://github.com/aaronpius/data-quality-cli.git
$ cd data-quality-cli
$ python -m venv .venv
$ source .venv/bin/activate
$ python -m pip install -e ".[dev]"
```

### 2. Profile a dataset

```console
$ dqcheck profile examples/customers.csv

Rows: 5  Columns: 6  Duplicate rows: 1 (20.00%)

                 Column profile
┏━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┓
┃ Column ┃ Type    ┃ Null % ┃ Unique ┃ Outliers ┃
┡━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━┩
│ id     │ int64   │   0.00 │      4 │        0 │
│ name   │ object  │   0.00 │      4 │          │
│ email  │ object  │  20.00 │      3 │          │
│ status │ object  │   0.00 │      2 │          │
│ age    │ int64   │   0.00 │      4 │        0 │
│ spend  │ float64 │   0.00 │      4 │        0 │
└────────┴─────────┴────────┴────────┴──────────┘
```

### 3. Enforce YAML quality rules

```console
$ dqcheck check examples/customers.csv --rules examples/rules.yaml

FAIL max_duplicate_percent: Duplicate rows: 20.00% (limit 10.00%)
PASS min_rows: Rows: 5 (minimum 1)
PASS max_null_percent (id): Nulls: 0.00% (limit 0.00%)
FAIL unique (id): Duplicate non-null values: 1
FAIL max_null_percent (email): Nulls: 20.00% (limit 5.00%)
PASS allowed_values (status): Invalid values: 0
PASS min (age): Minimum: 29 (required >= 0)
FAIL max (age): Maximum: 200 (required <= 120)
PASS min (spend): Minimum: 0.0 (required >= 0)
```

Because checks failed, `dqcheck` exits with status code `1`. That makes the same rules useful locally and in GitHub Actions or other CI/CD systems.

## Define your own rules

```yaml
dataset:
  min_rows: 1
  max_duplicate_percent: 0

columns:
  id:
    max_null_percent: 0
    unique: true

  status:
    allowed_values:
      - active
      - inactive

  amount:
    min: 0
```

Run them with:

```bash
dqcheck check data.csv --rules rules.yaml
```

## Reports

Write profiling or check results to files:

```bash
dqcheck profile examples/customers.csv --output report.md

dqcheck check examples/customers.csv \
  --rules examples/rules.yaml \
  --output report.json \
  --format json
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
| CSV | ✅ |
| Excel `.xlsx` / `.xlsm` | ✅ |
| JSON | ✅ |
| Parquet | ✅ Optional dependency |
| PostgreSQL | 🚧 Planned |
| Snowflake | 🚧 Planned |

For Parquet support:

```bash
python -m pip install -e ".[parquet]"
```

## CI and development quality

Every push and pull request is automatically tested on:

- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13
- Ruff linting
- Pytest test suite with coverage

The current `main` branch is expected to stay green.

## Roadmap

Contributor-ready roadmap work is tracked as GitHub issues. Planned areas include:

- Regex and pattern validation
- Date freshness and staleness checks
- Cross-file referential integrity
- PostgreSQL support
- Snowflake support
- HTML reporting
- A plugin interface for custom checks

If you want to contribute, pick an open issue with clear acceptance criteria and comment before starting larger changes.

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
```

Or:

```bash
make check
```

## Contributing

Contributions are welcome from first-time and experienced open-source contributors.

Good contributions include:

- New rule types
- New data-source connectors
- Tests for edge cases
- Documentation and examples
- Reporting improvements

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Project principles

- **Simple first:** useful defaults before large configuration systems
- **Transparent:** checks should explain exactly why they passed or failed
- **Automation-friendly:** local CLI behavior should translate naturally to CI
- **Local-first:** datasets stay on the user's machine unless they explicitly choose otherwise
- **Extensible:** new rules and sources should be easy to add without rewriting the core

## Security

Do not post sensitive datasets, credentials or production connection strings in public issues.

See [SECURITY.md](SECURITY.md) for reporting guidance.

## License

MIT. See [LICENSE](LICENSE).
