import os
import json
from pymongo import MongoClient

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')
db = client['treasury']

# List of collections to export
collections = ['frontend_data', 'currency', 'balance']

# Base output directory
output_base_path = 'streamlit/pages'

# Ensure the base directory exists
os.makedirs(output_base_path, exist_ok=True)

for collection_name in collections:
    # Fetch all documents from the collection
    collection = db[collection_name]
    data = list(collection.find())

    # Specify the path and filename
    output_path = os.path.join(output_base_path, f'{collection_name}.json')

    # Write the data to a JSON file
    with open(output_path, 'w') as file:
        json.dump(data, file, default=str, indent=4)

    print(f'Data exported to {output_path}')
