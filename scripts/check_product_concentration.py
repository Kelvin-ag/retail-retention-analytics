from pathlib import Path
import duckdb

database = (
    Path(__file__).resolve().parents[1]
    / "data" / "retail.duckdb"
)

with duckdb.connect(str(database), read_only=True) as connection:
    result = connection.execute("""
        WITH product_sales AS (
            SELECT
                product_key,
                SUM(net_product_revenue) AS sales
            FROM analytics.fct_order_lines
            WHERE is_paid_product_sale
              AND date_key >= DATE '2011-01-01'
              AND date_key < DATE '2011-12-01'
            GROUP BY product_key
        ),
        ranked AS (
            SELECT
                product_key,
                sales,
                ROW_NUMBER() OVER (
                    ORDER BY sales DESC, product_key
                ) AS product_rank,
                SUM(sales) OVER () AS total_sales,
                SUM(sales) OVER (
                    ORDER BY sales DESC, product_key
                    ROWS BETWEEN UNBOUNDED PRECEDING
                             AND CURRENT ROW
                ) AS cumulative_sales
            FROM product_sales
        )
        SELECT
            COUNT(*) AS products_with_sales,
            ROUND(MAX(total_sales), 2) AS product_sales_value,
            ROUND(
                100.0 * MAX(sales) / MAX(total_sales), 2
            ) AS largest_product_sales_pct,
            ROUND(
                100.0 * SUM(sales) FILTER (
                    WHERE product_rank <= 10
                ) / MAX(total_sales), 2
            ) AS top_10_sales_pct,
            MIN(product_rank) FILTER (
                WHERE cumulative_sales >= 0.8 * total_sales
            ) AS products_for_80_pct
        FROM ranked
    """).fetchdf()

print("PRODUCT CONCENTRATION — JANUARY–NOVEMBER 2011")
print(result.to_string(index=False))