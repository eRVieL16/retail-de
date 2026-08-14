-- models/intermediate/int_store_daily_summary.sql

with transactions as (
    select * from {{ source('silver', 'stg_transactions') }}
),

products as (
    select * from {{ source('silver', 'stg_products') }}
),

stores as (
    select * from {{ source('silver', 'stg_stores') }}
),

inventory as (
    select * from {{ source('silver', 'stg_inventory') }}
),

daily_sales as (
    select
        t.store_id,
        cast(t.transaction_date as date) as summary_date,
        count(distinct t.transaction_id) as transaction_count,
        sum(t.quantity) as total_units_sold,
        sum(t.total_amount) as total_revenue
    from transactions t
    inner join products p on t.product_id = p.product_id
    group by t.store_id, cast(t.transaction_date as date)
),

daily_inventory as (
    select
        i.store_id,
        i.snapshot_date as summary_date,
        sum(i.stock_qty) as total_stock_qty,
        sum(case when i.stock_qty <= i.reorder_point then 1 else 0 end) as low_stock_product_count,
        sum(case when i.is_backorder_anomaly then 1 else 0 end) as backorder_anomaly_count
    from inventory i
    inner join products p on i.product_id = p.product_id
    group by i.store_id, i.snapshot_date
)

select
    coalesce(ds.store_id, di.store_id) as store_id,
    s.store_name,
    s.region,
    s.store_type,
    coalesce(ds.summary_date, di.summary_date) as summary_date,
    coalesce(ds.transaction_count, 0) as transaction_count,
    coalesce(ds.total_units_sold, 0) as total_units_sold,
    coalesce(ds.total_revenue, 0) as total_revenue,
    coalesce(di.total_stock_qty, 0) as total_stock_qty,
    coalesce(di.low_stock_product_count, 0) as low_stock_product_count,
    coalesce(di.backorder_anomaly_count, 0) as backorder_anomaly_count
from daily_sales ds
full outer join daily_inventory di
    on ds.store_id = di.store_id
    and ds.summary_date = di.summary_date
left join stores s
    on coalesce(ds.store_id, di.store_id) = s.store_id