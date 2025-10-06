import os
import pprint
from pymongo import MongoClient


def main() -> None:
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

    count = cust_col.count_documents({})
    print(f"Total customer-centric documents in cluster: {count}")

    print("\nSample document:")
    doc = cust_col.find_one({}, {"_id": 0})
    pprint.pprint(doc)

    print("\nFirst 2 customers from India:")
    for d in cust_col.find({"country": "India"}, {"_id": 0}).limit(2):
        pprint.pprint(d)

    # Distinct countries as a quick sanity check
    countries = sorted(cust_col.distinct("country"))[:10]
    print("\nDistinct countries (up to 10):", countries)


if __name__ == "__main__":
    main()
