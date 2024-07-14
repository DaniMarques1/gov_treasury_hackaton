import requests
import json
from pymongo import MongoClient
from datetime import datetime, timezone

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['treasury']
collection = db['balance']
api_key = 'YOUR_API_KEY'

# API request
url = "https://api-gateway.skymavis.com/skynet/ronin/tokens/balances/summary"

payload = json.dumps({
    "includes": [
        "RON"
    ],
    "ownerAddress": "0x245db945c485b68fdc429e4f7085a1761aa4d45d",
    "tokenStandards": [
        "ERC20",
        "ERC721",
        "ERC1155"
    ]
})
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-API-KEY': api_key
}

response = requests.request("POST", url, headers=headers, data=payload)

if response.status_code == 200:
    response_data = response.json()

    # Process balances to add "std_value" and timestamp fields
    if 'result' in response_data and 'items' in response_data['result']:
        for item in response_data['result']['items']:
            if 'balance' in item and 'decimals' in item:
                item['std_value'] = float(item['balance']) / (10 ** item['decimals'])

    # Add timestamp field
    response_data['timestamp'] = datetime.now(timezone.utc)

    # Insert processed response data into MongoDB
    collection.insert_one(response_data)
    print("Data inserted into MongoDB successfully.")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}, Response: {response.text}")
