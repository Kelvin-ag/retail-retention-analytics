from pathlib import Path
import os
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE = PROJECT_ROOT / "data" / "retail.duckdb"

# Use dbt installed alongside the Python running this script.
DBT = Path(sys.executable).parent / (
    "dbt.exe" if os.name == "nt" else "dbt"
)

required_files = [
    PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx",
    PROJECT_ROOT / "scripts" / "ingest.py",
    PROJECT_ROOT / "scripts" / "export_marts.py",
    DBT,
]

for path in required_files:
    if not path.is_file():
        raise SystemExit(f"Required file not found: {path}")

environment = os.environ.copy()
environment["RETAIL_DUCKDB_PATH"] = str(DATABASE.resolve())

steps = [
    (
        "Load raw retail data",
        [sys.executable, "scripts/ingest.py"],
    ),
    (
        "Build and test dbt models",
        [
            str(DBT),
            "build",
            "--project-dir", "dbt",
            "--profiles-dir", "dbt",
        ],
    ),
    (
        "Export validated marts",
        [sys.executable, "scripts/export_marts.py"],
    ),
]

for step_number, (label, command) in enumerate(steps, start=1):
    print(f"\nSTEP {step_number}/{len(steps)}: {label}", flush=True)

    try:
        subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            env=environment,
            check=True,
        )
    except subprocess.CalledProcessError as error:
        print(f"\nPipeline stopped: {label} failed.", flush=True)
        raise SystemExit(error.returncode)

print("\nPipeline completed successfully.", flush=True)