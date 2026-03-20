# EveryDollar CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI tool that exports EveryDollar budget group transactions as CSV.

**Architecture:** Single-file CLI using only the Python standard library. Reads a session token from `.env`, fetches budget data from the EveryDollar API, filters by group label, and writes CSV to stdout.

**Tech Stack:** Python 3.10+, standard library only (`argparse`, `urllib.request`, `json`, `csv`, `sys`, `os`)

**Spec:** `docs/superpowers/specs/2026-03-20-every-dollar-cli-design.md`

---

## File Map

| File | Responsibility |
|------|---------------|
| `every_dollar/__init__.py` | Empty package marker |
| `every_dollar/cli.py` | All logic: arg parsing, API calls, filtering, CSV output |
| `pyproject.toml` | Package metadata, `every-dollar` entry point |
| `.env` | `SESSION=<token>` (gitignored) |
| `.gitignore` | Ignore `.env`, `__pycache__`, etc. |
| `tests/test_cli.py` | Unit tests for parsing, filtering, and CSV output |

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `every_dollar/__init__.py`
- Create: `every_dollar/cli.py` (stub)
- Create: `.gitignore`

- [ ] **Step 1: Create `.gitignore`**

```
.env
__pycache__/
*.pyc
*.egg-info/
dist/
build/
```

- [ ] **Step 2: Create `pyproject.toml`**

```toml
[project]
name = "every-dollar"
version = "0.1.0"
requires-python = ">=3.10"

[project.scripts]
every-dollar = "every_dollar.cli:main"
```

- [ ] **Step 3: Create `every_dollar/__init__.py`**

Empty file.

- [ ] **Step 4: Create `every_dollar/cli.py` stub**

```python
import argparse
import sys


def main():
    print("every-dollar CLI")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Verify the stub runs**

Run: `python -m every_dollar.cli`
Expected: prints "every-dollar CLI"

- [ ] **Step 6: Commit**

```bash
git add .gitignore pyproject.toml every_dollar/__init__.py every_dollar/cli.py
git commit -m "Scaffold every-dollar CLI project"
```

---

### Task 2: Argument Parsing

**Files:**
- Create: `tests/test_cli.py`
- Modify: `every_dollar/cli.py`

- [ ] **Step 1: Write failing tests for argument parsing**

```python
import pytest
from unittest.mock import patch
from every_dollar.cli import build_parser


def test_parse_year():
    parser = build_parser()
    args = parser.parse_args(["txns", "--group", "Blue Ridge", "--year", "2025"])
    assert args.group == "Blue Ridge"
    assert args.year == "2025"
    assert args.month is None


def test_parse_month():
    parser = build_parser()
    args = parser.parse_args(["txns", "--group", "Blue Ridge", "--month", "2025-03"])
    assert args.group == "Blue Ridge"
    assert args.month == "2025-03"
    assert args.year is None


def test_year_and_month_mutually_exclusive():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["txns", "--group", "Blue Ridge", "--year", "2025", "--month", "2025-03"])


def test_group_required():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["txns", "--year", "2025"])


def test_year_or_month_required():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["txns", "--group", "Blue Ridge"])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_cli.py -v`
Expected: FAIL — `build_parser` not found

- [ ] **Step 3: Implement `build_parser`**

```python
def build_parser():
    parser = argparse.ArgumentParser(prog="every-dollar")
    sub = parser.add_subparsers(dest="command")

    txns = sub.add_parser("txns")
    txns.add_argument("--group", required=True)

    period = txns.add_mutually_exclusive_group(required=True)
    period.add_argument("--year")
    period.add_argument("--month")

    return parser
```

Update `main()` to use `build_parser()`:

```python
def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.command != "txns":
        parser.print_help()
        sys.exit(1)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_cli.py -v`
Expected: all 5 PASS

- [ ] **Step 5: Commit**

```bash
git add every_dollar/cli.py tests/test_cli.py
git commit -m "Add argument parsing with txns subcommand"
```

---

### Task 3: Session Token Loading

**Files:**
- Modify: `tests/test_cli.py`
- Modify: `every_dollar/cli.py`

- [ ] **Step 1: Write failing tests for session loading**

```python
import os
import tempfile


