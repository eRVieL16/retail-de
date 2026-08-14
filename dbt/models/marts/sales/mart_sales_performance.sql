-- models/marts/sales/mart_sales_performance.sql

select
    store_id,
    store_name,
    region,
    store_type,
    summary_date,
    transaction_count,
    total_units_sold,
    total_revenue,
    round(total_revenue / nullif(transaction_count, 0), 2) as avg_revenue_per_transaction
from {{ ref('int_store_daily_summary') }}