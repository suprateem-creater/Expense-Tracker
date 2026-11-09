import json
import pytest
from tracker import main


def run_cli(capsys, args: list[str]):
    try:
        main(args)
        code = 0
    except SystemExit as exc:
        code = exc.code
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_add_expense(tmp_path, capsys):
    db_file = str(tmp_path / "expenses.json")

    code, out, err = run_cli(capsys, ["--file", db_file, "add", "Coffee", "4.50", "-c", "Food"])
    assert code == 0
    assert "Added expense #1: Coffee ($4.50) [food]" in out
    assert err == ""

    with open(db_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["id"] == 1
    assert data[0]["description"] == "Coffee"
    assert data[0]["amount"] == 4.50
    assert data[0]["category"] == "food"


def test_add_bad_input(tmp_path, capsys):
    db_file = str(tmp_path / "expenses.json")

    # Negative amount
    code, out, err = run_cli(capsys, ["--file", db_file, "add", "Coffee", "-5"])
    assert code == 1
    assert "Amount must be a positive number" in err

    # Non-numeric amount
    code, out, err = run_cli(capsys, ["--file", db_file, "add", "Coffee", "abc"])
    assert code == 1
    assert "Amount must be a positive number" in err

    # Zero amount
    code, out, err = run_cli(capsys, ["--file", db_file, "add", "Coffee", "0"])
    assert code == 1
    assert "Amount must be a positive number" in err

    # Empty description
    code, out, err = run_cli(capsys, ["--file", db_file, "add", "   ", "10"])
    assert code == 1
    assert "Description cannot be empty" in err


def test_list_and_total_with_filtering(tmp_path, capsys):
    db_file = str(tmp_path / "expenses.json")

    # Empty list
    code, out, err = run_cli(capsys, ["--file", db_file, "list"])
    assert code == 0
    assert "No expenses found." in out

    # Add items
    run_cli(capsys, ["--file", db_file, "add", "Lunch", "15.00", "-c", "food"])
    run_cli(capsys, ["--file", db_file, "add", "Bus Ticket", "2.50", "-c", "transport"])
    run_cli(capsys, ["--file", db_file, "add", "Dinner", "25.50", "-c", "food"])

    # List all
    code, out, err = run_cli(capsys, ["--file", db_file, "list"])
    assert code == 0
    assert "Lunch" in out
    assert "Bus Ticket" in out
    assert "Dinner" in out

    # List filtered
    code, out, err = run_cli(capsys, ["--file", db_file, "list", "-c", "transport"])
    assert code == 0
    assert "Bus Ticket" in out
    assert "Lunch" not in out

    # Total all
    code, out, err = run_cli(capsys, ["--file", db_file, "total"])
    assert code == 0
    assert "Total expenses: $43.00" in out

    # Total category
    code, out, err = run_cli(capsys, ["--file", db_file, "total", "-c", "food"])
    assert code == 0
    assert "Total expenses for category 'food': $40.50" in out


def test_delete_expense(tmp_path, capsys):
    db_file = str(tmp_path / "expenses.json")

    run_cli(capsys, ["--file", db_file, "add", "Snack", "3.00"])
    run_cli(capsys, ["--file", db_file, "add", "Book", "12.00"])

    # Delete existing
    code, out, err = run_cli(capsys, ["--file", db_file, "delete", "1"])
    assert code == 0
    assert "Deleted expense #1." in out

    # Verify deleted
    code, out, err = run_cli(capsys, ["--file", db_file, "list"])
    assert code == 0
    assert "Snack" not in out
    assert "Book" in out

    # Delete non-existent ID
    code, out, err = run_cli(capsys, ["--file", db_file, "delete", "99"])
    assert code == 1
    assert "Expense #99 not found" in err

    # Bad ID input
    code, out, err = run_cli(capsys, ["--file", db_file, "delete", "invalid"])
    assert code == 1
    assert "ID must be a positive integer" in err


def test_corrupted_json_handling(tmp_path, capsys):
    db_file = tmp_path / "expenses.json"
    db_file.write_text("{not valid json", encoding="utf-8")

    code, out, err = run_cli(capsys, ["--file", str(db_file), "list"])
    assert code == 1
    assert "Error reading" in err

