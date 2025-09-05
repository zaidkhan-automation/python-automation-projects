#!/usr/bin/env python3
"""
Expense Tracker (simple CLI)

Features:
- Add expense (amount, category, date, optional note)
- List expenses (filter by date range, category)
- Show totals and category totals
- Remove expense by id
- Export / import CSV
- Data persisted in 'expenses.json' in the same folder

How to run:
    python expense_tracker.py
"""
import json
import csv
import os
import uuid
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import List, Dict

DATA_FILE = "expenses.json"
DATE_FORMAT = "%Y-%m-%d"  # ISO style date

# -------------------------
# Helper I/O for data file
# -------------------------
def load_data() -> List[Dict]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            raw = json.load(f)
        except json.JSONDecodeError:
            return []
    # convert amount back to Decimal
    for item in raw:
        item["amount"] = Decimal(str(item["amount"]))
    return raw

def save_data(data: List[Dict]) -> None:
    safe = []
    for item in data:
        safe.append({
            "id": item["id"],
            "date": item["date"],               # string YYYY-MM-DD
            "category": item["category"],
            "amount": str(item["amount"]),      # save decimal as string
            "note": item.get("note", "")
        })
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(safe, f, indent=2, ensure_ascii=False)

# -------------------------
# Utility functions
# -------------------------
def parse_date(s: str) -> str:
    """Accept YYYY-MM-DD or empty (returns today's date)."""
    s = s.strip()
    if not s:
        return date.today().isoformat()
    try:
        dt = datetime.strptime(s, DATE_FORMAT).date()
        return dt.isoformat()
    except ValueError:
        raise ValueError(f"Invalid date format. Expected {DATE_FORMAT} (e.g. 2025-09-05).")

def parse_amount(s: str) -> Decimal:
    s = s.strip()
    try:
        # accept inputs like 12.50
        return Decimal(s)
    except InvalidOperation:
        raise ValueError("Invalid amount. Use a number like 12.50")

def print_expense(e: Dict) -> None:
    print(f"[{e['id'][:8]}] {e['date']}  {e['category']:<12}  ₹{e['amount']:>8}    {e.get('note','')}")

# -------------------------
# Main features
# -------------------------
def add_expense(data: List[Dict]) -> None:
    print("\nAdd a new expense")
    while True:
        try:
            amt = parse_amount(input("Amount (e.g. 150.00): ").strip())
            break
        except ValueError as ex:
            print(">", ex)

    cat = input("Category (e.g. Groceries, Transport): ").strip() or "Misc"
    date_input = input(f"Date (YYYY-MM-DD) [default {date.today().isoformat()}]: ")
    try:
        dt = parse_date(date_input)
    except ValueError as ex:
        print(">", ex)
        return
    note = input("Note (optional): ").strip()

    item = {
        "id": uuid.uuid4().hex,
        "date": dt,
        "category": cat,
        "amount": amt,
        "note": note
    }
    data.append(item)
    save_data(data)
    print("Saved:")
    print_expense(item)

def list_expenses(data: List[Dict]) -> None:
    print("\nList expenses (press Enter to skip a filter)")
    start = input("Start date (YYYY-MM-DD) [optional]: ").strip()
    end = input("End date (YYYY-MM-DD) [optional]: ").strip()
    cat = input("Category [optional]: ").strip()

    try:
        start_d = datetime.strptime(start, DATE_FORMAT).date() if start else None
        end_d = datetime.strptime(end, DATE_FORMAT).date() if end else None
    except ValueError:
        print("Invalid date format. Aborting list.")
        return

    filtered = []
    for e in data:
        e_date = datetime.fromisoformat(e["date"]).date()
        if start_d and e_date < start_d:
            continue
        if end_d and e_date > end_d:
            continue
        if cat and e["category"].lower() != cat.lower():
            continue
        filtered.append(e)

    if not filtered:
        print("No expenses found for the filters.")
        return

    # sort by date descending
    filtered.sort(key=lambda x: x["date"], reverse=True)
    for item in filtered:
        print_expense(item)
    print(f"\nTotal {len(filtered)} items shown.")

def show_summary(data: List[Dict]) -> None:
    if not data:
        print("\nNo expenses recorded yet.")
        return
    total = sum(e["amount"] for e in data)
    by_cat = {}
    for e in data:
        by_cat.setdefault(e["category"], Decimal(0))
        by_cat[e["category"]] += e["amount"]

    print("\nSummary")
    print("-" * 30)
    print(f"Total expenses: ₹{total}")
    print("\nBy category:")
    for cat, amt in sorted(by_cat.items(), key=lambda kv: kv[1], reverse=True):
        print(f"  {cat:<12} ₹{amt}")
    print("-" * 30)

def remove_expense(data: List[Dict]) -> None:
    print("\nRemove expense by id (first 8 chars shown in brackets above)")
    rid = input("Enter id (or leading 8 chars): ").strip()
    if not rid:
        print("No id entered.")
        return
    found = None
    for e in data:
        if e["id"].startswith(rid):
            found = e
            break
    if not found:
        print("No expense found with that id.")
        return
    print("Found:")
    print_expense(found)
    if input("Delete this expense? (y/N): ").strip().lower() == "y":
        data.remove(found)
        save_data(data)
        print("Deleted.")
    else:
        print("Cancelled.")

def export_csv(data: List[Dict]) -> None:
    filename = input("CSV filename to write [expenses_export.csv]: ").strip() or "expenses_export.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "date", "category", "amount", "note"])
        for e in data:
            writer.writerow([e["id"], e["date"], e["category"], str(e["amount"]), e.get("note","")])
    print("Exported to", filename)

def import_csv(data: List[Dict]) -> None:
    filename = input("CSV filename to import: ").strip()
    if not filename or not os.path.exists(filename):
        print("File not found.")
        return
    count = 0
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                amt = Decimal(row.get("amount","0"))
                dt = parse_date(row.get("date",""))
            except Exception:
                print("Skipping row with invalid data:", row)
                continue
            item = {
                "id": row.get("id", uuid.uuid4().hex),
                "date": dt,
                "category": row.get("category","Misc"),
                "amount": amt,
                "note": row.get("note","")
            }
            data.append(item)
            count += 1
    save_data(data)
    print(f"Imported {count} rows from {filename}")

# -------------------------
# CLI loop
# -------------------------
def print_menu():
    print("\nExpense Tracker — Menu")
    print("1) Add expense")
    print("2) List expenses")
    print("3) Show summary")
    print("4) Remove expense")
    print("5) Export CSV")
    print("6) Import CSV")
    print("7) Exit")

def main():
    data = load_data()
    while True:
        print_menu()
        choice = input("Choose an option (1-7): ").strip()
        if choice in ("1", "add"):
            add_expense(data)
        elif choice in ("2", "list"):
            list_expenses(data)
        elif choice in ("3", "summary"):
            show_summary(data)
        elif choice in ("4", "remove"):
            remove_expense(data)
        elif choice in ("5", "export"):
            export_csv(data)
        elif choice in ("6", "import"):
            import_csv(data)
        elif choice in ("7", "exit", "quit"):
            print("Goodbye — data saved.")
            break
        else:
            print("Unknown option. Try 1-7 or type commands: add, list, summary, remove, export, import, exit")

if __name__ == "__main__":
    main()