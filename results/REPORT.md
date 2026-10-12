# TP5 — ETL result

The flow ran dlt extraction/loading before dbt transformation on PostgreSQL.
The teacher's CSV contains 13 transaction records. This database view currently
contains **13** rows. Rates came from the real Frankfurter
API, base USD, dated **2026-10-12**; the saved JSON records the exact rates.
Latest business-day rates may precede the execution date.

`raw.currency_rates` is replaced every run; `raw.daily_transactions` is appended
every run, as the assignment specifies. Replaying the same CSV adds the same
transactions again; scheduling this unchanged historical file is not an
idempotent production design. No unrequested merge/deduplication is introduced.
dbt builds `public.final_transaction_usd` as a **view** over those tables.
An API rate is foreign-currency units per one USD, so amount_usd = amount / rate.
USD amounts stay unchanged. Unknown currencies yield NULL rather than a fake rate.
This uses the latest rates for all transactions, including the historical 2025
records; it does not claim these are historical transaction-date conversions.

`python currency_flow.py` executes once. `python currency_flow.py --serve`
serves the required daily 01:00 schedule in Africa/Lagos; the process and
configured Prefect server must stay running for scheduled jobs to execute.
The local verification executed once; it did not leave a daily service running.
PostgreSQL credentials are supplied privately through DATABASE_URL, not committed.
The notebook also needs reachable PostgreSQL; in Colab, localhost refers to Colab.

Assignment: https://github.com/ahmed3991/DataVisualisation-TP2025/blob/main/TP5/TP5.md
API: https://api.frankfurter.dev/v1/latest?base=USD&to=EUR,GBP,JPY
Transactions: https://drive.google.com/uc?export=download&id=1oY9CIYmtY0nL78bVp3lxvCWVDKMuhFv7
