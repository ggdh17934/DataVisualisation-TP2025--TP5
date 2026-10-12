# DataVisualisation-TP2025 — TP5

Simple solution of the [teacher's TP5](https://github.com/ahmed3991/DataVisualisation-TP2025/blob/main/TP5/TP5.md), covering the required tasks only.

- **TP5.ipynb**: executed notebook, with real outputs and the written answers.
- **tp5.py**: equivalent Python entry point.
- **EXPLICATION_AR.md**: Arabic explanation of each step and the results.
- **data/**: the actual source data used.
- **results/**: generated results and **REPORT.md** with the required answers.

## Run

Download `TP5.ipynb` from this private repository, upload it to [Google Colab](https://colab.research.google.com/), and choose **Runtime → Run all**. The first cell installs missing libraries. Private GitHub links can require authentication; uploading the downloaded notebook avoids that issue.

Alternatively, from this repository folder:

```sh
python -m pip install -r requirements.txt
python tp5.py
```

## PostgreSQL is required

Create an empty PostgreSQL database that your Python runtime can reach. Supply a connection URL when the notebook/script asks (hidden input), or set `DATABASE_URL` before running. URL-encode special characters in the password. Credentials are never included in this repository. Use your own database, user, host and port; the sample values in `.env.example` are placeholders.

In Colab, `localhost` refers to the Colab runtime, not your Windows computer. Use a reachable PostgreSQL server with its required SSL settings. The notebook recreates its companion Python/SQL files, so only uploading the notebook is sufficient **once the database is available**.

`python currency_flow.py` runs once. After setting `DATABASE_URL`, `python currency_flow.py --serve` registers and serves the teacher's daily 01:00 schedule in Africa/Lagos. Keep the serving process and Prefect server available for daily execution; this repository does not automatically run a hosted service.

The real pipeline was tested against an isolated PostgreSQL 17 database with the 13 supplied records and the public Frankfurter API. A fresh database produces 13 rows. Transactions append on every run, so repeated runs of the same historical CSV add duplicates, exactly as in the assignment. Rates replace each run. The dbt result is a view, not an additional physical table. Current exchange rates are used even for historical transactions.
