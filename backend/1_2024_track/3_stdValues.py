from pymongo import MongoClient

# This script will attribute human-readable values to the documents.

client = MongoClient('mongodb://localhost:27017/')

db = client['treasury']
collection = db['recent_data']

n = 0
for document in collection.find():
    value = document.get('value')
    n += 1
    print(n)

    std_value = float(value) / (10 ** 18)

    collection.update_one(
        {'_id': document['_id']},
        {'$set': {'std_value': std_value}}
    )

print("Conversion complete. Documents updated.")
