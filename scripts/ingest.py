from pathlib import Path
import hashlib
import json

import duckdb
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"
DATABASE = PROJECT_ROOT / "data" / "retail.duckdb"
LOG = PROJECT_ROOT / "data" / "retail_ingestion_log.json"

# A fingerprint lets us identify exactly which source file was loaded.
fingerprint = hashlib.sha256()
with SOURCE.open("rb") as file:
    for chunk in iter(lambda: file.read(1024 * 1024), b""):
        fingerprint.update(chunk)

sheet_tables = {
    "Year 2009-2010": "raw_retail_2009_2010",
    "Year 2010-2011": "raw_retail_2010_2011",
}

load_log = {
    "source_file": SOURCE.name,
    "sha256": fingerprint.hexdigest(),
    "tables": [],
}

with duckdb.connect(str(DATABASE)) as connection:
    with pd.ExcelFile(SOURCE) as workbook:
        for sheet, table in sheet_tables.items():
            print(f"Loading {sheet}...", flush=True)

            # Identifiers are labels, so preserve them as text.
            frame = pd.read_excel(
                workbook,
                sheet_name=sheet,
                dtype={
                    "Invoice": "string",
                    "StockCode": "string",
                    "Customer ID": "string",
                },
            )

            connection.register("source_rows", frame)

            # Re-running replaces each raw table instead of duplicating rows.
            connection.execute(
                f"CREATE OR REPLACE TABLE {table} AS "
                "SELECT * FROM source_rows"
            )

            loaded_rows = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            if loaded_rows != len(frame):
                raise ValueError(f"Row count mismatch for {sheet}")

            load_log["tables"].append({
                "sheet": sheet,
                "table": table,
                "source_rows": len(frame),
                "loaded_rows": loaded_rows,
            })

            connection.unregister("source_rows")
            print(f"{table}: {loaded_rows:,} rows loaded")

LOG.write_text(json.dumps(load_log, indent=2), encoding="utf-8")

print(f"\nDatabase saved: {DATABASE}")
print(f"Ingestion log saved: {LOG}")