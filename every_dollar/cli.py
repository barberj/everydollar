import argparse
import csv
import json
import sys
import urllib.error
import urllib.request


FIELDS = ["date", "month", "budget_item", "merchant", "amount", "type"]

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


def write_csv(rows, output=None):
    if output is None:
        output = sys.stdout
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


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


def build_parser():
    parser = argparse.ArgumentParser(prog="every-dollar")
    sub = parser.add_subparsers(dest="command")

    txns = sub.add_parser("txns")
    txns.add_argument("--group", required=True)

    period = txns.add_mutually_exclusive_group(required=True)
    period.add_argument("--year")
    period.add_argument("--month")

    return parser


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


if __name__ == "__main__":
    main()
