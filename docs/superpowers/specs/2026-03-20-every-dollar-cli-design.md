# EveryDollar CLI — Transaction Export Tool

## Overview

A Python CLI tool that pulls transactions from the EveryDollar budget API for a specified budget group and time period, outputting them as CSV.

## CLI Interface

```
every-dollar txns --group "Blue Ridge" --year 2025
every-dollar txns --group "Blue Ridge" --month 2025-03
```

- `txns` is the only subcommand
- `--group` is required (case-insensitive match against group labels)
- `--year` and `--month` are mutually exclusive; one is required
- `--month` format: `YYYY-MM`
- Output goes to stdout (pipeable to file)

## Data Flow

1. Read `SESSION` token from `.env` file
2. `GET /budgets` — returns `budgetExistence` map (see API Details for key format)
3. Determine which budget IDs to fetch based on `--year` or `--month`. Only fetch months present in `budgetExistence` for the requested period (do not assume all 12 months exist).
4. `GET /budgets/:id` for each relevant month
5. In each response, find the group matching `--group` (case-insensitive label match)
6. Collect all allocations from all budget items in that group
7. Sort by date, write CSV to stdout

## API Details

- Base URL: `https://www.everydollar.com/app/api`
- Auth: `SESSION` cookie (value stored in `.env`)
- Endpoints:
  - `GET /budgets` — returns all budget IDs by year/month
  - `GET /budgets/:id` — returns full budget with groups, items, and allocations
- Amounts are in cents (integers)
- `budgetExistence` keys are strings: years are `"2025"`, months are unpadded `"1"` through `"12"` (not zero-padded). Example: `{"2025": {"1": "uuid", "2": "uuid", ...}}`

## Budget Response Structure

```
Budget
  ├── id, date
  └── groups[]
        ├── label (e.g., "Blue Ridge")
        ├── type (income, expense, debt)
        └── budgetItems[]
              ├── label (e.g., "BR Electricity")
              └── allocations[]
                    ├── date
                    ├── merchant
                    ├── amount (cents, signed: positive=credit, negative=debit; CSV uses abs(amount)/100)
                    └── transactionId
```

## CSV Output Format

Columns: `date,month,budget_item,merchant,amount,type`

```
date,month,budget_item,merchant,amount,type
2026-02-20,2026-02,BR Electricity,Tri State Emc,279.00,debit
2026-01-31,2026-02,BR Internet,Ellijay Telephone Co,81.39,debit
2026-02-09,2026-02,Fund,Mobile Deposit,25.00,credit
```

- `date` — the allocation's transaction date
- `month` — the budget month (from the budget's `date` field, formatted as `YYYY-MM`)
- `budget_item` — the budget item label within the group
- `merchant` — merchant name from the allocation
- `amount` — absolute value, converted from cents to dollars (2 decimal places)
- `type` — `credit` when API amount is positive, `debit` when negative. Zero-amount allocations are skipped.
- Rows sorted by date ascending
- Allocations with null/missing `date` or `merchant` are skipped

## Project Structure

```
every_dollar/
  __init__.py
  cli.py          # argparse, main entry point, all logic
.env              # SESSION=<token>
pyproject.toml    # entry point: every-dollar = "every_dollar.cli:main"
```

## Authentication

Session token stored in `.env` as `SESSION=<value>` in the current working directory. Parsed manually (read the file, split on `=`). User manually updates the token when it expires.

## Error Handling

- Missing/expired session token: clear error message directing user to update `.env`
- Group not found in a budget: list available group names from the budget
- No budgets exist for the requested period: clear message stating no data found
- HTTP errors: report status code and stop

## Dependencies

Standard library only: `argparse`, `urllib.request`, `json`, `csv`, `os`. No external packages required (`.env` parsing is simple enough to do manually for a single variable).

## Technology

- Python 3.10+
- No external dependencies
- Entry point via `pyproject.toml` `[project.scripts]`
