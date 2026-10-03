SELECT
    CAST(calendar_date AS DATE) AS date_key,
    EXTRACT(YEAR FROM calendar_date)::INTEGER AS year,
    EXTRACT(QUARTER FROM calendar_date)::INTEGER AS quarter_number,
    EXTRACT(MONTH FROM calendar_date)::INTEGER AS month_number,
    STRFTIME(calendar_date, '%B') AS month_name,
    STRFTIME(calendar_date, '%Y-%m') AS year_month,
    CAST(DATE_TRUNC('month', calendar_date) AS DATE) AS month_start
FROM GENERATE_SERIES(
    DATE '2009-01-01',
    DATE '2011-12-31',
    INTERVAL '1 day'
) AS calendar(calendar_date)