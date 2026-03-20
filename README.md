# EveryDollar CLI

A Python CLI that exports transactions from the [EveryDollar](https://www.everydollar.com) budget app as CSV.

## Requirements

- Python 3.10+
- No external dependencies (standard library only)

## Install

```bash
pip install -e .
```

## Authentication

The CLI reads a `SESSION` token from a `.env` file in the current directory:

```
SESSION=your-session-token-here
```

To get your session token, log into EveryDollar in a browser and copy the `SESSION` cookie value.

## Usage

Export transactions for a budget group by year or month:

```bash
# All transactions for a group in a given year
every-dollar txns --group "Groceries" --year 2025

# Single month
every-dollar txns --group "Groceries" --month 2025-03
```

- `--group` is required (case-insensitive match)
- `--year` and `--month` are mutually exclusive; one is required
- `--month` format: `YYYY-MM`
- Output goes to stdout as CSV

### CSV Output

```
date,month,budget_item,merchant,amount,type
2025-02-15,2025-02,Electricity,Tri State,279.00,debit
2025-02-10,2025-02,Savings,Mobile Deposit,50.00,credit
```

| Column | Description |
|---|---|
| `date` | Transaction date |
| `month` | Budget month (`YYYY-MM`) |
| `budget_item` | Item label within the group |
| `merchant` | Merchant name |
| `amount` | Absolute dollar amount (2 decimal places) |
| `type` | `credit` (positive) or `debit` (negative) |

## Tests

```bash
pytest
```
