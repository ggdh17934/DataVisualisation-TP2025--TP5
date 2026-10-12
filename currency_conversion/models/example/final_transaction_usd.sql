with latest_rates as (
    select date as rate_date, rates__eur as eur_rate,
           rates__gbp as gbp_rate, rates__jpy as jpy_rate
    from {{ source('raw_data_dlt', 'currency_rates') }}
    order by date desc
    limit 1
)
select t.transaction_id, t.customer_id, t.transaction_date,
       t.currency, t.amount as original_amount, r.rate_date,
       case t.currency
           when 'USD' then t.amount
           when 'EUR' then t.amount / r.eur_rate
           when 'GBP' then t.amount / r.gbp_rate
           when 'JPY' then t.amount / r.jpy_rate
           else null
       end as amount_usd
from {{ source('raw_data_dlt', 'daily_transactions') }} as t
cross join latest_rates as r
where t.amount is not null
