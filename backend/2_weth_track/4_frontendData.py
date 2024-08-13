from pymongo import MongoClient
from bson import SON

client = MongoClient("mongodb://localhost:27017/")
db = client["treasury"]
new_treasury = db['new_treasury']
old_treasury = db['old_treasury']
frontend_data = db["frontend_data"]

wallets = {
    "new_treasury": "0x245db945c485b68fdc429e4f7085a1761aa4d45d",
    "old_treasury": "0xa99cacd1427f493a95b585a5c7989a08c86a616b"
}

def create_pipeline(token, wallet):
    return [
        {
            "$match": {
                "tokenSymbol": token,
                "to": wallet,
                "std_value": {"$lt": 50}
            }
        },
        {
            "$addFields": {
                "blockTimeDate": {
                    "$toDate": {"$multiply": ["$blockTime", 1000]}
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "day": {"$dayOfMonth": "$blockTimeDate"},
                    "month": {"$month": "$blockTimeDate"},
                    "year": {"$year": "$blockTimeDate"},
                },
                "daily_sum": {"$sum": "$std_value"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "timestamp": {
                    "$dateFromParts": {
                        "day": "$_id.day",
                        "month": "$_id.month",
                        "year": "$_id.year",
                    }
                },
                "weth_marketplace": "$daily_sum"
            }
        },
        {
            "$sort": SON([("timestamp", 1)])
        }
    ]

def process_treasury(collection, wallet):
    pipeline = create_pipeline("WETH", wallet)
    result = collection.aggregate(pipeline)

    final_results = {}

    for doc in result:
        timestamp = doc["timestamp"]
        unix_timestamp = int(timestamp.timestamp())  # Convert to Unix timestamp
        if timestamp not in final_results:
            final_results[timestamp] = {
                "timestamp": timestamp,
                "date": unix_timestamp  # Add the new "date" field
            }
        final_results[timestamp]["weth_marketplace"] = doc["weth_marketplace"]

    for doc in final_results.values():
        timestamp = doc["timestamp"]
        update_fields = {
            "weth_marketplace": doc["weth_marketplace"],
            "date": doc["date"]  # Include the new "date" field in the update
        }
        frontend_data.update_one(
            {"timestamp": timestamp},
            {"$set": update_fields},
            upsert=True
        )

process_treasury(new_treasury, wallets["new_treasury"])
process_treasury(old_treasury, wallets["old_treasury"])

print("Aggregation and insertion completed.")
