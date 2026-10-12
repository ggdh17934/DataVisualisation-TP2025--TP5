"""Run the required ETL once, inspect its real PostgreSQL output and save it."""
# %% 1. Imports and PostgreSQL connection
import json
import os
from pathlib import Path
from getpass import getpass

import pandas as pd
import psycopg2

ROOT = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = getpass("PostgreSQL connection URL (hidden): ")
from currency_flow import currency_exchange_rate_etl

# %% 2. Extract and load with dlt, then transform with dbt inside Prefect
currency_exchange_rate_etl()

# %% 3. Query the resulting USD view, without printing connection credentials
with psycopg2.connect(os.environ["DATABASE_URL"]) as connection:
    with connection.cursor() as cursor:
        cursor.execute("select * from public.final_transaction_usd order by transaction_id")
        final_transactions = pd.DataFrame(cursor.fetchall(), columns=[c.name for c in cursor.description])
print(final_transactions.to_string(index=False))
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
final_transactions.to_csv(OUT / "final_transaction_usd.csv", index=False)
rates = json.loads((OUT / "exchange_rates.json").read_text(encoding="utf-8"))
print("API rate date:", rates["date"], "Base:", rates["base"], "Rates:", rates["rates"])

# %% 4. Explain the required pipeline and its conversion direction
report = f"""# TP5 — ETL result

The flow ran dlt extraction/loading before dbt transformation on PostgreSQL.
The teacher's CSV contains 13 transaction records. This database view currently
contains **{len(final_transactions)}** rows. Rates came from the real Frankfurter
API, base USD, dated **{rates['date']}**; the saved JSON records the exact rates.
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
"""
(OUT / "REPORT.md").write_text(report, encoding="utf-8")
print("Saved the USD results and pipeline explanation.")
