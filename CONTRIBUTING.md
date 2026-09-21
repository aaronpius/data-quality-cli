# Contributing to dqcheck

Thanks for helping improve dqcheck.

## Ways to contribute

- Report reproducible bugs
- Propose data-quality rules
- Improve documentation and examples
- Add tests
- Implement roadmap items

## Local setup

```bash
git clone https://github.com/aaronpius/data-quality-cli.git
cd data-quality-cli
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
ruff check .
```

## Pull requests

1. Open an issue first for significant behavior changes.
2. Keep PRs focused.
3. Add or update tests for changed behavior.
4. Run `pytest` and `ruff check .` locally.
5. Explain the user-facing impact in the PR description.

## Design principles

- Useful defaults over excessive configuration
- Deterministic checks over opaque scoring
- Human-readable output and machine-readable output
- Local-first processing where practical
- Never upload user datasets without explicit action
