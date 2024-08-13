from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["treasury"]

recent_data_collection = db["recent_data"]
new_txn_collection = db["new_txn"]

# Copy documents from "recent_data" to "new_txn"
documents = list(recent_data_collection.find({}))
if documents:
    new_txn_collection.insert_many(documents)

# Delete all documents from "recent_data"
recent_data_collection.delete_many({})

print("Documents copied and erased successfully.")

client.close()
