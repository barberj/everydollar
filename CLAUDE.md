# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

EveryDollar CLI — a Python tool that exports transactions from the EveryDollar budget API as CSV. Standard library only, no external dependencies. Python 3.10+.

## Commands

```bash
# Install in dev mode
pip install -e .

# Run the CLI
every-dollar txns --group "Blue Ridge" --year 2025
every-dollar txns --group "Blue Ridge" --month 2025-03

# Run all tests
pytest

# Run a single test
pytest tests/test_cli.py::test_extract_allocations
```

## Architecture

Single-module CLI (`every_dollar/cli.py`) with all logic in one file:
- **API client**: `api_get()` hits `https://www.everydollar.com/app/api` using `urllib.request` with a `SESSION` cookie
- **Data flow**: `load_session()` → `fetch_budget_existence()` → `resolve_budget_ids()` → `fetch_budget()` → `extract_allocations()` → `write_csv()`
- **Auth**: `SESSION` token read from `.env` file in working directory
- **Entry point**: `every-dollar` script defined in `pyproject.toml` → `every_dollar.cli:main`

## Key conventions

- Amounts from the API are in cents (signed integers); CSV output uses absolute dollars with 2 decimal places
- `budgetExistence` map uses unpadded month strings (`"1"` not `"01"`)
- Group matching is case-insensitive
- Allocations with null date, null merchant, or zero amount are skipped
