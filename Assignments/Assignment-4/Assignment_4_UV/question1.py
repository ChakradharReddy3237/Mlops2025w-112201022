import os
import sqlite3
import pandas as pd
from pathlib import Path


def connect_db(db_file: str = "question1.db") -> sqlite3.Connection:
    return sqlite3.connect(db_file)


def insert_from_dataframe(conn: sqlite3.Connection, df: pd.DataFrame) -> None:
    products = df[["StockCode", "Description", "UnitPrice"]].drop_duplicates()
    invoices = df[["InvoiceNo", "StockCode", "Quantity", "InvoiceDate", "CustomerID", "Country"]]
    # Aggregate potential duplicates per (InvoiceNo, StockCode) to satisfy UNIQUE constraint
    invoices = (
        invoices
        .groupby(["InvoiceNo", "StockCode"], as_index=False)
        .agg({
            "Quantity": "sum",
            "InvoiceDate": "first",
            "CustomerID": "first",
            "Country": "first",
        })
    )

    cur = conn.cursor()

    cur.executemany(
        """
        INSERT OR IGNORE INTO Product (StockCode, Description, UnitPrice)
        VALUES (?, ?, ?)
        """,
        products[["StockCode", "Description", "UnitPrice"]].itertuples(index=False, name=None),
    )

    cur.executemany(
        """
        INSERT INTO Invoice (InvoiceNo, StockCode, Quantity, InvoiceDate, CustomerID, Country)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        invoices[["InvoiceNo", "StockCode", "Quantity", "InvoiceDate", "CustomerID", "Country"]].itertuples(index=False, name=None),
    )

    conn.commit()
    print("Data inserted successfully!")


def main() -> None:
    # Ensure DB schema exists (load from SQL file if present)
    conn = connect_db()
    sql_path = Path("question1.sql")
    if sql_path.exists():
        with open(sql_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

    # Ensure CSV exists with a clear message
    csv_path = Path("data/online_retail.csv")
    if not csv_path.exists():
        raise FileNotFoundError(
            "data/online_retail.csv not found. Run 'bash get_data.sh' to download and convert the dataset."
        )

    df = pd.read_csv(csv_path)
    # Optional limit via env var to keep simple and configurable
    limit = os.getenv("Q1_ROW_LIMIT")
    if limit and limit.isdigit():
        df = df.iloc[: int(limit)]
    insert_from_dataframe(conn, df)
    conn.close()


if __name__ == "__main__":
    main()
