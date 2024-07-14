from pymongo import MongoClient

# Script made to erase AM (Axie Material) transactions from the db. Can cause trouble in the fee type definition algo.
client = MongoClient('mongodb://localhost:27017/')

db = client['treasury']
collection = db['recent_data']

query = {
    "feeType": "partsEvol",
    "tokenSymbol": "AM"
}

result = collection.delete_many(query)

print(f"Documents deleted: {result.deleted_count}")
