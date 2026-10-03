from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE = PROJECT_ROOT / "data" / "retail.duckdb"

# getting table details; including all missing id's and cancellations. Get an overall row count from both sheets
with duckdb.connect(str(DATABASE), read_only=True) as connection:
    connection.execute("""
        CREATE TEMP VIEW combined AS
        SELECT *
        FROM raw_retail_2009_2010
        WHERE "InvoiceDate" < TIMESTAMP '2010-12-01'

        UNION ALL

        SELECT *
        FROM raw_retail_2010_2011
    """)
    for table in ["raw_retail_2009_2010", "raw_retail_2010_2011"]:
        result = connection.execute(f"""
            SELECT
                COUNT(*) AS total_rows,
                MIN("InvoiceDate") AS earliest_date,
                MAX("InvoiceDate") AS latest_date,
                COUNT(*) FILTER (
                    WHERE "Customer ID" IS NULL
                ) AS missing_customer_rows,
                COUNT(*) FILTER (
                    WHERE "Invoice" LIKE 'C%'
                ) AS cancellation_rows,
                COUNT(*) FILTER (
                    WHERE "Quantity" < 0
                ) AS negative_quantity_rows,
                COUNT(*) FILTER (
                    WHERE "Price" = 0
                ) AS zero_price_rows,
                COUNT(*) FILTER (
                    WHERE "Price" < 0
                ) AS negative_price_rows
            FROM {table}
        """).fetchdf()

        print(f"\n{table}")
        print(result.T.to_string(header=False))

    # Counting how many record are duplicated in both tables because there are overlapping time periods
    overlap = connection.execute("""
        SELECT COUNT(*) AS matching_rows
        FROM (
            SELECT * FROM raw_retail_2009_2010
            INTERSECT ALL
            SELECT * FROM raw_retail_2010_2011
        ) AS shared_rows
    """).fetchone()[0]

    print(f"\nExact matching rows across sheets: {overlap:,}")

    #Counting unmatched rows from the first sheet after Dec 1st 2010
    unmatched = connection.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT *
            FROM raw_retail_2009_2010
            WHERE "InvoiceDate" >= TIMESTAMP '2010-12-01'

            EXCEPT ALL

            SELECT *
            FROM raw_retail_2010_2011
        ) AS unmatched_rows
    """).fetchone()[0]

    print(f"Unmatched first-sheet rows in overlap: {unmatched:,}")

    # Appending table rows from both sheets for further analysis
    append = connection.execute("""
        SELECT
            COUNT(*) AS total_rows,
            COUNT(*) FILTER (
                WHERE "Customer ID" IS NULL
            ) AS missing_customer_rows,
            ROUND(
                100.0 * COUNT(*) FILTER (
                    WHERE "Customer ID" IS NULL
                ) / COUNT(*),
                2
            ) AS missing_customer_pct,
            MIN("InvoiceDate") AS earliest_date,
            MAX("InvoiceDate") AS latest_date
        FROM combined
    """).fetchdf()

    print("\nCOMBINED DATA CHECK")
    print(append.T.to_string(header=False))

    # Diagnosing revenue taking missing customer ID's into account
    revenue_coverage = connection.execute("""
        SELECT
            CASE
                WHEN "Customer ID" IS NULL THEN 'Missing ID'
                ELSE 'Identified'
            END AS customer_status,
            COUNT(*) AS row_count,
            ROUND(SUM(
                CASE WHEN "Quantity" > 0 AND "Price" > 0
                     THEN "Quantity" * "Price" ELSE 0 END
            ), 2) AS positive_sales_value,
            ROUND(SUM(
                CASE WHEN "Quantity" < 0 AND "Price" > 0
                     THEN "Quantity" * "Price" ELSE 0 END
            ), 2) AS negative_quantity_value,
            ROUND(SUM("Quantity" * "Price"), 2) AS signed_line_value
        FROM combined
        GROUP BY 1
        ORDER BY 1
    """).fetchdf()

    print("\nVALUE BY CUSTOMER ID AVAILABILITY")
    print(revenue_coverage.to_string(index=False))

    # investigaing the negative price rows because of a discrepancy in the figures
    negative_prices = connection.execute("""
        SELECT *,
               ROUND("Quantity" * "Price", 2) AS line_value
        FROM combined
        WHERE "Price" < 0
        ORDER BY "InvoiceDate"
    """).fetchdf()

    print("\nNEGATIVE-PRICE RECORDS")
    print(negative_prices.to_string(index=False))

    # Checking every record with stock code "B"
    bad_debt = connection.execute("""
        SELECT *,
               ROUND("Quantity" * "Price", 2) AS line_value
        FROM combined
        WHERE "StockCode" = 'B'
        ORDER BY "InvoiceDate", "Invoice"
    """).fetchdf()

    print("\nALL STOCK CODE B RECORDS")
    print(bad_debt.to_string(index=False))

    # Identifying other none product codes
    unusual_codes = connection.execute("""
        SELECT
            "StockCode",
            "Description",
            COUNT(*) AS row_count,
            ROUND(SUM("Quantity" * "Price"), 2) AS signed_value
        FROM combined
        WHERE "StockCode" IS NULL
           OR NOT regexp_matches("StockCode", '^[0-9]{5}')
        GROUP BY "StockCode", "Description"
        ORDER BY "StockCode", row_count DESC
    """).fetchdf()

    print("\nCODES FOR REVIEW")
    print(unusual_codes.to_string(index=False))

    # Inspecting a sample of entries
    manual_entries = connection.execute("""
        SELECT *,
               ROUND("Quantity" * "Price", 2) AS line_value
        FROM combined
        WHERE UPPER(TRIM("StockCode")) = 'M'
        ORDER BY ABS("Quantity" * "Price") DESC,
                 "InvoiceDate", "Invoice"
        LIMIT 20
    """).fetchdf()

    print("\nLARGEST MANUAL ENTRIES")
    print(manual_entries.to_string(index=False))

    # Inspecting records where prices are zero
    zero_prices = connection.execute("""
        SELECT
            "Description",
            COUNT(*) AS row_count,
            COUNT(*) FILTER (
                WHERE "Customer ID" IS NOT NULL
            ) AS identified_rows,
            MIN("Quantity") AS min_quantity,
            MAX("Quantity") AS max_quantity
        FROM combined
        WHERE "Price" = 0
        GROUP BY "Description"
        ORDER BY row_count DESC
        LIMIT 25
    """).fetchdf()

    print("\nZERO-PRICE RECORDS — TOP 25 DESCRIPTIONS")
    print(zero_prices.to_string(index=False))

    # Summarising all rows with price at zero
    zero_summary = connection.execute("""
        SELECT
            COUNT(*) AS zero_price_rows,
            COUNT(*) FILTER (
                WHERE "Customer ID" IS NOT NULL
            ) AS identified_rows,
            COUNT(*) FILTER (
                WHERE "Quantity" > 0
            ) AS positive_quantity_rows,
            COUNT(*) FILTER (
                WHERE "Quantity" < 0
            ) AS negative_quantity_rows,
            COUNT(*) FILTER (
                WHERE "Quantity" = 0
            ) AS zero_quantity_rows
        FROM combined
        WHERE "Price" = 0
    """).fetchdf()

    print("\nZERO-PRICE SUMMARY")
    print(zero_summary.T.to_string(header=False))

    # invoice type and quantity sign
    cancellation_check = connection.execute("""
        SELECT
            CASE
                WHEN "Invoice" IS NULL THEN 'Missing invoice'
                WHEN UPPER(TRIM("Invoice")) LIKE 'C%'
                    THEN 'Cancellation'
                ELSE 'Other invoice'
            END AS invoice_type,
            CASE
                WHEN "Quantity" > 0 THEN 'Positive'
                WHEN "Quantity" < 0 THEN 'Negative'
                WHEN "Quantity" = 0 THEN 'Zero'
                ELSE 'Missing'
            END AS quantity_sign,
            COUNT(*) AS row_count,
            ROUND(SUM("Quantity" * "Price"), 2) AS signed_value
        FROM combined
        WHERE "Price" > 0
        GROUP BY 1, 2
        ORDER BY 1, 2
    """).fetchdf()

    print("\nINVOICE TYPE VS QUANTITY SIGN — POSITIVE PRICES")
    print(cancellation_check.to_string(index=False))

    # checking the only cancellation with a positive value
    cancellation_exception = connection.execute("""
        SELECT *,
               ROUND("Quantity" * "Price", 2) AS line_value
        FROM combined
        WHERE UPPER(TRIM("Invoice")) LIKE 'C%'
          AND "Quantity" > 0
          AND "Price" > 0
    """).fetchdf()

    print("\nPOSITIVE CANCELLATION EXCEPTION")
    print(cancellation_exception.to_string(index=False))

    # checking for repeated rows in dataset
    duplicate_summary = connection.execute("""
        WITH repeated AS (
            SELECT
                "Invoice", "StockCode", "Description",
                "Quantity", "InvoiceDate", "Price",
                "Customer ID", "Country",
                COUNT(*) AS occurrences
            FROM combined
            GROUP BY
                "Invoice", "StockCode", "Description",
                "Quantity", "InvoiceDate", "Price",
                "Customer ID", "Country"
            HAVING COUNT(*) > 1
        )
        SELECT
            COUNT(*) AS repeated_groups,
            COALESCE(SUM(occurrences - 1), 0) AS extra_copies,
            ROUND(COALESCE(SUM(
                (occurrences - 1) * "Quantity" * "Price"
            ), 0), 2) AS extra_copies_signed_value
        FROM repeated
    """).fetchdf()

    print("\nIDENTICAL-ROW SUMMARY")
    print(duplicate_summary.T.to_string(header=False))

    # completeness check for the 6 essential columns in dataset
    missing_fields = connection.execute("""
        SELECT
            COUNT(*) FILTER (
                WHERE NULLIF(TRIM("Invoice"), '') IS NULL
            ) AS missing_invoice,
            COUNT(*) FILTER (
                WHERE NULLIF(TRIM("StockCode"), '') IS NULL
            ) AS missing_stock_code,
            COUNT(*) FILTER (
                WHERE "InvoiceDate" IS NULL
            ) AS missing_date,
            COUNT(*) FILTER (
                WHERE "Quantity" IS NULL
            ) AS missing_quantity,
            COUNT(*) FILTER (
                WHERE "Price" IS NULL
            ) AS missing_price,
            COUNT(*) FILTER (
                WHERE NULLIF(TRIM("Country"), '') IS NULL
            ) AS missing_country
        FROM combined
    """).fetchdf()

    print("\nMISSING ESSENTIAL FIELDS")
    print(missing_fields.T.to_string(header=False))