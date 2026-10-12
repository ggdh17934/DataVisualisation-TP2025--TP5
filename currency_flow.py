"""The required dlt → dbt Prefect flow, once or scheduled daily."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("PREFECT_HOME", str(ROOT / ".prefect"))
os.environ.setdefault("PREFECT_SERVER_ANALYTICS_ENABLED", "false")
os.environ.setdefault("DLT_TELEMETRY", "false")

from dbt.cli.main import dbtRunner
from prefect import flow, task
from prefect.schedules import Cron
from rest_api_pipeline import configure_connection, load_pipeline

@task
def run_dbt_models():
    project = ROOT / "currency_conversion"
    result = dbtRunner().invoke(["run", "--project-dir", str(project), "--profiles-dir", str(project)])
    if not result.success:
        raise RuntimeError("dbt transformation failed; check the dbt log.") from result.exception

@flow(name="Currency Exchange Rate ETL")
def currency_exchange_rate_etl():
    configure_connection()
    load_pipeline()
    run_dbt_models()

if __name__ == "__main__":
    import sys
    if "--serve" in sys.argv:
        currency_exchange_rate_etl.serve(
            name="daily-data-deployment", schedule=Cron("0 1 * * *", timezone="Africa/Lagos"),
            description="Load exchange rates and transactions, then run dbt daily at 1 AM.",
            tags=["daily-pipeline"],
        )
    else:
        currency_exchange_rate_etl()
