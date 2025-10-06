import os
import pandas as pd
from pymongo import MongoClient


def main() -> None:
    # Load Data
    df = pd.read_csv("data/online_retail.csv")
    df = df.dropna(subset=["CustomerID"])  # drop rows without customer id

    # MongoDB Connection (local, overridable)
    mongo_uri = os.getenv("MONGODB_URI_LOCAL", "mongodb://localhost:27017/")
    client = MongoClient(mongo_uri)
    db = client["retail_db"]

    # Collections
    transactions = db["transaction_centric"]
    customers = db["customer_centric"]

    # Transaction-centric Data
    grouped_txn = df.groupby(["InvoiceNo", "CustomerID", "InvoiceDate", "Country"])

    txn_docs = []
    for (invoice, customer, date, country), group in grouped_txn:
        items = group[["StockCode", "Description", "Quantity", "UnitPrice"]].to_dict("records")
        total = (group["Quantity"] * group["UnitPrice"]).sum()
        doc = {
            "invoice_no": str(invoice),
            "customer_id": str(int(customer)),
            "invoice_date": pd.to_datetime(date).isoformat(),
            "country": country,
            "total_amount": float(total),
            "items": items,
        }
        txn_docs.append(doc)

    if txn_docs:
        transactions.insert_many(txn_docs)
        print(f"Inserted {len(txn_docs)} transaction documents")

    # Customer-centric Data
    grouped_cust = df.groupby(["CustomerID", "Country"])

    cust_docs = []
    for (customer, country), group in grouped_cust:
        invoices = []
        total_spent = 0.0
        for (inv_no, inv_date), inv_group in group.groupby(["InvoiceNo", "InvoiceDate"]):
            items = inv_group[["StockCode", "Description", "Quantity", "UnitPrice"]].to_dict("records")
            total = (inv_group["Quantity"] * inv_group["UnitPrice"]).sum()
            total_spent += total
            invoices.append(
                {
                    "invoice_no": str(inv_no),
                    "invoice_date": pd.to_datetime(inv_date).isoformat(),
                    "total_amount": float(total),
                    "items": items,
                }
            )

        doc = {
            "customer_id": str(int(customer)),
            "country": country,
            "total_spent": float(total_spent),
            "invoices": invoices,
        }
        cust_docs.append(doc)

    if cust_docs:
        customers.insert_many(cust_docs)
        print(f"Inserted {len(cust_docs)} customer documents")

    # Helpful indexes
    transactions.create_index("invoice_no")
    transactions.create_index("customer_id")
    customers.create_index("customer_id")


if __name__ == "__main__":
    main()
