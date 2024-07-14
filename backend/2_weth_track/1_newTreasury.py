import requests
import json
from pymongo import MongoClient

# This script will retrieve data from the new treasury
# It takes a long time to retrieve all data

client = MongoClient('mongodb://localhost:27017/')
db = client['treasury']
collection = db['new_treasury']
api_key = 'YOUR_API_KEY' # You need to ask SM an auth for your key to use this endpoint

url = "https://api-gateway.skymavis.com/skynet-tx-query/ronin/tokens/transfers/search"

addresses = [
    "0x245db945c485b68fdc429e4f7085a1761aa4d45d"
]

start_block = 17934197 #This is the block from the first transaction sent to the new trasury
end_block = 30746337 #This is the last block before 1st january 2024
block_step = 200

total_requests = 0
total_time = 0

for address in addresses:
    current_start_block = start_block

    while current_start_block <= end_block:
        current_end_block = min(current_start_block + block_step - 1, end_block)
        print(f"Retrieving blocks {current_start_block} to {current_end_block} for address {address}...")

        offset = 0
        while True:
            payload = json.dumps({
                "address": {
                    "relateTo": address,
                },
                "block": {
                    "blockRange": [
                        current_start_block,
                        current_end_block
                    ]
                },
                "paging": {
                    "limit": 200,
                    "offset": offset,
                    "pagingStyle": "offset"
                },
            })

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-API-KEY': api_key
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            total_requests += 1
            response_json = response.json()

            if 'result' in response_json and 'items' in response_json['result']:
                items = response_json['result']['items']
                if items:
                    collection.insert_many(items)
                    print(f"{len(items)} new documents processed.")
                    if len(items) < 200:
                        break
                else:
                    print("No new documents to process.")
                    break
            else:
                print("Empty response or unexpected format.")
                break

            offset += 200
        current_start_block += block_step

print(f"All data fetched and stored in MongoDB.")
print(f"Total requests made: {total_requests}")
