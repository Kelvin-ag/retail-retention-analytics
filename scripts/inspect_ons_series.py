import csv
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
source = project_root / "data" / "raw" / "drsi.csv"

with source.open(encoding="utf-8-sig", newline="") as file:
    reader = csv.reader(file)
    series_names = next(reader)
    series_codes = next(reader)

for name, code in zip(series_names, series_codes):
    normalised = " ".join(name.lower().split())

    if all(
        phrase in normalised
        for phrase in (
            "non-store",
            "value",
            "not seasonally adjusted",
            "all business index",
        )
    ):
        print(f"Series code: {code}")
        print(f"Series name: {name}\n")

print("\nSOURCE FILE CHECK — J596")

with source.open(encoding="utf-8-sig", newline="") as file:
    reader = csv.reader(file)
    next(reader)  # Skip titles
    codes = next(reader)
    series_position = codes.index("J596")

    for row in reader:
        if row and row[0].strip() in {
            "Release Date",
            "2009 DEC",
            "2011 NOV",
        }:
            print(f"{row[0]}: {row[series_position]}")