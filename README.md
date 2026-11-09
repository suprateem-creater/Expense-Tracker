# Expense Tracker CLI

A lightweight, robust command-line expense tracker written in Python. It stores records in a local JSON file and handles invalid inputs and corrupt data gracefully without crashing.

## Features

- **Add Expenses**: Track expenses with an amount, description, and optional category.
- **List Expenses**: View formatted expenses in a clean table view, with optional category filtering.
- **Calculate Total**: View your grand total or filter by a specific category.
- **Delete Expenses**: Remove entries by ID.
- **Safe Persistence**: Stores data in human-readable JSON (`expenses.json`) and handles file errors and invalid inputs gracefully.

---

## Installation

### Prerequisites

- Python 3.10+
- (Optional) `pytest` for running unit tests

### Setup & Install

1. Clone or download this repository:
   ```bash
   git clone <repo-url>
   cd Expense-Tracker
   ```

2. (Option A) Install as an editable CLI command:
   ```bash
   pip install -e .
   ```
   Now you can use the `tracker` command directly:
   ```bash
   tracker --help
   ```

3. (Option B) Run directly with Python without installation:
   ```bash
   python tracker.py --help
   ```

4. Install test dependencies:
   ```bash
   pip install pytest
   ```

---

## Usage & Examples

Run the tool using `tracker <command>` (or `python tracker.py <command>`):

### 1. Add an Expense (`add`)
```bash
tracker add "Coffee" 4.50
tracker add "Lunch" 15.00 -c food
tracker add "Bus pass" 55.00 --category transport
```

### 2. List Expenses (`list`)
List all expenses:
```bash
tracker list
```
*Output:*
```text
ID    Date          Category      Amount      Description
------------------------------------------------------------
1     2026-11-09    general       $4.50       Coffee
2     2026-11-09    food          $15.00      Lunch
3     2026-11-09    transport     $55.00      Bus pass
```

Filter by category:
```bash
tracker list -c food
```

### 3. Calculate Total (`total`)
Show overall total:
```bash
tracker total
```
*Output:*
```text
Total expenses: $74.50
```

Show total for a specific category:
```bash
tracker total -c food
```
*Output:*
```text
Total expenses for category 'food': $15.00
```

### 4. Delete an Expense (`delete`)
Remove an expense by its ID:
```bash
tracker delete 1
```

### 5. Custom Storage File (`--file`)
You can specify a custom JSON file or environment variable:
```bash
tracker --file my_expenses.json add "Book" 19.99
```

---

## Running Tests

Run the test suite using `pytest`:
```bash
pytest
```
or
```bash
python -m pytest -v
```

