-- models/marts/inventory/mart_inventory_status.sql

select
    store_id,
    store_name,
    region,
    summary_date,
    total_stock_qty,
    low_stock_product_count,
    backorder_anomaly_count,
    case
        when low_stock_product_count > 0 then true
        else false
    end as needs_restock_attention
from {{ ref('int_store_daily_summary') }}