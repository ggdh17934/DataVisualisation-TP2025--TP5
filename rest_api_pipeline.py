"""Extract the teacher's sources and load PostgreSQL with dlt."""
import json
import os
from pathlib import Path
from urllib.parse import urlparse, unquote, parse_qs

import dlt
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent
RATE_URL = "https://api.frankfurter.dev/v1/latest?base=USD&to=EUR,GBP,JPY"
TRANSACTIONS_URL = "https://drive.google.com/uc?export=download&id=1oY9CIYmtY0nL78bVp3lxvCWVDKMuhFv7"

def configure_connection():
    """One connection URL supplies both dlt and dbt; never print credentials."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("Set DATABASE_URL to your PostgreSQL connection URL first (see README).")
    parsed = urlparse(url)
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise ValueError("DATABASE_URL must be a PostgreSQL URL.")
    values = {"PGHOST": parsed.hostname or "localhost", "PGPORT": str(parsed.port or 5432),
              "PGUSER": unquote(parsed.username or ""), "PGPASSWORD": unquote(parsed.password or ""),
              "PGDATABASE": unquote(parsed.path.lstrip("/")),
              "PGSSLMODE": parse_qs(parsed.query).get("sslmode", ["prefer"])[0]}
    os.environ.update(values)
    return url

def get_currency_rates():
    response = requests.get(RATE_URL, timeout=60)
    response.raise_for_status()
    rates = response.json()
    if rates["base"] != "USD" or rates["amount"] != 1 or any(rates["rates"][c] <= 0 for c in ["EUR", "GBP", "JPY"]):
        raise ValueError("Expected positive EUR/GBP/JPY rates for one USD.")
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "exchange_rates.json").write_text(json.dumps(rates, indent=2), encoding="utf-8")
    yield rates

def get_transaction_logs():
    cached = ROOT / "data" / "transactions.csv"
    return pd.read_csv(cached if cached.exists() else TRANSACTIONS_URL)

def load_pipeline():
    url = configure_connection()
    pipeline = dlt.pipeline(pipeline_name="currency_conversion", destination="postgres",
                           dataset_name="raw", pipelines_dir=str(ROOT / ".dlt-state"))
    # A nested rates dictionary becomes rates__eur, rates__gbp and rates__jpy.
    pipeline.run(get_currency_rates(), table_name="currency_rates",
                 write_disposition="replace", credentials=url)
    transactions = get_transaction_logs()
    pipeline.run(transactions, table_name="daily_transactions",
                 write_disposition="append", credentials=url)
    print(f"Loaded latest USD exchange rates and appended {len(transactions)} transactions to raw.")

if __name__ == "__main__":
    load_pipeline()
