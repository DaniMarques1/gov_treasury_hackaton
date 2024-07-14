from pymongo import MongoClient

# This script will attribute human-readable values to the documents

client = MongoClient('mongodb://localhost:27017/')

db = client['treasury']
new_collection = db['new_treasury']

n = 0
for document in new_collection.find():
    value = document.get('value')
    n += 1
    print(f'New Treasury Document {n}')

    std_value = float(value) / (10 ** 18)

    new_collection.update_one(
        {'_id': document['_id']},
        {'$set': {'std_value': std_value}}
    )

print("New Treasury Standard Values Updated.")

old_collection = db['old_treasury']

m = 0
for document in old_collection.find():
    value = document.get('value')
    m += 1
    print(f'Old Treasury Document {m}')

    std_value = float(value) / (10 ** 18)

    old_collection.update_one(
        {'_id': document['_id']},
        {'$set': {'std_value': std_value}}
    )

print("Old Treasury Standard Values Updated.")