def test_load_session_from_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("SESSION=abc123\n")
    token = load_session(str(env_file))
    assert token == "abc123"


def test_load_session_missing_file():
    with pytest.raises(SystemExit):
        load_session("/nonexistent/.env")


def test_load_session_missing_key(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("OTHER=value\n")
    with pytest.raises(SystemExit):
        load_session(str(env_file))
```

Add `from every_dollar.cli import build_parser, load_session` to imports.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_cli.py::test_load_session_from_env_file -v`
Expected: FAIL — `load_session` not found

- [ ] **Step 3: Implement `load_session`**

```python
def load_session(env_path=".env"):
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("SESSION="):
                    return line.split("=", 1)[1]
    except FileNotFoundError:
        pass
    print("Error: SESSION not found. Set SESSION=<token> in .env", file=sys.stderr)
    sys.exit(1)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_cli.py -v`
Expected: all 8 PASS

- [ ] **Step 5: Commit**

```bash
git add every_dollar/cli.py tests/test_cli.py
git commit -m "Add session token loading from .env"
```

---

### Task 4: Budget ID Resolution

**Files:**
- Modify: `tests/test_cli.py`
- Modify: `every_dollar/cli.py`

- [ ] **Step 1: Write failing tests for budget ID resolution**

```python
SAMPLE_EXISTENCE = {
    "2025": {
        "1": "uuid-jan",
        "2": "uuid-feb",
        "3": "uuid-mar",
    },
    "2024": {
        "11": "uuid-nov",
        "12": "uuid-dec",
    },
}


def test_resolve_budget_ids_by_year():
    result = resolve_budget_ids(SAMPLE_EXISTENCE, year="2025")
    assert result == ["uuid-jan", "uuid-feb", "uuid-mar"]


def test_resolve_budget_ids_by_month():
    result = resolve_budget_ids(SAMPLE_EXISTENCE, month="2025-02")
    assert result == ["uuid-feb"]


def test_resolve_budget_ids_year_not_found():
    with pytest.raises(SystemExit):
        resolve_budget_ids(SAMPLE_EXISTENCE, year="2023")


def test_resolve_budget_ids_month_not_found():
    with pytest.raises(SystemExit):
        resolve_budget_ids(SAMPLE_EXISTENCE, month="2025-06")


def test_resolve_budget_ids_by_year_sorted_by_month():
    existence = {"2024": {"2": "uuid-feb", "11": "uuid-nov", "1": "uuid-jan"}}
    result = resolve_budget_ids(existence, year="2024")
    assert result == ["uuid-jan", "uuid-feb", "uuid-nov"]
```

Add `resolve_budget_ids` to imports.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_cli.py::test_resolve_budget_ids_by_year -v`
Expected: FAIL — `resolve_budget_ids` not found

- [ ] **Step 3: Implement `resolve_budget_ids`**

```python
def resolve_budget_ids(budget_existence, year=None, month=None):
    if year:
        months = budget_existence.get(year)
        if not months:
            print(f"Error: No budgets found for year {year}", file=sys.stderr)
            sys.exit(1)
        return [months[k] for k in sorted(months, key=lambda m: int(m))]

    # month format: "YYYY-MM"
    y, m = month.split("-")
    m = str(int(m))  # strip leading zero
    months = budget_existence.get(y)
    if not months or m not in months:
        print(f"Error: No budget found for {month}", file=sys.stderr)
        sys.exit(1)
    return [months[m]]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_cli.py -v`
Expected: all 13 PASS

- [ ] **Step 5: Commit**

```bash
git add every_dollar/cli.py tests/test_cli.py
git commit -m "Add budget ID resolution from budgetExistence map"
```

---

### Task 5: Group Filtering and Allocation Extraction

**Files:**
- Modify: `tests/test_cli.py`
- Modify: `every_dollar/cli.py`

- [ ] **Step 1: Write failing tests for extraction**

```python
SAMPLE_BUDGET = {
    "id": "budget-1",
    "date": "2025-02-01",
    "groups": [
        {
            "label": "Blue Ridge",
            "budgetItems": [
                {
                    "label": "BR Electricity",
                    "allocations": [
                        {"date": "2025-02-15", "merchant": "Tri State", "amount": -27900},
                        {"date": None, "merchant": "Bad", "amount": -100},
                        {"date": "2025-02-16", "merchant": None, "amount": -200},
                    ],
                },
                {
                    "label": "BR Internet",
                    "allocations": [
                        {"date": "2025-01-31", "merchant": "Ellijay Tel", "amount": -8139},
                    ],
                },
                {
                    "label": "Fund",
                    "allocations": [
                        {"date": "2025-02-10", "merchant": "Deposit", "amount": 5000},
                        {"date": "2025-02-11", "merchant": "Zero", "amount": 0},
                    ],
                },
            ],
        },
        {
            "label": "Food",
            "budgetItems": [],
        },
    ],
}


def test_extract_allocations():
    rows = extract_allocations(SAMPLE_BUDGET, "Blue Ridge")
    assert len(rows) == 3  # skips null date, null merchant, and zero amount
    assert rows[0] == {
        "date": "2025-01-31",
        "month": "2025-02",
        "budget_item": "BR Internet",
        "merchant": "Ellijay Tel",
        "amount": "81.39",
        "type": "debit",
    }
    assert rows[1] == {
        "date": "2025-02-10",
        "month": "2025-02",
        "budget_item": "Fund",
        "merchant": "Deposit",
        "amount": "50.00",
        "type": "credit",
    }
    assert rows[2] == {
        "date": "2025-02-15",
        "month": "2025-02",
        "budget_item": "BR Electricity",
        "merchant": "Tri State",
        "amount": "279.00",
        "type": "debit",
    }


def test_extract_allocations_case_insensitive():
    rows = extract_allocations(SAMPLE_BUDGET, "blue ridge")
    assert len(rows) == 3


def test_extract_allocations_group_not_found():
    with pytest.raises(SystemExit):
        extract_allocations(SAMPLE_BUDGET, "Nonexistent")
```

Add `extract_allocations` to imports.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_cli.py::test_extract_allocations -v`
Expected: FAIL — `extract_allocations` not found

- [ ] **Step 3: Implement `extract_allocations`**

```python
def extract_allocations(budget, group_name):
    budget_month = budget["date"][:7]  # "2025-02-01" -> "2025-02"

    group = None
    for g in budget["groups"]:
        if g["label"].lower() == group_name.lower():
            group = g
            break

    if group is None:
        available = [g["label"] for g in budget["groups"]]
        print(f"Error: Group '{group_name}' not found. Available: {', '.join(available)}", file=sys.stderr)
        sys.exit(1)

    rows = []
    for item in group["budgetItems"]:
        for alloc in item.get("allocations", []):
            if not alloc.get("date") or not alloc.get("merchant"):
                continue
            amount_cents = alloc["amount"]
            if amount_cents == 0:
                continue
            rows.append({
                "date": alloc["date"],
                "month": budget_month,
                "budget_item": item["label"],
                "merchant": alloc["merchant"],
                "amount": f"{abs(amount_cents) / 100:.2f}",
                "type": "credit" if amount_cents > 0 else "debit",
            })

    rows.sort(key=lambda r: r["date"])
    return rows
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_cli.py -v`
Expected: all 16 PASS

- [ ] **Step 5: Commit**

```bash
git add every_dollar/cli.py tests/test_cli.py
git commit -m "Add group filtering and allocation extraction"
```

---

### Task 6: CSV Output

**Files:**
- Modify: `tests/test_cli.py`
- Modify: `every_dollar/cli.py`

- [ ] **Step 1: Write failing test for CSV output**

```python
import io


def test_write_csv():
    rows = [
        {"date": "2025-02-15", "month": "2025-02", "budget_item": "BR Electricity", "merchant": "Tri State", "amount": "279.00", "type": "debit"},
        {"date": "2025-02-10", "month": "2025-02", "budget_item": "Fund", "merchant": "Deposit", "amount": "50.00", "type": "credit"},
    ]
    output = io.StringIO()
    write_csv(rows, output)
    result = output.getvalue()
    lines = result.strip().split("\n")
    assert lines[0] == "date,month,budget_item,merchant,amount,type"
    assert lines[1] == "2025-02-15,2025-02,BR Electricity,Tri State,279.00,debit"
    assert lines[2] == "2025-02-10,2025-02,Fund,Deposit,50.00,credit"


def test_write_csv_empty():
    output = io.StringIO()
    write_csv([], output)
    result = output.getvalue()
    lines = result.strip().split("\n")
    assert len(lines) == 1  # header only
```

Add `write_csv` to imports.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_cli.py::test_write_csv -v`
Expected: FAIL — `write_csv` not found

- [ ] **Step 3: Implement `write_csv`**

```python
import csv


FIELDS = ["date", "month", "budget_item", "merchant", "amount", "type"]


def write_csv(rows, output=None):
    if output is None:
        output = sys.stdout
    writer = csv.DictWriter(output, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_cli.py -v`
Expected: all 18 PASS

- [ ] **Step 5: Commit**

```bash
git add every_dollar/cli.py tests/test_cli.py
git commit -m "Add CSV output writer"
```

---

### Task 7: API Client and Main Wiring

**Files:**
- Modify: `every_dollar/cli.py`

- [ ] **Step 1: Implement API fetch functions**

```python
import json
import urllib.request
import urllib.error

BASE_URL = "https://www.everydollar.com/app/api"


def api_get(path, session):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    req.add_header("Cookie", f"SESSION={session}")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"Error: API returned {e.code} for {path}", file=sys.stderr)
        sys.exit(1)


def fetch_budget_existence(session):
    data = api_get("/budgets", session)
    return data["budgetExistence"]


def fetch_budget(budget_id, session):
    return api_get(f"/budgets/{budget_id}", session)
```

- [ ] **Step 2: Wire up `main()`**

```python
def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.command != "txns":
        parser.print_help()
        sys.exit(1)

    session = load_session()
    existence = fetch_budget_existence(session)
    budget_ids = resolve_budget_ids(existence, year=args.year, month=args.month)

    all_rows = []
    for bid in budget_ids:
        budget = fetch_budget(bid, session)
        all_rows.extend(extract_allocations(budget, args.group))

    all_rows.sort(key=lambda r: r["date"])
    write_csv(all_rows)
```

- [ ] **Step 3: Verify the full module runs without errors**

Run: `python -m every_dollar.cli txns --help`
Expected: prints usage showing `--group`, `--year`, `--month`

- [ ] **Step 4: Commit**

```bash
git add every_dollar/cli.py
git commit -m "Wire up API client and main entry point"
```

---

### Task 8: Manual End-to-End Test

**Files:** none (verification only)

- [ ] **Step 1: Create `.env` with a valid session token**

Create `.env` in the project root:
```
SESSION=<your-actual-token>
```

- [ ] **Step 2: Test single month**

Run: `python -m every_dollar.cli txns --group "Blue Ridge" --month 2026-02`
Expected: CSV output to stdout with Blue Ridge transactions for February 2026

- [ ] **Step 3: Test full year**

Run: `python -m every_dollar.cli txns --group "Blue Ridge" --year 2025 > blue_ridge_2025.csv`
Expected: CSV file created with all Blue Ridge transactions for 2025

- [ ] **Step 4: Test error cases**

Run: `python -m every_dollar.cli txns --group "Nonexistent" --month 2026-02`
Expected: error listing available group names

Run: `python -m every_dollar.cli txns --group "Blue Ridge" --year 1999`
Expected: error about no budgets found

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "Complete EveryDollar CLI transaction export tool"
```
