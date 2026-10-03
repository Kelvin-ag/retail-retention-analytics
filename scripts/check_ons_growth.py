import csv
from decimal import Decimal
from pathlib import Path

source = (
    Path(__file__).resolve().parents[1]
    / "data" / "raw" / "drsi.csv"
)

months = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV".split()
expected_periods = {
    f"{year} {month}"
    for year in (2010, 2011)
    for month in months
}
values = {}

with source.open(encoding="utf-8-sig", newline="") as file:
    reader = csv.reader(file)
    next(reader)  # Titles
    codes = next(reader)
    position = codes.index("J596")

    for row in reader:
        if not row:
            continue

        period = row[0].strip()

        if period in expected_periods:
            if period in values:
                raise ValueError(f"Duplicate period: {period}")

            values[period] = Decimal(row[position].strip())

missing = expected_periods - values.keys()
if missing:
    raise ValueError(f"Missing periods: {sorted(missing)}")

averages = {}

print("J596 — JANUARY–NOVEMBER")
for year in (2010, 2011):
    year_values = [values[f"{year} {month}"] for month in months]
    averages[year] = sum(year_values) / Decimal(len(year_values))

    print(
        f"{year}: months={len(year_values)}, "
        f"average_index={averages[year]:.6f}"
    )

growth = (averages[2011] / averages[2010] - 1) * 100
print(f"Change in average monthly index: {growth:.2f}%")