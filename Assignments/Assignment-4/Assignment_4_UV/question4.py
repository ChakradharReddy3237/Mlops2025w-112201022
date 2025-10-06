import os
import pandas as pd
from pymongo import MongoClient


def main() -> None:
    # MongoDB Connection (Atlas or local fallback)
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("MONGODB_URI not set. Using local MongoDB at localhost:27017")
        uri = "mongodb://localhost:27017/"
    
    target = "Atlas" if uri.startswith("mongodb+srv://") else "local"
    
    try:
        client = MongoClient(uri)
        # Test connection
        client.admin.command('ping')
        print(f"Connected to MongoDB ({target})")
    except Exception as e:
        if target == "Atlas":
            print(f"Atlas connection failed ({e}). Falling back to local MongoDB...")
            uri = "mongodb://localhost:27017/"
            target = "local"
            try:
                client = MongoClient(uri)
                client.admin.command('ping')
                print(f"Connected to MongoDB ({target})")
            except Exception as local_e:
                raise RuntimeError(f"Both Atlas and local MongoDB failed: {local_e}")
        else:
            raise RuntimeError(f"MongoDB connection failed: {e}")

    db = client["retail_db"]
    cust_col = db["customer_centric"]

    # Drop existing collection (start fresh)
    cust_col.drop()

    # Load CSV (first 1000 rows)
    df = pd.read_csv("data/online_retail.csv")
    df = df.dropna(subset=["CustomerID"])  # keep valid customers only
    df = df.iloc[:1000]

    # Build Customer-Centric Docs
    cust_docs = []
    grouped = df.groupby(["CustomerID", "Country"])

    for (customer, country), group in grouped:
        invoices = []
        total_spent = 0.0
        for (inv_no, inv_date), g in group.groupby(["InvoiceNo", "InvoiceDate"]):
            items = g[["StockCode", "Description", "Quantity", "UnitPrice"]].to_dict("records")
            total = (g["Quantity"] * g["UnitPrice"]).sum()
            total_spent += total
            invoices.append(
                {
                    "invoice_no": str(inv_no),
                    "invoice_date": pd.to_datetime(inv_date).isoformat() if not pd.isna(inv_date) else None,
                    "total_amount": round(float(total), 2),
                    "items": items,
                }
            )
        cust_docs.append(
            {
                "customer_id": str(int(customer)),
                "country": country,
                "total_spent": round(float(total_spent), 2),
                "invoices": invoices,
            }
        )

    # Insert into Atlas in small chunks
    if cust_docs:
        batch = 500
        inserted = 0
        for i in range(0, len(cust_docs), batch):
            chunk = cust_docs[i : i + batch]
            cust_col.insert_many(chunk)
            inserted += len(chunk)
        print(f"Inserted {inserted} customer-centric documents into MongoDB ({target}).")
    else:
        print("No documents to insert.")


if __name__ == "__main__":
    main()
