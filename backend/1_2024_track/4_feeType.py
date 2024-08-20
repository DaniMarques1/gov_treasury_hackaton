import requests
import json
from pymongo import MongoClient

# This script will analyze all data from the transactions to define the fee type
# It can become slow dealing with a dataset that is too large

client = MongoClient('mongodb://localhost:27017/')
db = client['treasury']
collection = db['recent_data']
api_key = 'YOUR_API_KEY'

def determine_fee_type(doc):
    items = doc.get('items', [])
    for item in items:
        contract_address = item.get('contractAddress', '').lower()
        to_address = item.get('to', '').lower()
        from_address = item.get('from', '').lower()

        if from_address == "0xfff9ce5f71ca6178d3beecedb61e7eff1602950e" and to_address == "0x245db945c485b68fdc429e4f7085a1761aa4d45d":
            return "marketplace"

        elif contract_address == "0xa8754b9fa15fc18bb59458815510e40a12cd2014" and to_address == "0x0000000000000000000000000000000000000000":
            return "breeding"

        elif len(items) == 1 and contract_address == "0x97a9107c1793bc407d6f527b77e7fff4d812bece" and to_address == "0x245db945c485b68fdc429e4f7085a1761aa4d45d":
            return "ascending"

        elif contract_address == "0x12b707c3d2786570cfdc3a998a085b62acdba4b3":
            return "partsEvol"

        elif from_address == "0x36b628e771b0ca12a135e0a7b8e0394f99dce95b":
            return "r&cMint"

    return "unknown"

def update_existing_data(grouped_data, db, collection_name):
    collection = db[collection_name]
    updated_ids = []
    for transaction_hash, items in grouped_data.items():
        fee_type = determine_fee_type({'items': items})

        result = collection.update_many(
            {'transactionHash': transaction_hash},
            {'$set': {'feeType': fee_type}}
        )
        if result.modified_count > 0:
            updated_ids.append(transaction_hash)
    return updated_ids

documents = collection.find({})
transaction_hashes = [doc['transactionHash'] for doc in documents if 'transactionHash' in doc]

print(f"Total transaction hashes collected: {len(transaction_hashes)}")

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-API-KEY': api_key
}

batch_size = 100
total_hashes = len(transaction_hashes)
updated_ids = []

for i in range(0, total_hashes, batch_size):
    batch_hashes = transaction_hashes[i:i + batch_size]

    payload = json.dumps({
        "transaction_hashes": batch_hashes
    })

    url = "https://api-gateway.skymavis.com/skynet/ronin/tokens/transfers/txs"
    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        try:
            response_data = response.json()['result']['items']
            print(f"Response data items count for batch {i // batch_size + 1}: {len(response_data)}")

            grouped_data = {}
            for item in response_data:
                transaction_hash = item['transactionHash']
                if transaction_hash not in grouped_data:
                    grouped_data[transaction_hash] = []
                grouped_data[transaction_hash].append(item)

            batch_updated_ids = update_existing_data(grouped_data, db, 'recent_data')
            updated_ids.extend(batch_updated_ids)
            print(f"Updated {len(batch_updated_ids)} documents in 'recent_data' collection for batch {i // batch_size + 1}.")
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response: {e}")
        except KeyError as e:
            print(f"KeyError: {e}. Ensure response structure matches expected format.")
    else:
        print(f"Failed to fetch data from API for batch {i // batch_size + 1}. Status code: {response.status_code}")

client.close()
print(f"Total documents updated in 'test2' collection: {len(updated_ids)}")
