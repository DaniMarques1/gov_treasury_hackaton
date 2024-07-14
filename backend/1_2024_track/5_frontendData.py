from pymongo import MongoClient
from bson import SON

# This script will merge all WETH and AXS transactions from the 2024 collection data into daily sums

client = MongoClient("mongodb://localhost:27017/")
db = client["treasury"]
new_treasury = db['recent_data']
frontend_data = db["frontend_data"]

wallet = "0x245db945c485b68fdc429e4f7085a1761aa4d45d"
tokens = ["WETH", "AXS"]
fee_types = ["marketplace", "breeding", "ascending", "partsEvol", "r&cMint"]

def create_pipeline(token, fee_type):
    return [
        {
            "$match": {
                "tokenSymbol": token,
                "to": wallet,
                "feeType": fee_type
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
                f"{token.lower()}_{fee_type}": "$daily_sum"
            }
        },
        {
            "$sort": SON([("timestamp", 1)])
        }
    ]

final_results = {}

for token in tokens:
    for fee_type in fee_types:
        pipeline = create_pipeline(token, fee_type)
        result = new_treasury.aggregate(pipeline)

        for doc in result:
            timestamp = doc["timestamp"]
            if timestamp not in final_results:
                final_results[timestamp] = {"timestamp": timestamp}
            final_results[timestamp][f"{token.lower()}_{fee_type}"] = doc[f"{token.lower()}_{fee_type}"]

for doc in final_results.values():
    timestamp = doc["timestamp"]
    update_fields = {k: v for k, v in doc.items() if k != "timestamp"}
    frontend_data.update_one(
        {"timestamp": timestamp},
        {"$set": update_fields},
        upsert=True
    )

print("Aggregation and insertion completed.")
