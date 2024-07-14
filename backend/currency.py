import requests
from pymongo import MongoClient
from datetime import datetime, timezone

# Script to take the most recent conversion from WETH nad AXS to USD

def get_current_prices():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=axie-infinity,ethereum&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        axs_price = data['axie-infinity']['usd']
        weth_price = data['ethereum']['usd']
        return axs_price, weth_price
    else:
        return None, None

def store_prices_in_db(axs_price, weth_price):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['treasury']
    collection = db['currency']

    document = {
        "timestamp": datetime.now(timezone.utc),
        "axs_price": axs_price,
        "weth_price": weth_price
    }

    collection.insert_one(document)
    client.close()

axs_price, weth_price = get_current_prices()
if axs_price is not None and weth_price is not None:
    store_prices_in_db(axs_price, weth_price)
    print("Prices stored in database successfully.")
else:
    print("Failed to fetch prices.")
