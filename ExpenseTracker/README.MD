# 💰 Expense Tracker (Python CLI)

A simple *Expense Tracker* built with Python that lets you record, view, and manage your daily expenses.  
It stores your data in a JSON file locally and provides options to export/import CSV for easy backup or analysis.

---

## ✨ Features
- ➕ Add expenses with *amount, category, date, and optional note*  
- 📋 List expenses with optional filters (date range, category)  
- 📊 Show *total spend* and *category-wise breakdown*  
- ❌ Remove expenses by ID  
- 📤 Export expenses to CSV (open in Excel/Google Sheets)  
- 📥 Import expenses from a CSV file  
- 💾 Data saved automatically in expenses.json  

---

## 🛠 Requirements
- Python *3.7+*
- No external libraries needed (only built-in Python modules)

---

## 🚀 How to Run
1. Open terminal in the project folder (ExpenseTracker/).
2. Run:
   bash
   python expense_tracker.py
   
3. Use the numbered menu to add, list, summarize, remove, export, or import expenses.

---

## 📂 Project Structure

ExpenseTracker/
│── expense_tracker.py   # Main program
│── expenses.json        # Data file (created automatically after adding expenses)
│── expenses_export.csv  # CSV file (created when exporting)
│── README.md            # Project documentation


---

## 📝 Example Usage

### Adding an expense

Expense Tracker — Menu
1) Add expense
2) List expenses
3) Show summary
4) Remove expense
5) Export CSV
6) Import CSV
7) Exit
Choose an option (1-7): 1

Add a new expense
Amount (e.g. 150.00): 250
Category (e.g. Groceries, Transport): Groceries
Date (YYYY-MM-DD) [default 2025-09-05]:
Note (optional): Vegetables and fruits

Saved:
[3f8b9c12] 2025-09-05  Groceries     ₹250    Vegetables and fruits


### Listing expenses

[3f8b9c12] 2025-09-05  Groceries     ₹250    Vegetables and fruits

Total 1 items shown.


### Summary

Summary
------------------------------
Total expenses: ₹250

By category:
  Groceries     ₹250
------------------------------


---

## 🔮 Future Improvements
- 📆 Monthly and yearly reports  
- 📊 Graphs and charts with Matplotlib  
- 🖥 GUI app with Tkinter  
- ☁ Cloud sync (Google Sheets or web app)

---

## 📜 License
MIT License — free to use, share, and modify.