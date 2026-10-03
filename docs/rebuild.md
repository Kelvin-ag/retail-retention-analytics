## Project Details
- Environment: Windows, Python 3.14.7, Git and Power BI Desktop.
- Dependencies: installed from requirements-lock.txt.
- Required source files: data/raw/online_retail_II.xlsx and data/raw/drsi.csv.
- ONS version used: release 21 August 2026, series J596.
- Raw data is excluded from Git.
- Validation status: full pipeline completed successfully in the development environment; a fresh-environment rebuild has not yet been tested.

## Setup Commands
> py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe scripts\run_pipeline.py

## Power BI Steps
- Open powerbi/RetailRetention.pbip.
- Set SourcePath to the local project’s data/exports folder.
- Set RawSourcePath to its data/raw folder.
- Select Close & Apply, then refresh as needed.