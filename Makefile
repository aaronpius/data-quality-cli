.PHONY: install test lint check demo

install:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check .

check: lint test

demo:
	dqcheck profile examples/customers.csv
