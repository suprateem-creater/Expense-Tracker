import argparse
import json
import os
import sys
from datetime import date


def get_storage_path(filepath: str | None = None) -> str:
    return filepath or os.environ.get("EXPENSE_TRACKER_FILE", "expenses.json")


def load_expenses(filepath: str) -> list[dict]:
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                print(f"Error: Data in '{filepath}' is not a valid expense list.", file=sys.stderr)
                sys.exit(1)
            return data
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)


def save_expenses(filepath: str, expenses: list[dict]) -> None:
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(expenses, f, indent=2)
    except OSError as e:
        print(f"Error saving to '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)


def parse_positive_float(value: str) -> float:
    try:
        val = float(value)
        if val <= 0:
            raise ValueError()
        return round(val, 2)
    except ValueError:
        print("Error: Amount must be a positive number.", file=sys.stderr)
        sys.exit(1)


def parse_positive_int(value: str) -> int:
    try:
        val = int(value)
        if val <= 0:
            raise ValueError()
        return val
    except ValueError:
        print("Error: ID must be a positive integer.", file=sys.stderr)
        sys.exit(1)


def cmd_add(args: argparse.Namespace) -> None:
    filepath = get_storage_path(args.file)
    amount = parse_positive_float(args.amount)
    description = args.description.strip()
    if not description:
        print("Error: Description cannot be empty.", file=sys.stderr)
        sys.exit(1)

    expenses = load_expenses(filepath)
    next_id = max((item.get("id", 0) for item in expenses), default=0) + 1
    new_expense = {
        "id": next_id,
        "date": date.today().isoformat(),
        "description": description,
        "amount": amount,
        "category": args.category.strip().lower() if args.category else "general",
    }
    expenses.append(new_expense)
    save_expenses(filepath, expenses)
    print(f"Added expense #{next_id}: {new_expense['description']} (${new_expense['amount']:.2f}) [{new_expense['category']}]")


def cmd_list(args: argparse.Namespace) -> None:
    filepath = get_storage_path(args.file)
    expenses = load_expenses(filepath)

    if args.category:
        cat = args.category.strip().lower()
        expenses = [e for e in expenses if e.get("category", "").lower() == cat]

    if not expenses:
        print("No expenses found.")
        return

    print(f"{'ID':<6}{'Date':<14}{'Category':<14}{'Amount':<12}{'Description'}")
    print("-" * 60)
    for e in expenses:
        amt_str = f"${e.get('amount', 0.0):.2f}"
        print(f"{e.get('id', 0):<6}{e.get('date', ''):<14}{e.get('category', 'general'):<14}{amt_str:<12}{e.get('description', '')}")


def cmd_total(args: argparse.Namespace) -> None:
    filepath = get_storage_path(args.file)
    expenses = load_expenses(filepath)

    category_label = ""
    if args.category:
        cat = args.category.strip().lower()
        expenses = [e for e in expenses if e.get("category", "").lower() == cat]
        category_label = f" for category '{cat}'"

    total = sum(e.get("amount", 0.0) for e in expenses)
    print(f"Total expenses{category_label}: ${total:.2f}")


def cmd_delete(args: argparse.Namespace) -> None:
    filepath = get_storage_path(args.file)
    target_id = parse_positive_int(args.id)
    expenses = load_expenses(filepath)

    original_count = len(expenses)
    expenses = [e for e in expenses if e.get("id") != target_id]

    if len(expenses) == original_count:
        print(f"Error: Expense #{target_id} not found.", file=sys.stderr)
        sys.exit(1)

    save_expenses(filepath, expenses)
    print(f"Deleted expense #{target_id}.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tracker",
        description="Simple CLI Expense Tracker",
    )
    parser.add_argument("--file", help="Path to expenses JSON storage file (default: expenses.json)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = subparsers.add_parser("add", help="Add a new expense")
    p_add.add_argument("description", help="Description of the expense")
    p_add.add_argument("amount", help="Amount of the expense")
    p_add.add_argument("-c", "--category", default="general", help="Category (default: general)")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = subparsers.add_parser("list", help="List all expenses")
    p_list.add_argument("-c", "--category", help="Filter by category")
    p_list.set_defaults(func=cmd_list)

    # total
    p_total = subparsers.add_parser("total", help="Calculate total expenses")
    p_total.add_argument("-c", "--category", help="Filter by category")
    p_total.set_defaults(func=cmd_total)

    # delete
    p_delete = subparsers.add_parser("delete", help="Delete an expense by ID")
    p_delete.add_argument("id", help="Expense ID to delete")
    p_delete.set_defaults(func=cmd_delete)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        sys.exit(e.code)
    args.func(args)


if __name__ == "__main__":
    main()

