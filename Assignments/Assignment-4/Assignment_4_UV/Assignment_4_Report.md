# Assignment 4 Report (uv solution)

Author: Chakradhar Reddy
Date: 2025-10-02

## Objectives
- Acquire and prepare the UCI Online Retail dataset for analysis.
- Load a normalized subset into SQLite with basic constraints and indexes.
- Model the same data in MongoDB using two designs and compare typical CRUD patterns.
- Publish customer-centric data to MongoDB Atlas.

## Data Preparation
- `get_data.sh` downloads the Excel file and converts it to CSV via `convert_data.py` (openpyxl backend).
- The CSV is stored under `data/online_retail.csv`.

## Q1 — SQLite (Relational)
Design decisions:
- Tables: `Product(StockCode PK, Description, UnitPrice)` and `Invoice(InvoiceNo, StockCode, Quantity, InvoiceDate, CustomerID, Country)`.
- Constraints: non-negative `UnitPrice`; `Invoice` has `UNIQUE(InvoiceNo, StockCode)` to avoid duplicates.
- Indexes: on `Invoice.StockCode` and `Invoice.CustomerID` to speed lookups.
Process:
1) Initialize schema using `question1.sql` (via `get_data.sh`).
2) `question1.py` reads `data/online_retail.csv` and inserts de-duplicated products and invoices with `executemany` for efficiency. Row count can be limited via `Q1_ROW_LIMIT`.

## Q2 — MongoDB (Local, Two Designs)
Collections and structure:
- Transaction-centric (`transaction_centric`): one document per invoice with flattened item list and `total_amount`.
- Customer-centric (`customer_centric`): one document per customer with an array of invoices and `total_spent`.
Notes:
- Local URI defaults to `mongodb://localhost:27017/` and can be overridden via `MONGODB_URI_LOCAL`.
- Helpful indexes are created on `invoice_no` and `customer_id`.

## Q3 — CRUD Benchmark
Approach:
- Rebuild both collections from a 1k-row slice for predictable runtimes.
- Measure average latencies for create/read/update/delete operations using multiple runs.
Outputs:
- Console table with averaged timings per operation and model.
- `crud_benchmark.png` comparing models visually.
- `crud_benchmark_results.csv` with numeric values for quick inclusion in reports.
Interpretation (typical):
- Direct customer lookups are faster on the customer-centric design.
- Invoice-level retrieval tends to favor the transaction-centric design.
- Aggregations are comparable if totals are materialized.

## Q4 — MongoDB Atlas
- `question4.py` uploads customer-centric documents using `MONGODB_URI`. Inserts are chunked for robustness on larger sets.
- `test_question4.py` validates by printing document counts, a sample (without `_id`), first two Indian customers, and a small set of distinct countries.

## Reproducibility and Troubleshooting
- uv manages the Python version and packages via `pyproject.toml`.
- Optional checks: `ruff`, `mypy`.
- If matplotlib cannot open a window, set `MPLBACKEND=Agg` (the plot will still be saved).
- Ensure MongoDB is running locally for Q2/Q3 or adjust URIs; set `MONGODB_URI` for Atlas in Q4.

## How to Run
1. `uv python install 3.10 && uv sync`
2. `bash get_data.sh`
3. Run per question as shown in README.
4. Export the report via `export_report.sh`.
