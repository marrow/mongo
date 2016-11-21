# encoding: utf-8

from pymongo import MongoClient
from marrow.mongo import Document, Index
from marrow.mongo.field import ObjectId, String, Number, Array


collection = MongoClient().test.collection
collection.drop()


class Account(Document):
	username = String(required=True)
	name = String()
	locale = String(default='en-CA-u-tz-cator-cu-CAD', assign=True)
	age = Number()
	
	id = ObjectId('_id', assign=True)
	tag = Array(String(), default=lambda: [], assign=True)
	
	_username = Index('username', unique=True)


alice = Account('amcgregor', "Alice Bevan-McGregor", age=27)
print(alice.id)  # Already has an ID.
print(alice.id.generation_time)  # This even includes the creation time.

Account._username.create_index(collection)

result = collection.insert_one(alice)
assert result.acknowledged and result.inserted_id == alice.id

record = collection.find_one(Account.username == 'amcgregor')
record = Account.from_mongo(record)
print(record.name)  # Alice Bevan-McGregor
