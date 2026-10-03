from pathlib import Path
import csv
import pandas as pd

# Locate the project folder relative to this script.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW = PROJECT_ROOT / "data" / "raw"

# Inspect the Excel workbook without loading every row.
with pd.ExcelFile(RAW / "online_retail_II.xlsx") as workbook:
    print("EXCEL SHEETS:", workbook.sheet_names)

    for sheet in workbook.sheet_names:
        sample = pd.read_excel(workbook, sheet_name=sheet, nrows=5)

        print(f"\nSHEET: {sheet}")
        print("COLUMNS:", sample.columns.tolist())
        print(sample.to_string(index=False))

# Inspect the CSV as raw rows, without assuming its header layout.
print("\nCSV PREVIEW — first 8 rows, first 8 fields:")

with open(RAW / "drsi.csv", encoding="utf-8-sig", newline="") as file:
    reader = csv.reader(file)

    for row_number, row in enumerate(reader, start=1):
        print(f"Row {row_number} ({len(row)} fields): {row[:8]}")
        if row_number == 8:
            break