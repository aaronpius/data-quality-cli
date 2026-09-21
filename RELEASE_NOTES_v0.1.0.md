# dqcheck v0.1.0

The first public alpha release of **dqcheck**, a lightweight command-line tool for profiling datasets and enforcing practical data-quality rules.

## Highlights

- Profile CSV, Excel, JSON and optional Parquet files
- Detect duplicate rows, nulls, cardinality and numeric outliers
- Define data-quality expectations in readable YAML
- Validate uniqueness, allowed values and numeric ranges
- Export Markdown and JSON reports
- Use CI-friendly exit codes so failed checks can block pipelines
- Run the same checks locally and in GitHub Actions

## Example

```bash
dqcheck profile examples/customers.csv

dqcheck check examples/customers.csv \
  --rules examples/rules.yaml
```

## Quality and compatibility

The project includes automated CI across:

- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

The release is checked with Ruff and Pytest.

## What is next

The roadmap now includes contributor-ready issues for:

- Regex and pattern validation
- Date freshness checks
- Cross-file referential integrity
- PostgreSQL support
- Snowflake support
- Standalone HTML reports
- A plugin API for custom rules

This is an early alpha release. Feedback, bug reports and contributions are welcome.
