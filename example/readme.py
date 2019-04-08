# Imports.

from pymongo import MongoClient

from marrow.mongo import Index
from marrow.mongo.field import Array, Number, ObjectId, String
from marrow.mongo.trait import Queryable


# Connect to the test database on the local machine.

db = MongoClient().test


# Define an Account object model and associated metadata.

class Account(Queryable):
	__collection__ = 'collection'
	
	username = String(required=True)
	name = String()
	locale = String(default='en-CA-u-tz-cator-cu-CAD', assign=True)
	age = Number()
	
	tag = Array(String(), assign=True)
	
	_username = Index('username', unique=True)


# Bind it to a database, then (re-)create the collection including indexes.

collection = Account.bind(db).create_collection(drop=True)


# Create a new record; this record is unsaved...

alice = Account('amcgregor', "Alice Bevan-McGregor", age=27)

print(alice.id)  # It already has an ID, however!
print(alice.id.generation_time)  # This includes the creation time.


# Inserting it will add it to the storage back-end; the MongoDB database.

result = alice.insert_one()

assert result.acknowledged and result.inserted_id == alice


# Now you can query Account objects for one with an appropriate username.

record = Account.find_one(username='amcgregor')

print(record.name)  # Alice Bevan-McGregor; it's already an Account instance.
